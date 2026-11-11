"""Protect the Azure credential boundary in the Bicep validation workflows."""
from pathlib import Path
import unittest

from scripts.check_bicep import validate_what_if


class BicepWhatIfValidationTests(unittest.TestCase):
    def test_existing_france_data_foundations_are_known_hosting_preview_ignores(self):
        prefix = ('/subscriptions/43c19721-4a1d-49ed-954b-5e8a29b346b1/'
                  'resourceGroups/rg-pb-dev-francecentral-foundation/providers/')
        allowed = [
            'Microsoft.CognitiveServices/accounts/cs-pb-dev-3dg66adbcqbhw-foundry',
            'Microsoft.CognitiveServices/accounts/cs-pb-dev-3dg66adbcqbhw-foundry/projects/phonebuddy-dev',
            'Microsoft.ManagedIdentity/userAssignedIdentities/id-pb-dev-data',
            'Microsoft.Sql/servers/sql-pb-dev-3dg66adbcqbhw/databases/phonebuddy',
            'Microsoft.Storage/storageAccounts/pbdev3dg66adbcqbhw',
        ]
        result = {'status': 'Succeeded', 'changes': [
            {'changeType': 'Ignore', 'resourceId': prefix + resource}
            for resource in allowed
        ]}
        self.assertEqual(validate_what_if(result), result['changes'])
        scope = prefix.removesuffix('/providers/')
        self.assertEqual(validate_what_if(result, scope), result['changes'])
        for other_scope in (
                prefix.replace('rg-pb-dev-', 'rg-pb-test-'),
                prefix.replace('43c19721-4a1d-49ed-954b-5e8a29b346b1',
                               '00000000-0000-0000-0000-000000000000')):
            outside = {'status': 'Succeeded', 'changes': [{
                'changeType': 'Ignore',
                'resourceId': other_scope +
                'Microsoft.ManagedIdentity/userAssignedIdentities/id-pb-test-data',
            }]}
            with self.assertRaisesRegex(ValueError, 'outside the reviewed'):
                validate_what_if(outside, scope)
        result['changes'].append({'changeType': 'Ignore', 'resourceId':
                                  prefix + 'Microsoft.Storage/storageAccounts/unreviewed'})
        with self.assertRaisesRegex(ValueError, 'Unexpected ignored resource'):
            validate_what_if(result)

    def test_smart_detection_and_known_conditional_workload_resources_may_be_ignored(self):
        safe_result = {
            'status': 'Succeeded',
            'changes': [{
                'changeType': 'Ignore',
                'resourceId': ('/subscriptions/sub/resourceGroups/rg/providers/'
                               'Microsoft.Insights/actionGroups/Application Insights Smart Detection'),
            }, {
                'changeType': 'Ignore',
                'resourceId': ('/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/'
                               'resourceGroups/rg-pb-dev-westeurope-foundation/providers/'
                               'Microsoft.App/containerApps/ca-pb-dev-release-test'),
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
        with self.assertRaisesRegex(ValueError, 'Unexpected ignored resource'):
            validate_what_if(unsafe_result)


class BicepCiBoundaryTests(unittest.TestCase):
    def test_azure_identity_is_confined_to_trusted_main_workflows(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        quality = (root / 'ci.yml').read_text()
        trusted = (root / 'azure-hosting-what-if.yml').read_text()
        deployment = (root / 'azure-deploy.yml').read_text()
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
        self.assertIn('--validation-level ProviderNoRbac', trusted)
        self.assertIn('rg-pb-dev-francecentral-foundation', trusted)
        self.assertIn('deployStaticSite=false', trusted)
        self.assertIn('--expected-scope', trusted)
        self.assertNotIn('az deployment group create', trusted)
        self.assertIn("github.event_name == 'push' && github.ref == 'refs/heads/main'", quality)
        self.assertIn('needs: quality', quality)
        self.assertIn('docker buildx build', quality)
        self.assertIn('actions/upload-artifact@', quality)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", quality)
        self.assertIn('Image publication is not applicable outside main pushes', quality)
        self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/main'", quality)
        self.assertNotIn('pull_request:', deployment)
        self.assertIn('workflow_run:', deployment)
        self.assertIn('branches: [main]', deployment)
        self.assertIn("github.event.workflow_run.event == 'push'", deployment)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", deployment)
        self.assertIn('github.event.workflow_run.head_sha', deployment)
        self.assertIn('scripts/deployment_policy.py verify-current-source', deployment)
        self.assertIn('actions/download-artifact@', deployment)
        self.assertIn('run-id: ${{ github.event.workflow_run.id }}', deployment)
        self.assertIn('environment: dev', deployment)
        self.assertIn('id-token: write', deployment)
        self.assertIn('cancel-in-progress: false', deployment)
        self.assertIn("contains(@, 'release-test')", deployment)
        self.assertLess(deployment.index('repository_exists='),
                        deployment.index('existing_tag='))
        self.assertIn('managePullRoleAssignment=false', deployment)
        self.assertIn('az deployment group create', deployment)
        self.assertIn('az containerapp revision deactivate', deployment)
        self.assertIn('$GITHUB_WORKSPACE/scripts/deployment_policy.py" verify-manifest', deployment)
        self.assertIn('scripts/deployment_policy.py verify-existing-image', deployment)
        self.assertIn('scripts/deployment_policy.py recovery-required', deployment)
        self.assertIn('scripts/deployment_policy.py candidate-revisions', deployment)
        self.assertIn("steps.recovery-decision.outputs.required == 'true'", deployment)
        self.assertIn('id: observe', deployment)
        self.assertIn('No active candidate revision matched', deployment)
        self.assertLess(deployment.index('Preview the exact Bicep release'),
                        deployment.index('Apply the reviewed Bicep release'))
        self.assertLess(deployment.index('Observe the deployed version'),
                        deployment.index('Record successful release annotation'))

    def test_health_gate_is_manual_main_only_and_runs_before_annotation(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        workflow = (root / 'azure-health-gate.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertNotIn('pull_request:', workflow)
        self.assertNotIn('pull_request_target:', workflow)
        self.assertIn("github.repository == 'vkaam/phonebuddy' && github.ref == 'refs/heads/main'", workflow)
        self.assertIn('options: [dev]', workflow)
        self.assertIn('id-token: write', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertIn('scripts/health_gate.py', workflow)
        self.assertIn('rg-pb-${TARGET_ENVIRONMENT}-francecentral-foundation', workflow)
        self.assertIn('scripts/release_annotation.py', workflow)
        self.assertIn('--workspace-id', workflow)
        self.assertIn('--app-name', workflow)
        self.assertLess(workflow.index('Run bounded readiness'),
                        workflow.index('Record successful release annotation'))
        self.assertNotIn('az deployment', workflow)

    def test_hosting_pull_role_assignment_can_be_prebootstrapped(self):
        source = (Path(__file__).resolve().parents[1] / 'infra/hosting.bicep').read_text()
        self.assertIn('param managePullRoleAssignment bool = true', source)
        self.assertIn("if (managePullRoleAssignment)", source)
        self.assertIn('dependsOn: managePullRoleAssignment ? [pull] : []', source)
