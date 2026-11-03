"""Protect the Azure credential boundary in the Bicep validation workflows."""
from pathlib import Path
import unittest

from scripts.check_bicep import validate_what_if


class BicepWhatIfValidationTests(unittest.TestCase):
    def test_only_the_azure_managed_smart_detection_group_may_be_ignored(self):
        safe_result = {
            'status': 'Succeeded',
            'changes': [{
                'changeType': 'Ignore',
                'resourceId': ('/subscriptions/sub/resourceGroups/rg/providers/'
                               'Microsoft.Insights/actionGroups/Application Insights Smart Detection'),
            }],
        }
        self.assertEqual(validate_what_if(safe_result), safe_result['changes'])

        unsafe_result = {
            'status': 'Succeeded',
            'changes': [{
                'changeType': 'Ignore',
                'resourceId': ('/subscriptions/sub/resourceGroups/rg/providers/'
                               'Microsoft.Insights/actionGroups/unreviewed-resource'),
            }],
        }
        with self.assertRaisesRegex(ValueError, 'Only the Azure-managed'):
            validate_what_if(unsafe_result)


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

    def test_health_gate_is_manual_main_only_and_runs_before_annotation(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        workflow = (root / 'azure-health-gate.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertNotIn('pull_request:', workflow)
        self.assertNotIn('pull_request_target:', workflow)
        self.assertIn("github.repository == 'vkaam/phonebuddy' && github.ref == 'refs/heads/main'", workflow)
        self.assertIn('options: [dev, test]', workflow)
        self.assertIn('id-token: write', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertIn('scripts/health_gate.py', workflow)
        self.assertIn('scripts/release_annotation.py', workflow)
        self.assertLess(workflow.index('Run bounded readiness'),
                        workflow.index('Record successful release annotation'))
        self.assertNotIn('az deployment', workflow)
