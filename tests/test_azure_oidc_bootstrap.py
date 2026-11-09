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

    def test_federation_requires_only_the_matching_environment_trust(self):
        trusted = [{"issuer": bootstrap.ISSUER,
                    "subject": f"repo:vkaam@25612385/phonebuddy@1437973251:environment:{env}",
                    "audiences": [bootstrap.AUDIENCE]} for env in ("dev", "test")]
        for env, own, other in (("dev", trusted[0], trusted[1]),
                                ("test", trusted[1], trusted[0])):
            bootstrap.validate_federated_credentials([own], env)
            for invalid in ([], [other], [own, other],
                            [{**own, "issuer": "https://wrong.example"}],
                            [{**own, "audiences": ["wrong"]}]):
                with self.subTest(env=env, invalid=invalid), self.assertRaisesRegex(RuntimeError, "exactly the approved"):
                    bootstrap.validate_federated_credentials(invalid, env)

    def test_apply_requires_explicit_environment_app_before_azure_changes(self):
        with patch.object(bootstrap, "az") as az:
            with self.assertRaisesRegex(RuntimeError, "explicit environment application ID"):
                bootstrap.bootstrap("dev", "subscription-id", apply=True)
        az.assert_not_called()

    def test_unexpected_trust_blocks_role_assignment(self):
        responses = [None, [{"id": "/group"}], {"id": "app-object"},
                     {"id": "principal-object"}, [{"subject": "unexpected"}]]
        with patch.object(bootstrap, "az", side_effect=responses) as az:
            with self.assertRaisesRegex(RuntimeError, "approved dev"):
                bootstrap.bootstrap("dev", "subscription-id", apply=True, app_id="app-id")
        self.assertFalse(any(call.args[:3] == ("role", "assignment", "create") for call in az.call_args_list))

    def test_cross_environment_role_blocks_role_assignment(self):
        trust = {"issuer": bootstrap.ISSUER,
                 "subject": "repo:vkaam@25612385/phonebuddy@1437973251:environment:dev",
                 "audiences": [bootstrap.AUDIENCE]}
        responses = [None, [{"id": "/own-group"}], {"id": "app-object"},
                     {"id": "principal-object"}, [trust],
                     [{"scope": "/other-group", "roleDefinitionName": "Contributor"}]]
        with patch.object(bootstrap, "az", side_effect=responses) as az:
            with self.assertRaisesRegex(RuntimeError, "outside its own foundation group"):
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
