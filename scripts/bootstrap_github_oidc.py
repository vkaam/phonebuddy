"""Create environment-scoped GitHub OIDC principals in Azure.

This is an explicit bootstrap operation. It is dry-run unless --apply is passed.
The script never creates a client secret and does not print tenant, subscription,
application, or principal identifiers.
"""

import argparse
import json
import subprocess
import sys


REPOSITORY = "vkaam/phonebuddy"
ENVIRONMENTS = ("dev", "test")
REGION = "westeurope"
ROLE = "Contributor"
ISSUER = "https://token.actions.githubusercontent.com"
AUDIENCE = "api://AzureADTokenExchange"


class AzCommandError(Exception):
    """A sanitized Azure CLI failure that does not retain command arguments."""

    def __init__(self, returncode):
        self.returncode = returncode
        super().__init__(f"Azure CLI command failed (exit status {returncode}).")


def az(*args, json_output=False):
    command = ["az", *args]
    if json_output:
        command.extend(("--output", "json"))
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise AzCommandError(error.returncode) from None
    return json.loads(result.stdout) if json_output and result.stdout.strip() else result.stdout.strip()


def ensure_single(items, label):
    if len(items) > 1:
        raise RuntimeError(f"More than one Azure {label} matched; resolve duplicates before retrying.")
    return items[0] if items else None


def validate_federated_credentials(credentials, expected):
    """Accept no trust or exactly the expected GitHub trust; reject all others."""
    if len(credentials) > 1:
        raise RuntimeError("Application has multiple federated credentials; review them manually before granting access.")
    if not credentials:
        return None
    credential = credentials[0]
    actual = {key: credential.get(key) for key in expected}
    if credential.get("name") != "github-environment" or actual != expected:
        raise RuntimeError("Application has an unexpected federated credential; review it manually before granting access.")
    return credential


def bootstrap(environment, subscription_id, apply):
    app_name = f"PhoneBuddy GitHub Deploy {environment}"
    resource_group = f"rg-pb-{environment}-{REGION}-foundation"
    subject = f"repo:{REPOSITORY}:environment:{environment}"
    print(f"Environment: {environment}; resource group: {resource_group}; role: {ROLE}")
    print(f"Federation subject: {subject}")
    if not apply:
        print("Dry run only. Re-run with --apply to create or reconcile this identity.")
        return

    az("account", "set", "--subscription", subscription_id)
    groups = az("group", "list", "--query", f"[?name=='{resource_group}']", json_output=True)
    group = ensure_single(groups, f"resource group named {resource_group}")
    if not group:
        raise RuntimeError(f"Required resource group {resource_group} does not exist in the selected subscription.")

    apps = az("ad", "app", "list", "--filter", f"displayName eq '{app_name}'", json_output=True)
    app = ensure_single(apps, f"application named {app_name}")
    if not app:
        app = az("ad", "app", "create", "--display-name", app_name, json_output=True)
        print(f"Created application registration for {environment}.")
    app_id = app["appId"]
    object_id = app["id"]

    service_principals = az("ad", "sp", "list", "--filter", f"appId eq '{app_id}'", json_output=True)
    service_principal = ensure_single(service_principals, f"service principal for {app_name}")
    if not service_principal:
        service_principal = az("ad", "sp", "create", "--id", app_id, json_output=True)
        print(f"Created service principal for {environment}.")

    federated = az("ad", "app", "federated-credential", "list", "--id", object_id, json_output=True)
    expected = {"issuer": ISSUER, "subject": subject, "audiences": [AUDIENCE]}
    credential = validate_federated_credentials(federated, expected)
    if not credential:
        payload = {"name": "github-environment", **expected}
        az("ad", "app", "federated-credential", "create", "--id", object_id, "--parameters", json.dumps(payload), json_output=True)
        print(f"Configured GitHub OIDC trust for {environment}.")

    scope = group["id"]
    principal_id = service_principal["id"]
    assignments = az("role", "assignment", "list", "--scope", scope, "--all", "--query", f"[?principalId=='{principal_id}' && roleDefinitionName=='{ROLE}']", json_output=True)
    if not assignments:
        az("role", "assignment", "create", "--assignee-object-id", principal_id, "--assignee-principal-type", "ServicePrincipal", "--role", ROLE, "--scope", scope, json_output=True)
        print(f"Assigned {ROLE} at the {environment} resource-group scope.")
    else:
        print(f"Verified existing {ROLE} assignment at the {environment} resource-group scope.")
    print(f"Bootstrap completed for {environment}. Store the application ID in GitHub environment {environment} as AZURE_CLIENT_ID.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=ENVIRONMENTS, required=True)
    parser.add_argument("--subscription-id", required=True, help="Approved nonproduction subscription; not logged.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag, only prints the planned scope.")
    args = parser.parse_args(argv)
    try:
        bootstrap(args.environment, args.subscription_id, args.apply)
    except AzCommandError as error:
        print(f"Bootstrap failed: {error}", file=sys.stderr)
        return 1
    except (KeyError, RuntimeError) as error:
        print(f"Bootstrap failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
