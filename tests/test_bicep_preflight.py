"""Deployment preflight rejects unresolved or mismatched environment inputs."""
import unittest
import json
from datetime import date
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from scripts.check_bicep import (
    DATA_PLATFORM_DEPLOYMENT_NAME,
    FOUNDATION_DEPLOYMENT_NAME,
    FOUNDATION_RESOURCE_GROUP_NAME,
    FOUNDATION_RESOURCE_GROUP_OUTPUT,
    deployment_ready,
    expected_resource_group_names,
    runtime_sql_admin_overrides,
    validate_foundation_isolation,
    validate_foundry_model_evidence,
    validate_data_platform,
    validate_what_if,
    validate_quality_evidence,
)


def params(environment='dev', location='westeurope', owner='team', cost_center='123'):
    return {key: {'value': value} for key, value in {
        'environment': environment, 'location': location,
        'owner': owner, 'costCenter': cost_center,
        'sqlAdminObjectId': '00000000-0000-0000-0000-000000000001',
        'sqlAdminLogin': 'phonebuddy-admin',
        'foundryModelName': 'gpt-5-mini',
        'foundryModelVersion': '2025-08-07',
    }.items()}


def foundry_evidence(location='westeurope', lifecycle='GenerallyAvailable', capacity=20,
                     model='gpt-5-mini', version='2025-08-07', sku='GlobalStandard',
                     model_sku='GlobalStandard', model_capacity=1000000, deprecation='2027-01-01T00:00:00Z'):
    return (
        {'value': [{'location': location, 'model': {
            'format': 'OpenAI', 'name': model, 'version': version,
            'lifecycleStatus': lifecycle,
            'deprecation': {'inference': deprecation},
            'skus': [{'name': model_sku, 'deprecationDate': '2027-01-01T00:00:00Z',
                      'capacity': {'default': 10, 'maximum': model_capacity}}],
        }}]},
        {'value': [{'location': location,
                    'properties': {'skuName': sku, 'availableCapacity': capacity}}]},
    )


class DeploymentReadinessTests(unittest.TestCase):
    def test_valid_values_and_environment_pass(self):
        deployment_ready('dev', params())

    def test_mismatched_environment_fails(self):
        with self.assertRaisesRegex(ValueError, 'does not match'):
            deployment_ready('prod', params())

    def test_unresolved_or_blank_fields_fail(self):
        for field in ('location', 'owner', 'costCenter'):
            for value in ('UNRESOLVED', ' unresolved ', ''):
                values = params()
                values[field]['value'] = value
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        deployment_ready('dev', values)

    def test_unresolved_test_and_prod_are_not_deployment_ready(self):
        for environment in ('test', 'prod'):
            values = params(environment, location='UNRESOLVED',
                            owner='UNRESOLVED', cost_center='UNRESOLVED')
            with self.subTest(environment=environment):
                with self.assertRaisesRegex(ValueError, 'must be supplied'):
                    deployment_ready(environment, values)

    def test_unresolved_sql_admin_blocks_deployment(self):
        for field in ('sqlAdminObjectId', 'sqlAdminLogin'):
            values = params()
            values[field]['value'] = 'UNRESOLVED'
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    deployment_ready('dev', values)

    def test_runtime_sql_admin_environment_values_resolve_placeholders(self):
        values = params()
        values['sqlAdminObjectId']['value'] = 'UNRESOLVED'
        values['sqlAdminLogin']['value'] = 'UNRESOLVED'
        with patch.dict('os.environ', {
            'PHONEBUDDY_SQL_ADMIN_OBJECT_ID': '00000000-0000-0000-0000-000000000002',
            'PHONEBUDDY_SQL_ADMIN_LOGIN': 'owner@example.test',
        }, clear=True):
            deployment_ready('dev', values, runtime_sql_admin_overrides())

    def test_partial_runtime_sql_admin_values_fail_closed(self):
        values = params()
        values['sqlAdminObjectId']['value'] = 'UNRESOLVED'
        values['sqlAdminLogin']['value'] = 'UNRESOLVED'
        with patch.dict('os.environ', {
            'PHONEBUDDY_SQL_ADMIN_OBJECT_ID': '00000000-0000-0000-0000-000000000002',
        }, clear=True):
            with self.assertRaisesRegex(ValueError, 'sqlAdminLogin'):
                deployment_ready('dev', values, runtime_sql_admin_overrides())


class FoundryAvailabilityTests(unittest.TestCase):
    def test_exact_location_catalog_and_global_capacity_pass(self):
        models, capacities = foundry_evidence()
        result = validate_foundry_model_evidence(
            models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
            'GlobalStandard', 20, today=date(2026, 11, 3),
        )
        self.assertEqual(result['availableCapacity'], 20)
        self.assertEqual(result['location'], 'westeurope')

    def test_global_capacity_default_is_minimum_when_minimum_is_omitted(self):
        models, capacities = foundry_evidence()
        with self.assertRaisesRegex(ValueError, 'SKU limits'):
            validate_foundry_model_evidence(
                models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
                'GlobalStandard', 5, today=date(2026, 11, 3),
            )

    def test_identical_catalog_entries_by_sku_are_deduplicated(self):
        models, capacities = foundry_evidence()
        models['value'].append(dict(models['value'][0]))
        result = validate_foundry_model_evidence(
            models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
            'GlobalStandard', 20, today=date(2026, 11, 3),
        )
        self.assertEqual(result['model'], 'gpt-5-mini')

    def test_conflicting_duplicate_lifecycle_evidence_fails(self):
        models, capacities = foundry_evidence()
        conflicting = json.loads(json.dumps(models['value'][0]))
        conflicting['model']['lifecycleStatus'] = 'Deprecated'
        models['value'].append(conflicting)
        with self.assertRaisesRegex(ValueError, 'conflicting lifecycle'):
            validate_foundry_model_evidence(
                models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
                'GlobalStandard', 20, today=date(2026, 11, 3),
            )

    def test_does_not_fallback_to_another_geography(self):
        models, capacities = foundry_evidence(location='swedencentral')
        with self.assertRaisesRegex(ValueError, 'no geography fallback'):
            validate_foundry_model_evidence(
                models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
                'GlobalStandard', 20, today=date(2026, 11, 3),
            )

    def test_retired_preview_and_deprecating_models_fail(self):
        for status in ('Preview', 'Deprecating', 'Deprecated'):
            models, capacities = foundry_evidence(lifecycle=status)
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'GenerallyAvailable'):
                validate_foundry_model_evidence(
                    models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
                    'GlobalStandard', 20, today=date(2026, 11, 3),
                )

    def test_missing_model_version_or_insufficient_quota_fails(self):
        for models, capacities in (
            foundry_evidence(model='other-model'),
            foundry_evidence(capacity=1),
            foundry_evidence(sku='DataZoneStandard'),
        ):
            with self.subTest(models=models, capacities=capacities), self.assertRaises(ValueError):
                validate_foundry_model_evidence(
                    models, capacities, 'westeurope', 'gpt-5-mini', '2025-08-07',
                    'GlobalStandard', 20, today=date(2026, 11, 3),
                )


def data_platform_template():
    return {'resources': [
        {'type': 'Microsoft.Sql/servers'},
        {'type': 'Microsoft.Sql/servers/administrators',
         'properties': {'administratorType': 'ActiveDirectory'}},
        {'type': 'Microsoft.Sql/servers/databases'},
        {'type': 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies'},
        {'type': 'Microsoft.Storage/storageAccounts', 'properties': {
            'allowBlobPublicAccess': False, 'allowSharedKeyAccess': False,
            'supportsHttpsTrafficOnly': True}},
        {'type': 'Microsoft.Storage/storageAccounts/blobServices', 'properties': {
            'deleteRetentionPolicy': {'enabled': True},
            'containerDeleteRetentionPolicy': {'enabled': True}}},
        {'type': 'Microsoft.Storage/storageAccounts/blobServices/containers'},
        {'type': 'Microsoft.ServiceBus/namespaces', 'properties': {'disableLocalAuth': True}},
        {'type': 'Microsoft.ServiceBus/namespaces/queues', 'properties': {
            'deadLetteringOnMessageExpiration': True, 'maxDeliveryCount': 5}},
        {'type': 'Microsoft.ManagedIdentity/userAssignedIdentities'},
        {'type': 'Microsoft.CognitiveServices/accounts', 'kind': 'SpeechServices',
         'properties': {'disableLocalAuth': True}},
        {'type': 'Microsoft.CognitiveServices/accounts', 'kind': 'AIServices',
         'properties': {'disableLocalAuth': True}},
        {'type': 'Microsoft.CognitiveServices/accounts/projects'},
        {'type': 'Microsoft.CognitiveServices/accounts/deployments', 'sku': {'name': 'GlobalStandard'},
         'properties': {'model': {'name': 'gpt-5-mini', 'version': '2025-08-07'},
                        'versionUpgradeOption': 'NoAutoUpgrade'}},
        {'type': 'Microsoft.Authorization/roleAssignments'},
        {'type': 'Microsoft.Sql/servers/azureADOnlyAuthentications',
         'properties': {'azureADOnlyAuthentication': True}},
        {'type': 'Microsoft.ServiceBus/namespaces/queues', 'properties': {
            'deadLetteringOnMessageExpiration': True, 'maxDeliveryCount': 3}},
    ]}


class DataPlatformTemplateTests(unittest.TestCase):
    def test_required_secure_data_platform_resources_pass(self):
        self.assertTrue(validate_data_platform(data_platform_template()))

    def test_storage_keys_public_blobs_and_nonregional_fallback_fail(self):
        for mutate, message in (
            (lambda t: t['resources'][4]['properties'].__setitem__('allowSharedKeyAccess', True), 'Shared Key'),
            (lambda t: t['resources'][8]['properties'].__setitem__('deadLetteringOnMessageExpiration', False), 'dead-letter'),
            (lambda t: t['resources'][-1]['properties'].__setitem__('maxDeliveryCount', 0), 'dead-letter'),
            (lambda t: t['resources'][13]['properties'].__setitem__('spilloverDeploymentName', 'fallback'), 'model version'),
        ):
            template = data_platform_template()
            mutate(template)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_data_platform(template)


def foundation_template(resource_group_name=FOUNDATION_RESOURCE_GROUP_NAME,
                        module_outputs=None):
    return {
        'resources': [{
            'type': 'Microsoft.Resources/deployments',
            'name': FOUNDATION_DEPLOYMENT_NAME,
            'properties': {
                'parameters': {name: {'value': f"[parameters('{name}')]"}
                              for name in ('environment', 'location', 'owner', 'costCenter')},
                'template': {
                    'parameters': {name: {} for name in
                                   ('environment', 'location', 'owner', 'costCenter')},
                    'resources': [{
                        'type': 'Microsoft.Resources/resourceGroups',
                        'name': resource_group_name,
                        'tags': {'environment': "[parameters('environment')]"},
                    }],
                    'outputs': module_outputs or {
                        'resourceGroupName': {'type': 'string',
                                              'value': FOUNDATION_RESOURCE_GROUP_NAME},
                    },
                },
            },
        }, {
            'type': 'Microsoft.Resources/deployments',
            'name': DATA_PLATFORM_DEPLOYMENT_NAME,
            'resourceGroup': (
                "[format('rg-pb-{0}-{1}-foundation', parameters('environment'), "
                "parameters('location'))]"
            ),
            'dependsOn': [
                "[subscriptionResourceId('Microsoft.Resources/deployments', "
                "format('phonebuddy-{0}-{1}-foundation', parameters('environment'), "
                "parameters('location')))]",
            ],
            'properties': {'parameters': {
                name: {} for name in (
                    'environment', 'location', 'owner', 'costCenter',
                    'sqlAdminObjectId', 'sqlAdminLogin', 'foundryModelName',
                    'foundryModelVersion', 'foundryModelCapacity',
                )
            }},
        }],
        'outputs': {'resourceGroupName': {
            'type': 'string', 'value': FOUNDATION_RESOURCE_GROUP_OUTPUT,
        }},
    }


class FoundationIsolationTests(unittest.TestCase):
    def test_environment_scoped_names_are_distinct(self):
        validate_foundation_isolation(foundation_template())
        names = expected_resource_group_names({
            'dev': 'westeurope',
            'test': 'westeurope',
            'prod': 'unresolved',
        })
        self.assertEqual(names, {
            'dev': 'rg-pb-dev-westeurope-foundation',
            'test': 'rg-pb-test-westeurope-foundation',
            'prod': 'rg-pb-prod-unresolved-foundation',
        })
        self.assertEqual(len(set(names.values())), 3)

    def test_regionless_or_fixed_resource_group_name_fails(self):
        for name in ('rg-pb-dev-foundation', 'rg-pb-test-westeurope-foundation'):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'resource group name'):
                    validate_foundation_isolation(foundation_template(name))

    def test_module_must_receive_selected_environment(self):
        template = foundation_template()
        template['resources'][0]['properties']['parameters']['environment'] = {
            'value': 'dev',
        }
        with self.assertRaisesRegex(ValueError, 'forward the selected environment'):
            validate_foundation_isolation(template)

    def test_fixed_resource_group_name_fails(self):
        with self.assertRaisesRegex(ValueError, 'resource group name'):
            validate_foundation_isolation(foundation_template('rg-pb-foundation'))

    def test_secret_or_unrelated_output_fails(self):
        outputs = {
            'resourceGroupName': {'type': 'string',
                                  'value': FOUNDATION_RESOURCE_GROUP_NAME},
            'connectionString': {'type': 'string', 'value': 'secret'},
        }
        with self.assertRaisesRegex(ValueError, 'outputs may expose only'):
            validate_foundation_isolation(foundation_template(module_outputs=outputs))

        template = foundation_template()
        template['outputs']['credential'] = {'type': 'string', 'value': 'secret'}
        with self.assertRaisesRegex(ValueError, 'outputs may expose only'):
            validate_foundation_isolation(template)

    def test_secret_input_fails(self):
        template = foundation_template()
        nested = template['resources'][0]['properties']['template']
        nested['parameters']['adminPassword'] = {}
        with self.assertRaisesRegex(ValueError, 'must not contain secrets'):
            validate_foundation_isolation(template)

    def test_resource_group_must_include_its_environment_tag(self):
        template = foundation_template()
        template['resources'][0]['properties']['template']['resources'][0]['tags'] = {
            'environment': 'dev',
        }
        with self.assertRaisesRegex(ValueError, 'tagged with its environment'):
            validate_foundation_isolation(template)


class WhatIfEvidenceTests(unittest.TestCase):
    def test_complete_results_are_accepted(self):
        changes = [{'changeType': 'Create', 'resourceId': '/subscriptions/example/resourceGroups/dev'}]
        self.assertEqual(validate_what_if({'status': 'Succeeded', 'changes': changes}), changes)

    def test_cli_rejects_missing_results_without_running_bicep(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'what-if.json'
            path.write_text(json.dumps({'status': 'Succeeded', 'changes': []}))
            result = subprocess.run(
                [sys.executable, '-B', str(root / 'scripts/check_bicep.py'),
                 '--what-if-result', str(path)], capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Missing what-if changes', result.stderr)

    def test_missing_uncertain_or_unexpected_results_fail(self):
        for result in (None, {}, {'status': 'Failed'}, {'status': 'Succeeded', 'changes': []},
                       {'status': 'Succeeded', 'changes': [{'changeType': 'Ignore', 'resourceId': '/x'}]},
                       {'status': 'Succeeded', 'changes': [{'changeType': 'Unsupported', 'resourceId': '/x'}]},
                       {'status': 'Succeeded', 'changes': [{'changeType': 'Create'}]},
                       {'status': 'Succeeded', 'changes': [{'changeType': 'Create', 'resourceId': '/x'}], 'potentialChanges': [{'resourceId': '/y'}]}):
            with self.subTest(result=result):
                with self.assertRaises(ValueError):
                    validate_what_if(result)


class QualityEvidenceTests(unittest.TestCase):
    def test_exact_commit_latest_check_must_pass(self):
        run = {'id': 1, 'name': 'Quality', 'head_sha': 'abc',
               'app': {'slug': 'github-actions'}, 'status': 'completed', 'conclusion': 'success'}
        validate_quality_evidence([{'check_runs': [run]}], 'abc')
        for pages, sha in (([], 'abc'), ([{'check_runs': [run]}], 'other'),
                           ([{'check_runs': [run, dict(run, id=2, status='in_progress', conclusion=None)]}], 'abc'),
                           ([{'check_runs': [dict(run, conclusion='skipped')]}], 'abc'),
                           ([{'check_runs': [dict(run, app={'slug': 'other'})]}], 'abc')):
            with self.subTest(pages=pages, sha=sha):
                with self.assertRaises(ValueError):
                    validate_quality_evidence(pages, sha)


if __name__ == '__main__':
    unittest.main()
