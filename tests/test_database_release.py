"""Cover the dev release's database migration, grant and firewall handling (issue 161)."""
import base64
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

from scripts import database_release as dr
from scripts.release_recovery import recovery_decision

ROOT = Path(__file__).resolve().parents[1]
TENANT = '11111111-2222-4333-8444-555555555555'
API_CLIENT = '99999999-8888-4777-9666-555555555555'
OWNER = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'
MEMBER = 'bbbbbbbb-bbbb-4ccc-8ddd-eeeeeeeeeeee'
ORGANIZATION = 'cccccccc-bbbb-4ccc-8ddd-eeeeeeeeeeee'
ENVIRONMENT = {
    'SQL_SERVER': 'sql-pb-dev-abc123.database.windows.net',
    'SQL_DATABASE': 'phonebuddy',
    'RESOURCE_GROUP': 'rg-pb-dev-francecentral-foundation',
    'SQL_MANAGED_IDENTITY_CLIENT_ID': API_CLIENT,
    'ENTRA_TENANT_ID': TENANT,
    'SQL_OWNER_OBJECT_ID': OWNER,
    'SQL_OWNER_LOGIN': "Owner O'Brien",
    'MEMBER_OBJECT_IDS': f'{OWNER}, {MEMBER},{OWNER}',
    'MEMBER_ORGANIZATION_ID': ORGANIZATION,
    'GITHUB_RUN_ID': '42',
    'GITHUB_RUN_ATTEMPT': '2',
}
# Built at runtime so no token-shaped literal lives in the repository.
SECRET_TOKEN = '.'.join(['ey' + 'JhbGciOiJSUzI1NiJ9', 'ey' + 'JvaWQiOiJ4In0', 'c2lnbmF0dXJl' + 'LXNlY3JldA'])


class FakeConnection:
    def __init__(self, ledger=(), fail_on=None):
        self.ledger, self.fail_on, self.executed = list(ledger), fail_on, []

    def execute(self, sql):
        self.executed.append(sql)
        if self.fail_on and self.fail_on in sql:
            raise dr.DatabaseReleaseError('boom ' + SECRET_TOKEN)

    def query(self, sql):
        return list(self.ledger) if 'SchemaMigration' in sql else ['1']


def config(**overrides):
    return dr.Config.from_environment({**ENVIRONMENT, **overrides})


def migration(version, text='CREATE TABLE dbo.T (Id int);'):
    return dr.Migration(version, f'{version:03d}_step.sql', text)


class ConfigTests(unittest.TestCase):
    def test_valid_inputs_are_normalized(self):
        result = config()
        self.assertEqual(result.server_name, 'sql-pb-dev-abc123')
        self.assertEqual(result.member_object_ids, [OWNER, MEMBER])
        self.assertEqual(result.rule_name, 'pb-release-42-2')

    def test_invalid_values_are_all_named(self):
        for name, value in [
            ('SQL_MANAGED_IDENTITY_CLIENT_ID', 'not-a-guid'),
            ('SQL_MANAGED_IDENTITY_CLIENT_ID', '00000000-0000-0000-0000-000000000000'),
            ('SQL_OWNER_OBJECT_ID', ''),
            ('SQL_OWNER_LOGIN', 'UNRESOLVED'),
            ('MEMBER_OBJECT_IDS', f'{OWNER},nope'),
            ('MEMBER_ORGANIZATION_ID', ''),
            ('SQL_SERVER', 'sql-pb-dev-abc123'),
            ('RESOURCE_GROUP', 'rg-pb-prod-foundation'),
        ]:
            with self.subTest(name=name, value=value):
                with self.assertRaises(dr.DatabaseReleaseError) as raised:
                    config(**{name: value})
                self.assertIn(name.replace('MEMBER_ORGANIZATION_ID', 'PHONEBUDDY_DEV_ORGANIZATION_ID')
                              .replace('MEMBER_OBJECT_IDS', 'PHONEBUDDY_DEV_MEMBER_OBJECT_IDS'),
                              str(raised.exception))

    def test_no_members_needs_no_organization(self):
        result = config(MEMBER_OBJECT_IDS='', MEMBER_ORGANIZATION_ID='')
        self.assertEqual(result.member_object_ids, [])


class MigrationDiscoveryTests(unittest.TestCase):
    def write(self, directory, files):
        for name, text in files.items():
            (Path(directory) / name).write_text(text, encoding='utf-8')

    def test_repository_migrations_match_the_release_schema(self):
        schema = json.loads((ROOT / 'infra/release-schema.json').read_text())
        migrations = dr.discover_migrations()
        self.assertEqual([m.name for m in migrations],
                         ['001_identity.sql', '002_api_role_grants.sql'])
        self.assertEqual(schema['version'], migrations[-1].version)
        self.assertEqual(schema['migration_mode'], 'expand')
        self.assertIn(schema['version'], schema['compatible_versions'])

    def test_gaps_bad_names_and_stale_schema_fail(self):
        schema = {'version': 2, 'migration_mode': 'expand'}
        for files in ({'002_a.sql': 'SELECT 1;'}, {'001_a.sql': 'x', '003_b.sql': 'x'},
                      {'001_Bad.sql': 'x'}):
            with self.subTest(files=list(files)), tempfile.TemporaryDirectory() as directory:
                self.write(directory, files)
                with self.assertRaises(dr.DatabaseReleaseError):
                    dr.discover_migrations(directory, schema)
        with tempfile.TemporaryDirectory() as directory:
            self.write(directory, {'001_a.sql': 'SELECT 1;', '002_b.sql': 'SELECT 1;'})
            for stale in ({'version': 1, 'migration_mode': 'expand'},
                          {'version': 2, 'migration_mode': 'none'}):
                with self.assertRaisesRegex(dr.DatabaseReleaseError, 'release-schema'):
                    dr.discover_migrations(directory, stale)

    def test_destructive_sql_needs_a_contract_release(self):
        for sql in ('DROP TABLE dbo.T;', 'ALTER TABLE t ALTER COLUMN c int;',
                    'DELETE FROM dbo.T;', 'TRUNCATE TABLE dbo.T;', 'EXEC sp_rename a, b;'):
            with self.subTest(sql=sql), tempfile.TemporaryDirectory() as directory:
                self.write(directory, {'001_a.sql': sql})
                with self.assertRaisesRegex(dr.DatabaseReleaseError, 'destructive'):
                    dr.discover_migrations(directory, {'version': 1, 'migration_mode': 'expand'})
                self.assertEqual(len(dr.discover_migrations(
                    directory, {'version': 1, 'migration_mode': 'contract'})), 1)

    def test_comments_and_grants_are_not_destructive(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(directory, {'001_a.sql': '-- drop table\nGRANT SELECT, DELETE ON OBJECT::dbo.T TO r;'})
            self.assertEqual(len(dr.discover_migrations(
                directory, {'version': 1, 'migration_mode': 'expand'})), 1)


class ApplyMigrationTests(unittest.TestCase):
    def test_applies_in_order_and_records_each_version(self):
        connection, log = FakeConnection(), []
        dr.apply_migrations(connection, [migration(1), migration(2)], log.append)
        batches = connection.executed
        self.assertIn('dbo.SchemaMigration', batches[0])
        self.assertEqual(batches[1], migration(1).text)
        self.assertIn('VALUES (1,', batches[2])
        self.assertEqual(batches[3], migration(2).text)
        self.assertIn('VALUES (2,', batches[4])

    def test_recorded_migrations_are_skipped_and_edits_are_rejected(self):
        first = migration(1)
        connection = FakeConnection(ledger=[f'1:{first.checksum}'])
        dr.apply_migrations(connection, [first, migration(2, 'SELECT 2;')], lambda _: None)
        self.assertNotIn(first.text, connection.executed)
        with self.assertRaisesRegex(dr.DatabaseReleaseError, 'changed after it was applied'):
            dr.apply_migrations(FakeConnection(ledger=['1:' + '0' * 64]), [first], lambda _: None)

    def test_failure_stops_before_later_migrations_and_is_not_recorded(self):
        connection = FakeConnection(fail_on='SECOND')
        migrations = [migration(1), migration(2, 'SECOND;'), migration(3, 'THIRD;')]
        with self.assertRaises(dr.DatabaseReleaseError) as raised:
            dr.apply_migrations(connection, migrations, lambda _: None)
        self.assertIn('002_step.sql failed', str(raised.exception))
        self.assertFalse(any('THIRD' in sql for sql in connection.executed))
        self.assertFalse(any('VALUES (2,' in sql for sql in connection.executed))


class PrincipalTests(unittest.TestCase):
    def test_users_are_created_by_sid_without_a_directory_lookup(self):
        sql = dr.ensure_external_user_sql('id-pb-dev-pull', API_CLIENT)
        self.assertIn(f"CAST(CAST(N'{API_CLIENT}' AS uniqueidentifier) AS varbinary(16))", sql)
        self.assertIn('WITH SID =', sql)
        self.assertIn('TYPE = E', sql)
        self.assertNotIn('EXTERNAL PROVIDER', sql.upper())

    def test_hostile_names_are_escaped(self):
        sql = dr.ensure_external_user_sql("o'; DROP TABLE x;--", OWNER)
        self.assertIn("N'o''; DROP TABLE x;--'", sql)
        self.assertIn('QUOTENAME(@name)', sql)

    def test_api_gets_only_the_migration_role_and_is_checked(self):
        connection = FakeConnection()
        dr.configure_principals(connection, config(), lambda _: None)
        joined = '\n'.join(connection.executed)
        self.assertIn("IS_ROLEMEMBER(N'pb_api'", joined)
        self.assertIn('broad database role', joined)
        self.assertIn('can write memberships', joined)
        # The API identity is never added to db_owner; only the owner is.
        api_role_batches = [sql for sql in connection.executed if "N'id-pb-dev-pull'" in sql]
        self.assertFalse(any("N'db_owner'" in sql and 'ALTER ROLE' in sql for sql in api_role_batches))
        owner_roles = [sql for sql in connection.executed if "N'db_owner'" in sql]
        self.assertTrue(any("N'Owner O''Brien'" in sql for sql in owner_roles))

    def test_grant_migration_gives_exactly_the_api_permissions(self):
        text = (ROOT / 'services/api/migrations/002_api_role_grants.sql').read_text()
        statements = [line for line in text.splitlines() if re.match(r'(GRANT|REVOKE|DENY)', line)]
        self.assertEqual(statements, [
            'GRANT SELECT ON OBJECT::dbo.OrganizationMembership TO pb_api;',
            'GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::dbo.WebSocketTicket TO pb_api;',
            'REVOKE INSERT, UPDATE, DELETE ON OBJECT::dbo.OrganizationMembership FROM pb_api;',
        ])
        self.assertIn('IF DATABASE_PRINCIPAL_ID(N\'pb_api\') IS NULL', text)
        self.assertNotRegex(text.upper(), r'PASSWORD|SECRET|TOKEN|DB_OWNER|DB_DATAWRITER')

    def test_membership_seed_is_insert_if_missing_only(self):
        sql = dr.seed_membership_sql(ORGANIZATION, TENANT, MEMBER)
        self.assertIn('IF NOT EXISTS', sql)
        self.assertIn('INSERT INTO dbo.OrganizationMembership', sql)
        self.assertNotRegex(sql.upper(), r'UPDATE|MERGE|DELETE|ISACTIVE')
        connection = FakeConnection()
        dr.configure_principals(connection, config(), lambda _: None)
        seeds = [sql for sql in connection.executed if 'INSERT INTO dbo.OrganizationMembership' in sql]
        self.assertEqual(len(seeds), 2)

    def test_no_members_runs_no_seed(self):
        connection = FakeConnection()
        dr.configure_principals(connection, config(MEMBER_OBJECT_IDS='', MEMBER_ORGANIZATION_ID=''),
                                lambda _: None)
        self.assertFalse(any('OrganizationMembership' in sql and 'INSERT' in sql
                             for sql in connection.executed if 'SELECT 1' not in sql
                             and 'permission' not in sql.lower()
                             and 'THROW' not in sql))


class FirewallTests(unittest.TestCase):
    def az_recorder(self, fail_on=None, listing=''):
        calls = []

        def az(arguments):
            calls.append(arguments)
            if fail_on and fail_on in arguments:
                raise dr.DatabaseReleaseError('az failed')
            return listing if 'list' in arguments else ''
        az.calls = calls
        return az

    def deletes(self, az):
        return [c for c in az.calls if 'delete' in c]

    def test_rule_is_opened_for_the_runner_ip_and_removed(self):
        az = self.az_recorder()
        with dr.TemporaryFirewallRule(az, config(), '20.50.1.9'):
            created = az.calls[0]
            self.assertIn('create', created)
            self.assertEqual(created[created.index('--start-ip-address') + 1], '20.50.1.9')
            self.assertEqual(created[created.index('--end-ip-address') + 1], '20.50.1.9')
        self.assertEqual(len(self.deletes(az)), 1)
        self.assertIn('pb-release-42-2', self.deletes(az)[0])

    def test_rule_is_removed_when_the_body_fails(self):
        az = self.az_recorder()
        with self.assertRaisesRegex(RuntimeError, 'body'):
            with dr.TemporaryFirewallRule(az, config(), '20.50.1.9'):
                raise RuntimeError('body')
        self.assertEqual(len(self.deletes(az)), 1)

    def test_partly_created_rule_is_removed(self):
        az = self.az_recorder(fail_on='create')
        with self.assertRaisesRegex(dr.DatabaseReleaseError, 'az failed'):
            with dr.TemporaryFirewallRule(az, config(), '20.50.1.9'):
                self.fail('must not enter')
        self.assertEqual(len(self.deletes(az)), 1)

    def test_failed_cleanup_is_reported_not_swallowed(self):
        az = self.az_recorder(fail_on='delete')
        with self.assertRaises(dr.FirewallCleanupError):
            with dr.TemporaryFirewallRule(az, config(), '20.50.1.9'):
                pass

    def test_stale_rules_from_killed_runs_are_removed(self):
        az = self.az_recorder(listing='pb-release-1-1\nunrelated-rule\npb-release-7-3\n')
        dr.remove_stale_rules(az, config(), lambda _: None)
        removed = [c[c.index('--name') + 1] for c in self.deletes(az)]
        self.assertEqual(removed, ['pb-release-1-1', 'pb-release-7-3'])

    def test_public_ip_must_be_a_public_ipv4(self):
        self.assertEqual(dr.detect_public_ip(lambda: '20.50.1.9\n'), '20.50.1.9')
        for bad in ('10.0.0.4', '::1', 'nope', '2001:db8::1'):
            with self.subTest(bad=bad), self.assertRaises(dr.DatabaseReleaseError):
                dr.detect_public_ip(lambda: bad)

    def test_failed_migration_still_closes_the_firewall_and_stops(self):
        az = self.az_recorder()
        connection = FakeConnection(fail_on='SECOND')
        migrations = [migration(1), migration(2, 'SECOND;')]
        with self.assertRaises(dr.DatabaseReleaseError):
            dr.run_release(config(), migrations, connection, az, '20.50.1.9',
                           sleep=lambda _: None, log=lambda _: None)
        self.assertEqual(len(self.deletes(az)), 1)
        self.assertFalse(any('CREATE USER' in sql for sql in connection.executed))

    def test_success_runs_everything_between_open_and_close(self):
        az = self.az_recorder()
        connection = FakeConnection()
        dr.run_release(config(), [migration(1)], connection, az, '20.50.1.9',
                       sleep=lambda _: None, log=lambda _: None)
        verbs = [c[3] for c in az.calls]
        self.assertEqual(verbs, ['list', 'create', 'delete'])
        self.assertTrue(any('CREATE USER' in sql for sql in connection.executed))

    def test_connect_retries_while_access_propagates_then_gives_up(self):
        class Flaky:
            def __init__(self, failures):
                self.failures, self.calls = failures, 0

            def query(self, sql):
                self.calls += 1
                if self.calls <= self.failures:
                    raise dr.DatabaseReleaseError('Login failed')
                return ['1']

        slept = []
        flaky = Flaky(2)
        dr.wait_for_access(flaky, attempts=5, delay=7, sleep=slept.append, log=lambda _: None)
        self.assertEqual((flaky.calls, slept), (3, [7, 7]))
        with self.assertRaisesRegex(dr.DatabaseReleaseError, 'could not connect'):
            dr.wait_for_access(Flaky(99), attempts=2, delay=1, sleep=lambda _: None,
                               log=lambda _: None)


class SecretHandlingTests(unittest.TestCase):
    def test_scrub_removes_tokens_and_credentials(self):
        text = f'Login failed {SECRET_TOKEN} ' + 'pass' + 'word=hunter2 accessToken: abc'
        cleaned = dr.scrub(text)
        for leaked in (SECRET_TOKEN, 'hunter2', 'abc'):
            self.assertNotIn(leaked, cleaned)

    def test_migration_failures_never_print_a_token(self):
        connection = FakeConnection(fail_on='SECOND')
        with self.assertRaises(dr.DatabaseReleaseError) as raised:
            dr.apply_migrations(connection, [migration(1, 'SECOND;')], lambda _: None)
        stderr = io.StringIO()
        with mock.patch.object(dr, 'environment_config', return_value=config()), \
                mock.patch.object(dr, 'discover_migrations', return_value=[migration(1)]), \
                mock.patch.object(dr, 'detect_public_ip', return_value='20.50.1.9'), \
                mock.patch.object(dr, 'run_az', return_value=''), \
                mock.patch.object(dr, 'SqlcmdConnection', return_value=FakeConnection(fail_on='CREATE TABLE')), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            with mock.patch.object(dr, 'wait_for_access'):
                self.assertEqual(dr.main(['apply']), 1)
        self.assertNotIn(SECRET_TOKEN, stderr.getvalue())
        self.assertIn('::error::', stderr.getvalue())
        self.assertIsNotNone(raised.exception)

    def test_sqlcmd_uses_entra_cli_auth_and_scrubs_failures(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return mock.Mock(returncode=1, stdout='', stderr=f'denied {SECRET_TOKEN}')

        connection = dr.SqlcmdConnection('server.database.windows.net', 'db', run=fake_run)
        with self.assertRaises(dr.DatabaseReleaseError) as raised:
            connection.query('SELECT 1')
        self.assertNotIn(SECRET_TOKEN, str(raised.exception))
        command = ' '.join(calls[0])
        self.assertIn('ActiveDirectoryAzCli', command)
        for forbidden in ('-P', '--password', '-U'):
            self.assertNotIn(forbidden, calls[0])

    def test_deployment_identity_writes_only_the_object_id(self):
        payload = base64.urlsafe_b64encode(json.dumps({'oid': OWNER}).encode()).decode().rstrip('=')
        token = f'ey' + f'JhbGciOiJub25lIn0.{payload}.c2ln'
        calls = []

        def az(arguments):
            calls.append(arguments)
            return token + '\n'

        with tempfile.TemporaryDirectory() as directory, \
                contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            target = Path(directory) / 'oid.txt'
            dr.deployment_identity(az, target)
            self.assertEqual(target.read_text(), OWNER + '\n')
        self.assertIn('https://database.windows.net/', calls[0])
        self.assertNotIn(token, out.getvalue() + err.getvalue() + target.name)

    def test_token_without_object_id_is_rejected(self):
        payload = base64.urlsafe_b64encode(b'{}').decode().rstrip('=')
        with self.assertRaises(dr.DatabaseReleaseError):
            dr.token_object_id(f'a.{payload}.c')
        with self.assertRaises(dr.DatabaseReleaseError):
            dr.token_object_id('garbage')

    def test_sources_contain_no_credential_material(self):
        for path in ('scripts/database_release.py', 'services/api/migrations/002_api_role_grants.sql'):
            text = (ROOT / path).read_text().lower()
            self.assertNotRegex(text, r'administratorloginpassword|connectionstring|sas=|client_secret')


class WorkflowWiringTests(unittest.TestCase):
    deploy = (ROOT / '.github/workflows/azure-deploy.yml').read_text()

    def position(self, text):
        index = self.deploy.find(text)
        self.assertGreaterEqual(index, 0, text)
        return index

    def test_migrations_run_before_the_traffic_changing_deployment(self):
        order = [
            self.position('scripts/database_release.py check'),
            self.position('Make the deployment identity the SQL administrator through Bicep'),
            self.position('scripts/database_release.py apply'),
            self.position('- name: Apply the reviewed Bicep release'),
        ]
        self.assertEqual(order, sorted(order))
        sql_admin_step = self.deploy[order[1]:order[2]]
        self.assertIn('deployWorkload=false', sql_admin_step)
        self.assertIn('manageSqlAdministrator=true', sql_admin_step)

    def test_firewall_cleanup_always_runs_and_follows_the_migration(self):
        cleanup = self.position('scripts/database_release.py cleanup-firewall')
        self.assertGreater(cleanup, self.position('scripts/database_release.py apply'))
        step = self.deploy[self.deploy.rfind('- name:', 0, cleanup):cleanup]
        self.assertIn('if: always()', step)

    def test_failed_migration_does_not_count_as_a_partial_deployment(self):
        # Recovery is required only when the deployment step failed; a migration
        # failure leaves the deployment step skipped, so traffic never changed.
        from scripts.deployment_policy import recovery_required
        self.assertFalse(recovery_required('skipped', '', 'skipped', 'skipped', 'skipped'))

    def test_sqlcmd_is_pinned_and_checksummed_and_no_sql_secret_is_used(self):
        self.assertIn('go-sqlcmd/releases/download/v1.10.0/', self.deploy)
        self.assertIn('sha256sum --check', self.deploy[self.position('go-sqlcmd'):])
        self.assertNotRegex(self.deploy.lower(), r'sql_?password|sqlcmd.* -p |administratorloginpassword')
        for name in ('PHONEBUDDY_DEV_MEMBER_OBJECT_IDS', 'PHONEBUDDY_DEV_ORGANIZATION_ID',
                     'PHONEBUDDY_SQL_ADMIN_OBJECT_ID', 'PHONEBUDDY_SQL_ADMIN_LOGIN'):
            self.assertRegex(self.deploy, rf'\$\{{\{{ vars\.{name} \}}\}}')
        self.assertNotIn('secrets.PHONEBUDDY', self.deploy)

    def test_recovery_never_migrates(self):
        recover = (ROOT / '.github/workflows/azure-recover.yml').read_text()
        self.assertNotIn('database_release', recover)
        self.assertNotIn('sqlcmd', recover)
        deploy_recovery = self.deploy[self.position('- name: Redeploy the immutable last-known-good'):]
        self.assertNotIn('database_release', deploy_recovery.split('- name: Get the last-known-good')[0])

    def test_bicep_makes_the_deployment_identity_the_entra_administrator(self):
        hosting = (ROOT / 'infra/hosting.bicep').read_text()
        self.assertIn("Microsoft.Sql/servers/administrators@2023-08-01", hosting)
        self.assertIn('param manageSqlAdministrator bool = false', hosting)
        self.assertNotIn('administratorLoginPassword', hosting)
        data = (ROOT / 'infra/modules/data-platform.bicep').read_text()
        self.assertIn('azureADOnlyAuthentication: true', data)
        self.assertIn('principalType: sqlAdminPrincipalType', data)


class RecoverySafetyTests(unittest.TestCase):
    def manifest(self, sha, version, compatible, mode):
        return {
            'schema_version': 1, 'source_sha': sha * 40, 'workflow_run_id': 1,
            'workflow_run_attempt': 1, 'image_digest': 'sha256:' + 'a' * 64,
            'frontend_blob': f'releases/{sha * 40}/1-1/web.tar.gz', 'frontend_sha256': 'b' * 64,
            'configuration': {
                'environment': 'dev', 'resource_group': 'rg-pb-dev-x', 'container_app': 'ca-pb-dev-x',
                'static_site_name': '', 'static_site_location': 'eastus2',
                'container_image_digest': 'a' * 64, 'hosting_template_sha256': 'c' * 64,
                'release_schema_sha256': 'd' * 64},
            'schema_compatibility': {'version': version, 'compatible_versions': compatible,
                                     'migration_mode': mode},
            'release_configuration_sha256': 'e' * 64,
        }

    def test_release_that_migrated_is_not_automatically_rolled_back_to_a_schema_blind_release(self):
        schema = json.loads((ROOT / 'infra/release-schema.json').read_text())
        candidate = self.manifest('1', schema['version'], schema['compatible_versions'],
                                  schema['migration_mode'])
        previous = self.manifest('2', 0, [0], 'none')
        self.assertEqual(recovery_decision(candidate, previous),
                         (False, 'last_known_good_does_not_support_candidate_schema'))
        contract = self.manifest('1', 3, [3], 'contract')
        compatible = self.manifest('2', 2, [2, 3], 'expand')
        self.assertEqual(recovery_decision(contract, compatible),
                         (False, 'contract_migration_cannot_auto_rollback'))


if __name__ == '__main__':
    unittest.main()
