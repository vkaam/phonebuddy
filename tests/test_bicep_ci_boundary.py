"""Protect the Azure credential boundary in the Bicep validation workflow."""
from pathlib import Path
import unittest


class BicepCiBoundaryTests(unittest.TestCase):
    def test_azure_identity_is_confined_to_manual_main_job(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/ci.yml').read_text()
        quality, trusted = workflow.split('\n  dev-hosting-what-if:\n', 1)
        self.assertNotIn('pull_request_target:', workflow)
        self.assertNotIn('id-token: write', quality)
        self.assertNotIn('azure/login@', quality)
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.preview_dev_hosting", trusted)
        self.assertIn("github.repository == 'vkaam/phonebuddy' && github.ref == 'refs/heads/main'", trusted)
        self.assertIn('needs: quality', trusted)
        self.assertIn('environment: dev', trusted)
        self.assertIn('id-token: write', trusted)
        self.assertIn('persist-credentials: false', trusted)
        self.assertIn('az deployment group what-if', trusted)
        self.assertNotIn('az deployment group create', trusted)
