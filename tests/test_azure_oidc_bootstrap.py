import sys
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap_github_oidc as bootstrap  # noqa: E402


class AzureOidcBootstrapTests(unittest.TestCase):
    def test_dry_run_never_calls_azure(self):
        with patch.object(bootstrap, "az") as az:
            bootstrap.bootstrap("dev", "subscription-id", apply=False)
        az.assert_not_called()

    def test_only_approved_nonproduction_environments_are_available(self):
        self.assertEqual(bootstrap.ENVIRONMENTS, ("dev", "test"))
        self.assertEqual(bootstrap.ROLE, "Contributor")
        self.assertEqual(bootstrap.ISSUER, "https://token.actions.githubusercontent.com")

    def test_duplicate_application_matches_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "More than one Azure"):
            bootstrap.ensure_single([{}, {}], "application")

    def test_federation_requires_exactly_both_approved_trusts(self):
        trusted = [{"issuer": bootstrap.ISSUER,
                    "subject": f"repo:vkaam@25612385/phonebuddy@1437973251:environment:{env}",
                    "audiences": [bootstrap.AUDIENCE]} for env in ("dev", "test")]
        bootstrap.validate_federated_credentials(trusted)
        for invalid in (trusted[:1], trusted + [trusted[0]],
                        [trusted[0], {**trusted[1], "subject": "repo:other/project:environment:test"}]):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(RuntimeError, "exactly the approved"):
                bootstrap.validate_federated_credentials(invalid)

    def test_apply_requires_explicit_shared_app_before_azure_changes(self):
        with patch.object(bootstrap, "az") as az:
            with self.assertRaisesRegex(RuntimeError, "explicit shared application ID"):
                bootstrap.bootstrap("dev", "subscription-id", apply=True)
        az.assert_not_called()

    def test_unexpected_trust_blocks_role_assignment(self):
        responses = [None, [{"id": "/group"}], {"id": "app-object"},
                     {"id": "principal-object"}, [{"subject": "unexpected"}]]
        with patch.object(bootstrap, "az", side_effect=responses) as az:
            with self.assertRaisesRegex(RuntimeError, "approved dev and test"):
                bootstrap.bootstrap("dev", "subscription-id", apply=True, app_id="app-id")
        self.assertFalse(any(call.args[:3] == ("role", "assignment", "create") for call in az.call_args_list))

    def test_azure_cli_errors_do_not_retain_command_arguments(self):
        subscription_id = "subscription-id-that-must-not-leak"
        failure = subprocess.CalledProcessError(1, ["az", "account", "set", "--subscription", subscription_id])
        with patch.object(bootstrap.subprocess, "run", side_effect=failure):
            with self.assertRaises(bootstrap.AzCommandError) as raised:
                bootstrap.az("account", "set", "--subscription", subscription_id)
        self.assertNotIn(subscription_id, str(raised.exception))
        self.assertIn("exit status 1", str(raised.exception))

    def test_workflow_is_main_only_environment_scoped_and_has_no_pr_trigger(self):
        workflow = (ROOT / ".github/workflows/azure-oidc-smoke.yml").read_text()
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("environment: ${{ inputs.environment }}", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("for environment in dev test", workflow)
        self.assertNotIn("az deployment group create", workflow)


if __name__ == "__main__":
    unittest.main()
