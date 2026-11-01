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

    def test_federation_validation_rejects_unexpected_or_multiple_trusts(self):
        expected = {
            "issuer": bootstrap.ISSUER,
            "subject": "repo:vkaam/phonebuddy:environment:dev",
            "audiences": [bootstrap.AUDIENCE],
        }
        correct = {"name": "github-environment", **expected}
        self.assertIsNone(bootstrap.validate_federated_credentials([], expected))
        self.assertEqual(bootstrap.validate_federated_credentials([correct], expected), correct)
        with self.assertRaisesRegex(RuntimeError, "unexpected federated credential"):
            bootstrap.validate_federated_credentials([{"name": "other-trust", **expected}], expected)
        with self.assertRaisesRegex(RuntimeError, "multiple federated credentials"):
            bootstrap.validate_federated_credentials([correct, correct], expected)

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
        self.assertIn("AuthorizationFailed", workflow)


if __name__ == "__main__":
    unittest.main()
