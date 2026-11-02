"""Guard the trusted OIDC smoke workflow's credential boundary."""

from pathlib import Path
import unittest


class SmokeWorkflowTests(unittest.TestCase):
    def test_manual_main_only_environment_job_without_deployment_writes(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/azure-oidc-smoke.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertNotIn('pull_request:', workflow)
        self.assertNotIn('pull_request_target:', workflow)
        self.assertIn("github.repository == 'vkaam/phonebuddy' && github.ref == 'refs/heads/main'", workflow)
        self.assertIn('environment: ${{ inputs.environment }}', workflow)
        self.assertIn('id-token: write', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertIn('for environment in dev test', workflow)
        self.assertIn('az group show', workflow)
        self.assertNotIn('az deployment', workflow)
        self.assertNotIn('secrets: inherit', workflow)
