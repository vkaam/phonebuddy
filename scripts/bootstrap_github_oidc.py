"""Assign scoped Azure access to a reviewed environment GitHub OIDC principal.

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
REGION = "belgiumcentral"
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


def validate_federated_credentials(credentials, environment):
    """Require only this environment's repository-ID-qualified trust."""
    subject = f"repo:vkaam@25612385/phonebuddy@1437973251:environment:{environment}"
    if (len(credentials) != 1 or credentials[0].get("subject") != subject or
            any(c.get("issuer") != ISSUER or c.get("audiences") != [AUDIENCE] for c in credentials)):
        raise RuntimeError(f"Expected exactly the approved {environment} GitHub federation trust; review the registration before granting access.")


def bootstrap(environment, subscription_id, apply, app_id=None):
    resource_group = f"rg-pb-{environment}-{REGION}-foundation"
    print(f"Environment: {environment}; resource group: {resource_group}; role: {ROLE}")
    if not apply:
        print("Dry run only. Re-run with --apply and the reviewed environment application ID.")
        return
    if not app_id:
        raise RuntimeError("An explicit environment application ID is required.")
    az("account", "set", "--subscription", subscription_id)
    groups = az("group", "list", "--query", f"[?name=='{resource_group}']", json_output=True)
    group = ensure_single(groups, f"resource group named {resource_group}")
    if not group:
        raise RuntimeError(f"Required resource group {resource_group} does not exist in the selected subscription.")
    app = az("ad", "app", "show", "--id", app_id, json_output=True)
    service_principal = az("ad", "sp", "show", "--id", app_id, json_output=True)
    federated = az("ad", "app", "federated-credential", "list", "--id", app["id"], json_output=True)
    validate_federated_credentials(federated, environment)
    scope = group["id"]
    principal_id = service_principal["id"]
    assignments = az("role", "assignment", "list", "--assignee", app_id,
                     "--all", "--include-inherited", json_output=True)
    if any(a.get("scope", "").lower() != scope.lower() or
           a.get("roleDefinitionName") != ROLE for a in assignments):
        raise RuntimeError("The application has access outside its own foundation group or an unexpected role; review RBAC before granting access.")
    if not assignments:
        az("role", "assignment", "create", "--assignee-object-id", principal_id, "--assignee-principal-type", "ServicePrincipal", "--role", ROLE, "--scope", scope, json_output=True)
        print(f"Assigned {ROLE} at the {environment} resource-group scope.")
    else:
        print(f"Verified existing {ROLE} assignment at the {environment} resource-group scope.")
    print(f"The {environment} identity is scoped to its own foundation group.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=ENVIRONMENTS, required=True)
    parser.add_argument("--subscription-id", required=True, help="Approved nonproduction subscription; not logged.")
    parser.add_argument("--app-id", help="Reviewed environment application ID; not logged.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag, only prints the planned scope.")
    args = parser.parse_args(argv)
    try:
        bootstrap(args.environment, args.subscription_id, args.apply, args.app_id)
    except AzCommandError as error:
        print(f"Bootstrap failed: {error}", file=sys.stderr)
        return 1
    except (KeyError, RuntimeError) as error:
        print(f"Bootstrap failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
