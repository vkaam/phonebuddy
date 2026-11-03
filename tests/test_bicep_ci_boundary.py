"""Protect the Azure credential boundary in the Bicep validation workflows."""
from pathlib import Path
import unittest


class BicepCiBoundaryTests(unittest.TestCase):
    def test_azure_identity_is_confined_to_manual_main_workflow(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        quality = (root / 'ci.yml').read_text()
        trusted = (root / 'azure-hosting-what-if.yml').read_text()
        self.assertNotIn('id-token: write', quality)
        self.assertNotIn('azure/login@', quality)
        self.assertIn('workflow_dispatch:', trusted)
        self.assertNotIn('pull_request:', trusted)
        self.assertNotIn('pull_request_target:', trusted)
        self.assertIn("github.repository == 'vkaam/phonebuddy' && github.ref == 'refs/heads/main'", trusted)
        self.assertIn('environment: dev', trusted)
        self.assertIn('id-token: write', trusted)
        self.assertIn('persist-credentials: false', trusted)
        self.assertIn('--quality-evidence', trusted)
        self.assertIn('az deployment group what-if', trusted)
        self.assertNotIn('az deployment group create', trusted)
