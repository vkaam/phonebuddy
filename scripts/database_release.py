"""Apply database migrations and API grants as part of the dev release (issue 161).

The release identity is the SQL server's Entra administrator (set by Bicep) and
connects with an Entra token, so there is no SQL password or secret anywhere.
For the run it opens one temporary firewall rule for the runner and always
removes it. It then applies services/api/migrations/*.sql in order, idempotently,
creates the API managed-identity user by SID (no directory lookup), adds it to
the least-privilege role the migrations define, creates a database user for the
owner and seeds the owner's membership only where it is missing.

Migrations only move forward: nothing here, and nothing in recovery, reverses a
migration or restores a database over newer data.
"""

import argparse
import base64
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import types
from urllib.request import urlopen

try:
    from .api_settings import _GUID, _SQL_SERVER
except ImportError:  # executed as a script
    from api_settings import _GUID, _SQL_SERVER

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / 'services/api/migrations'
SCHEMA = ROOT / 'infra/release-schema.json'
DATABASE_RESOURCE = 'https://database.windows.net/'
API_USER = 'id-pb-dev-pull'
API_ROLE = 'pb_api'
OWNER_ROLE = 'db_owner'
ADMIN_ROLE = 'admin'
USER_ROLE = 'user'
FIREWALL_PREFIX = 'pb-release-'
# Roles and permissions the API identity must never hold.
BROAD_ROLES = ('db_owner', 'db_datawriter', 'db_ddladmin', 'db_securityadmin', 'db_accessadmin')
_MIGRATION_NAME = re.compile(r'(\d{3})_[a-z0-9_]+\.sql')
_DESTRUCTIVE = re.compile(
    r'\b(drop|truncate|sp_rename|alter\s+column|then\s+delete'
    r'|delete\s+(?!(on|cascade|set|no)\b)[\w\[#@])', re.IGNORECASE)
_TOKEN = re.compile(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*')
_SECRET_ASSIGNMENT = re.compile(
    r'(password|pwd|secret|token|accesstoken)\s*[=:]\s*\S+', re.IGNORECASE)
_NAME = re.compile(r'[A-Za-z0-9_-]{1,128}')


class DatabaseReleaseError(Exception):
    """A fail-closed release problem; the message is safe to print."""


def scrub(text):
    """Remove anything that looks like a bearer token or credential from output."""
    text = _TOKEN.sub('[token removed]', str(text))
    return _SECRET_ASSIGNMENT.sub(lambda match: match.group(1) + '=[removed]', text)


def sql_literal(value):
    """Quote a validated value as a Unicode T-SQL string literal."""
    return "N'" + str(value).replace("'", "''") + "'"


def valid_guid(value):
    value = (value or '').strip().lower()
    return value if _GUID.fullmatch(value) and not set(value) <= {'0', '-'} else None


# ---------------------------------------------------------------- configuration

class Config:
    """Public, validated release inputs. Nothing here is a credential."""

    def __init__(self, server, database, api_client_id, tenant_id, resource_group,
                 owner_object_id, owner_login, organization_id, member_object_ids,
                 rule_name):
        self.server, self.database = server, database
        self.api_client_id, self.tenant_id = api_client_id, tenant_id
        self.resource_group, self.owner_object_id = resource_group, owner_object_id
        self.owner_login, self.organization_id = owner_login, organization_id
        self.member_object_ids, self.rule_name = member_object_ids, rule_name

    @property
    def server_name(self):
        return self.server.split('.')[0]

    @classmethod
    def from_environment(cls, environ):
        found = []

        def guid(name, label):
            value = valid_guid(environ.get(name))
            if value is None:
                found.append(f'{name} must be a valid GUID ({label}).')
            return value

        server = (environ.get('SQL_SERVER') or '').strip().lower()
        if not _SQL_SERVER.fullmatch(server):
            found.append('SQL_SERVER must be the full <name>.database.windows.net hostname.')
        database = (environ.get('SQL_DATABASE') or '').strip()
        if not _NAME.fullmatch(database):
            found.append('SQL_DATABASE must be a database name.')
        resource_group = (environ.get('RESOURCE_GROUP') or '').strip()
        if not re.fullmatch(r'rg-pb-dev-[a-z0-9-]+', resource_group):
            found.append('RESOURCE_GROUP must be a dev foundation resource group.')
        api_client_id = guid('SQL_MANAGED_IDENTITY_CLIENT_ID', 'API managed identity client ID')
        tenant_id = guid('ENTRA_TENANT_ID', 'tenant ID')
        owner_object_id = guid('SQL_OWNER_OBJECT_ID', 'PHONEBUDDY_SQL_ADMIN_OBJECT_ID')
        owner_login = (environ.get('SQL_OWNER_LOGIN') or '').strip()
        if (not owner_login or len(owner_login) > 128
                or any(ord(char) < 32 for char in owner_login)
                or owner_login.lower() in {'unresolved', 'placeholder'}):
            found.append('SQL_OWNER_LOGIN must be the owner login (PHONEBUDDY_SQL_ADMIN_LOGIN).')
        raw_members = [item.strip() for item in (environ.get('MEMBER_OBJECT_IDS') or '').split(',')
                       if item.strip()]
        members = []
        for item in raw_members:
            value = valid_guid(item)
            if value is None:
                found.append('PHONEBUDDY_DEV_MEMBER_OBJECT_IDS must list valid GUIDs, '
                             'comma separated.')
                break
            if value not in members:
                members.append(value)
        organization = (environ.get('MEMBER_ORGANIZATION_ID') or '').strip()
        organization_id = None
        if organization or members:
            organization_id = valid_guid(organization)
            if organization_id is None:
                found.append('PHONEBUDDY_DEV_ORGANIZATION_ID must be a valid GUID.')
        run_id = environ.get('GITHUB_RUN_ID', 'local')
        attempt = environ.get('GITHUB_RUN_ATTEMPT', '1')
        if not re.fullmatch(r'[0-9a-z]{1,20}', run_id) or not re.fullmatch(r'[0-9]{1,4}', attempt):
            found.append('GITHUB_RUN_ID and GITHUB_RUN_ATTEMPT must be simple identifiers.')
        if found:
            raise DatabaseReleaseError('Database release inputs are invalid: ' + ' '.join(found))
        return cls(server, database, api_client_id, tenant_id, resource_group, owner_object_id,
                   owner_login, organization_id, members, f'{FIREWALL_PREFIX}{run_id}-{attempt}')


# ------------------------------------------------------------------- migrations

class Migration:
    def __init__(self, version, name, text):
        self.version, self.name, self.text = version, name, text
        self.checksum = hashlib.sha256(text.encode('utf-8')).hexdigest()


def read_schema(path=SCHEMA):
    schema = json.loads(Path(path).read_text(encoding='utf-8'))
    if schema.get('migration_mode') not in {'none', 'expand', 'contract'}:
        raise DatabaseReleaseError('release-schema.json has an invalid migration_mode.')
    return schema


def _strip_comments(text):
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)
    return re.sub(r'--[^\n]*', ' ', text)


def discover_migrations(directory=MIGRATIONS, schema=None):
    """Return ordered, linted migrations and require the manifest to describe them."""
    schema = read_schema() if schema is None else schema
    files = sorted(Path(directory).glob('*.sql'))
    migrations = []
    for path in files:
        match = _MIGRATION_NAME.fullmatch(path.name)
        if not match:
            raise DatabaseReleaseError(f'Migration {path.name} must be named NNN_snake_case.sql.')
        migrations.append(Migration(int(match.group(1)), path.name,
                                    path.read_text(encoding='utf-8')))
    if [m.version for m in migrations] != list(range(1, len(migrations) + 1)):
        raise DatabaseReleaseError('Migrations must be numbered 001.. without gaps or repeats.')
    mode = schema['migration_mode']
    if migrations and (mode == 'none' or schema.get('version') != migrations[-1].version):
        raise DatabaseReleaseError(
            'infra/release-schema.json must record the latest migration version and an '
            'expand or contract migration_mode so recovery sees the true database state.')
    for migration in migrations:
        if mode != 'contract' and _DESTRUCTIVE.search(_strip_comments(migration.text)):
            raise DatabaseReleaseError(
                f'Migration {migration.name} is destructive; only a contract release may '
                'remove or rename data, and contract releases are never auto-recovered.')
    return migrations


LEDGER_SQL = """\
IF OBJECT_ID(N'dbo.SchemaMigration', N'U') IS NULL
  CREATE TABLE dbo.SchemaMigration (
    Version int NOT NULL CONSTRAINT PK_SchemaMigration PRIMARY KEY,
    Name nvarchar(128) NOT NULL,
    Checksum char(64) NOT NULL,
    AppliedAt datetime2(3) NOT NULL CONSTRAINT DF_SchemaMigration_AppliedAt DEFAULT (SYSUTCDATETIME())
  );
"""
LEDGER_QUERY = ("SET NOCOUNT ON; SELECT CONCAT(Version, N':', Checksum) "
                "FROM dbo.SchemaMigration ORDER BY Version;")


def apply_migrations(connection, migrations, log=print):
    """Apply each unrecorded migration in order; stop at the first failure.

    A migration may be partly applied if the connection drops, so every file is
    idempotent and is simply run again on the next release.
    """
    connection.execute(LEDGER_SQL)
    applied = {}
    for row in connection.query(LEDGER_QUERY):
        version, _, checksum = row.partition(':')
        applied[int(version)] = checksum
    for migration in migrations:
        recorded = applied.get(migration.version)
        if recorded is not None:
            if recorded != migration.checksum:
                raise DatabaseReleaseError(
                    f'Migration {migration.name} changed after it was applied; '
                    'add a new migration instead of editing an applied one.')
            log(f'Migration {migration.name}: already applied.')
            continue
        try:
            connection.execute(migration.text)
            connection.execute(
                'INSERT INTO dbo.SchemaMigration (Version, Name, Checksum) VALUES '
                f'({migration.version}, {sql_literal(migration.name)}, '
                f"'{migration.checksum}');")
        except DatabaseReleaseError as error:
            raise DatabaseReleaseError(f'Migration {migration.name} failed: {error}') from error
        log(f'Migration {migration.name}: applied.')


# ------------------------------------------------------- principals and grants

def ensure_external_user_sql(name, object_id):
    """Create an Entra user by SID, so no directory lookup or Graph access is needed."""
    return f"""\
DECLARE @name sysname = {sql_literal(name)};
DECLARE @sid varbinary(16) = CAST(CAST({sql_literal(object_id)} AS uniqueidentifier) AS varbinary(16));
DECLARE @bySid sysname = (SELECT name FROM sys.database_principals WHERE sid = @sid);
DECLARE @byName varbinary(85) = (SELECT sid FROM sys.database_principals WHERE name = @name);
IF @bySid IS NOT NULL AND @bySid <> @name
  THROW 50001, N'The Entra identity already has a differently named database user.', 1;
IF @byName IS NOT NULL AND @byName <> @sid
  THROW 50001, N'A database user with this name exists for a different Entra identity.', 1;
IF @byName IS NULL
BEGIN
  DECLARE @create nvarchar(max) = N'CREATE USER ' + QUOTENAME(@name)
    + N' WITH SID = ' + CONVERT(nvarchar(34), @sid, 1) + N', TYPE = E;';
  EXEC (@create);
END;
"""


def add_to_role_sql(name, role):
    return f"""\
DECLARE @member sysname = {sql_literal(name)};
IF IS_ROLEMEMBER({sql_literal(role)}, @member) = 0
BEGIN
  DECLARE @add nvarchar(max) = N'ALTER ROLE ' + QUOTENAME({sql_literal(role)})
    + N' ADD MEMBER ' + QUOTENAME(@member) + N';';
  EXEC (@add);
END;
"""


def verify_api_privileges_sql(name):
    """Fail the release if the API identity's effective rights exceed the pb_api grants.

    Effective rights are tested as the API user (EXECUTE AS USER with
    HAS_PERMS_BY_NAME), so grants that arrive through any role, nested role or
    public are caught, not only direct grants.
    """
    roles = ', '.join(sql_literal(role) for role in BROAD_ROLES)
    write = ('INSERT', 'UPDATE', 'DELETE', 'ALTER', 'CONTROL')
    database_checks = ' OR '.join(
        f"HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'{perm}') = 1"
        for perm in ('CONTROL', 'ALTER', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE',
                     'ALTER ANY USER', 'ALTER ANY ROLE'))
    table_checks = ' OR '.join(
        f"HAS_PERMS_BY_NAME(N'dbo.OrganizationMembership', N'OBJECT', N'{perm}') = 1"
        for perm in write)
    return f"""\
DECLARE @api sysname = {sql_literal(name)};
IF EXISTS (SELECT 1 FROM sys.database_role_members m
    JOIN sys.database_principals r ON r.principal_id = m.role_principal_id
    JOIN sys.database_principals u ON u.principal_id = m.member_principal_id
    WHERE u.name = @api AND r.name IN ({roles}))
  THROW 50002, N'The API identity holds a broad database role.', 1;
DECLARE @problem nvarchar(200) = NULL;
EXECUTE AS USER = @api;
IF {table_checks}
  SET @problem = N'The API identity can write memberships (effective permission).';
ELSE IF {database_checks}
  SET @problem = N'The API identity holds effective database-wide permissions.';
REVERT;
IF @problem IS NOT NULL
  THROW 50003, @problem, 1;
"""


def seed_membership_sql(organization_id, tenant_id, object_id, role=USER_ROLE):
    """Insert a missing membership; existing rows are never touched or re-activated."""
    org, tenant, member = (sql_literal(value) for value in (organization_id, tenant_id, object_id))
    return f"""\
IF NOT EXISTS (SELECT 1 FROM dbo.OrganizationMembership
    WHERE OrganizationId = {org} AND TenantId = {tenant} AND ObjectId = {member})
  INSERT INTO dbo.OrganizationMembership (OrganizationId, TenantId, ObjectId, Role)
  VALUES ({org}, {tenant}, {member}, {sql_literal(role)});
"""


def configure_owner(connection, config, log=print):
    """Give the owner a database user first, so the administrator switch cannot lock them out."""
    connection.execute(ensure_external_user_sql(config.owner_login, config.owner_object_id))
    connection.execute(add_to_role_sql(config.owner_login, OWNER_ROLE))
    log('Owner database user ready.')


def configure_principals(connection, config, log=print):
    connection.execute(ensure_external_user_sql(API_USER, config.api_client_id))
    connection.execute(add_to_role_sql(API_USER, API_ROLE))
    connection.execute(verify_api_privileges_sql(API_USER))
    log('API identity user ready with least-privilege role.')
    for object_id in config.member_object_ids:
        # Only the owner is seeded as admin; every other listed member is a plain user.
        role = ADMIN_ROLE if object_id == config.owner_object_id else USER_ROLE
        connection.execute(seed_membership_sql(config.organization_id, config.tenant_id,
                                               object_id, role))
    log(f'Membership seed checked for {len(config.member_object_ids)} principal(s).')


# ------------------------------------------------------------------ connections

class SqlcmdConnection:
    """Run T-SQL through go-sqlcmd using the Azure CLI's Entra credential.

    ActiveDirectoryAzCli obtains the token with `az account get-access-token`
    inside sqlcmd; no password or token is passed on a command line or printed.
    """

    def __init__(self, server, database, binary='sqlcmd', run=subprocess.run):
        self.base = [binary, '-S', server, '-d', database, '--authentication-method',
                     'ActiveDirectoryAzCli', '-b', '-I']
        self.run = run

    def _run(self, extra):
        result = self.run(self.base + extra, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            detail = scrub((result.stdout or '') + (result.stderr or '')).strip()
            raise DatabaseReleaseError(detail[:2000] or f'sqlcmd exited {result.returncode}')
        return result.stdout or ''

    def execute(self, sql):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'batch.sql'
            path.write_text(sql, encoding='utf-8')
            self._run(['-i', str(path)])

    def query(self, sql):
        output = self._run(['-Q', sql, '-h', '-1', '-W'])
        return [line.strip() for line in output.splitlines() if line.strip()]


# --------------------------------------------------------------------- firewall

class FirewallCleanupError(DatabaseReleaseError):
    pass


class TemporaryFirewallRule:
    """Open one firewall rule for the runner and always remove it."""

    def __init__(self, az, config, ip):
        self.az, self.config, self.ip = az, config, ip

    def _scope(self):
        return ['--resource-group', self.config.resource_group,
                '--server', self.config.server_name]

    def __enter__(self):
        try:
            self.az(['sql', 'server', 'firewall-rule', 'create', *self._scope(),
                     '--name', self.config.rule_name, '--start-ip-address', self.ip,
                     '--end-ip-address', self.ip])
        except Exception:
            self.remove()  # a partly created rule must not survive
            raise
        return self

    def remove(self):
        try:
            self.az(['sql', 'server', 'firewall-rule', 'delete', *self._scope(),
                     '--name', self.config.rule_name, '--yes'])
        except Exception as error:
            raise FirewallCleanupError(
                f'Could not remove temporary firewall rule {self.config.rule_name}: '
                f'{scrub(error)}') from error

    def __exit__(self, exc_type, exc, _traceback):
        try:
            self.remove()
        except FirewallCleanupError as cleanup:
            if exc is None:
                raise
            # Report both: the original failure must not be hidden by the cleanup failure.
            raise DatabaseReleaseError(
                f'{scrub(exc)} Additionally: {cleanup}') from exc
        return False


def remove_stale_rules(az, config, log=print):
    """Delete rules left by an earlier run that was killed before cleanup."""
    scope = ['--resource-group', config.resource_group, '--server', config.server_name]
    names = az(['sql', 'server', 'firewall-rule', 'list', *scope, '--query',
                f"[?starts_with(name, '{FIREWALL_PREFIX}')].name", '--output', 'tsv'])
    for name in (line.strip() for line in names.splitlines()):
        if re.fullmatch(re.escape(FIREWALL_PREFIX) + r'[0-9a-z-]+', name):
            az(['sql', 'server', 'firewall-rule', 'delete', *scope, '--name', name, '--yes'])
            log(f'Removed stale firewall rule {name}.')


def run_az(arguments):
    result = subprocess.run(['az', *arguments], capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise DatabaseReleaseError(scrub(result.stderr or result.stdout).strip()[:2000]
                                   or f'az exited {result.returncode}')
    return result.stdout


def detect_public_ip(fetch=None):
    fetch = fetch or (lambda: urlopen('https://api.ipify.org', timeout=15).read().decode())
    try:
        address = ipaddress.ip_address(fetch().strip())
    except (ValueError, OSError) as error:
        raise DatabaseReleaseError('Could not determine the runner public IPv4 address.') from error
    if address.version != 4 or not address.is_global:
        raise DatabaseReleaseError('The runner address is not a public IPv4 address.')
    return str(address)


def wait_for_access(connection, attempts=12, delay=20, sleep=time.sleep, log=print):
    """Firewall and administrator changes take time to propagate; retry the first connect."""
    for attempt in range(1, attempts + 1):
        try:
            connection.query('SET NOCOUNT ON; SELECT 1;')
            return
        except DatabaseReleaseError as error:
            if attempt == attempts:
                raise DatabaseReleaseError(
                    f'The release identity could not connect to the database: {error}') from error
            log(f'Database not reachable yet (attempt {attempt}/{attempts}); retrying.')
            sleep(delay)


def run_release(config, migrations, connection, az, ip, sleep=time.sleep, log=print):
    """Open the firewall, migrate, configure principals, and always close the firewall."""
    remove_stale_rules(az, config, log)
    with TemporaryFirewallRule(az, config, ip):
        wait_for_access(connection, sleep=sleep, log=log)
        # The owner's access comes first: nothing that can fail runs between the
        # administrator switch and this user, apart from connecting.
        configure_owner(connection, config, log)
        apply_migrations(connection, migrations, log)
        configure_principals(connection, config, log)
    log('Temporary firewall rule removed.')


# --------------------------------------------------------------------------- CLI

def token_object_id(token):
    """Read the object ID claim from the release identity's own token."""
    try:
        payload = token.split('.')[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    except (IndexError, ValueError) as error:
        raise DatabaseReleaseError('The Entra token could not be read.') from error
    oid = valid_guid(claims.get('oid'))
    if oid is None:
        raise DatabaseReleaseError('The Entra token has no valid object ID claim.')
    return oid


def deployment_identity(az, output):
    token = az(['account', 'get-access-token', '--resource', DATABASE_RESOURCE,
                '--query', 'accessToken', '--output', 'tsv']).strip()
    Path(output).write_text(token_object_id(token) + '\n', encoding='utf-8')


def environment_config(environ=None):
    return Config.from_environment(os.environ if environ is None else environ)


def firewall_scope(environ):
    """Only the server and group are needed to remove rules, so cleanup never depends
    on the owner or membership inputs being valid."""
    server = (environ.get('SQL_SERVER') or '').strip().lower()
    group = (environ.get('RESOURCE_GROUP') or '').strip()
    if not _SQL_SERVER.fullmatch(server) or not re.fullmatch(r'rg-pb-dev-[a-z0-9-]+', group):
        raise DatabaseReleaseError('SQL_SERVER and RESOURCE_GROUP are required to clean up.')
    return types.SimpleNamespace(resource_group=group, server_name=server.split('.')[0])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check', help='validate inputs and migrations without Azure access')
    identity = commands.add_parser('deployment-identity',
                                   help='write the release identity object ID to a file')
    identity.add_argument('--output', type=Path, required=True)
    commands.add_parser('apply', help='migrate and configure the database')
    commands.add_parser('cleanup-firewall', help='remove any leftover release firewall rules')
    options = parser.parse_args(argv)
    try:
        if options.command == 'deployment-identity':
            deployment_identity(run_az, options.output)
            return 0
        if options.command == 'cleanup-firewall':
            remove_stale_rules(run_az, firewall_scope(os.environ))
            return 0
        config = environment_config()
        migrations = discover_migrations()
        if options.command == 'check':
            print(f'Database release inputs valid; {len(migrations)} migration(s) found.')
        else:
            run_release(config, migrations,
                        SqlcmdConnection(config.server, config.database),
                        run_az, detect_public_ip())
    except DatabaseReleaseError as error:
        print(f'::error::Database release: {scrub(error)}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
