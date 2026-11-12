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
    APP_DIAGNOSTIC_NAME,
    APP_DIAGNOSTIC_TYPE,
    DATA_PLATFORM_DEPLOYMENT_NAME,
    ENVIRONMENT_DIAGNOSTIC_NAME,
    ENVIRONMENT_DIAGNOSTIC_TYPE,
    FOUNDATION_DEPLOYMENT_NAME,
    FOUNDATION_RESOURCE_GROUP_NAME,
    FOUNDATION_RESOURCE_GROUP_OUTPUT,
    valid_foundation_resource_group_output,
    deployment_ready,
    environment_parameters,
    expected_resource_group_names,
    runtime_sql_admin_overrides,
    validate_foundation_isolation,
    validate_foundry_model_evidence,
    validate_data_platform,
    validate_what_if,
    validate_quality_evidence,
    has_expected_diagnostic_scope,
)
from scripts.azure_foundations_smoke import configured_location


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
    def test_environment_parameters_drive_location(self):
        compiled = {'parametersJson': json.dumps({'parameters': {
            'environment': {'value': 'dev'},
            'location': {'value': 'francecentral'},
        }})}
        with patch('scripts.check_bicep.run', return_value=json.dumps(compiled)) as run:
            values = environment_parameters('dev')
        self.assertEqual(values['location']['value'], 'francecentral')
        run.assert_called_once_with(
            'bicep', 'build-params', 'infra/environments/dev.bicepparam', '--stdout')

    def test_environment_parameters_reject_mismatched_file(self):
        compiled = {'parametersJson': json.dumps({'parameters': {
            'environment': {'value': 'test'},
            'location': {'value': 'francecentral'},
        }})}
        with patch('scripts.check_bicep.run', return_value=json.dumps(compiled)):
            with self.assertRaisesRegex(ValueError, 'selects a different environment'):
                environment_parameters('dev')


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


class SmokeLocationTests(unittest.TestCase):
    def test_location_is_read_from_environment_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            parameter_dir = Path(tmp) / 'infra' / 'environments'
            parameter_dir.mkdir(parents=True)
            (parameter_dir / 'dev.bicepparam').write_text(
                "using '../main.bicep'\nparam environment = 'dev'\n"
                "param location = 'francecentral'\n", encoding='utf-8')
            with patch('scripts.azure_foundations_smoke.ROOT', Path(tmp)):
                self.assertEqual(configured_location('dev'), 'francecentral')

    def test_unresolved_location_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            parameter_dir = Path(tmp) / 'infra' / 'environments'
            parameter_dir.mkdir(parents=True)
            (parameter_dir / 'dev.bicepparam').write_text(
                "param location = 'UNRESOLVED'\n", encoding='utf-8')
            with patch('scripts.azure_foundations_smoke.ROOT', Path(tmp)):
                with self.assertRaisesRegex(RuntimeError, 'Could not resolve'):
                    configured_location('dev')


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
        {'type': 'Microsoft.Sql/servers', 'properties': {
            'administrators': {'administratorType': 'ActiveDirectory',
                               'principalType': 'User',
                               'azureADOnlyAuthentication': True,
                               'login': 'admin', 'sid': 'object-id',
                               'tenantId': 'tenant-id'}}},
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
        {'type': 'Microsoft.CognitiveServices/accounts/deployments',
         'dependsOn': ["[resourceId('Microsoft.CognitiveServices/accounts/projects', 'foundry', 'phonebuddy-dev')]"],
         'sku': {'name': 'GlobalStandard'},
         'properties': {'model': {'name': 'gpt-5-mini', 'version': '2025-08-07'},
                        'versionUpgradeOption': 'NoAutoUpgrade'}},
        {'type': 'Microsoft.Authorization/roleAssignments'},
        {'type': 'Microsoft.ServiceBus/namespaces/queues', 'properties': {
            'deadLetteringOnMessageExpiration': True, 'maxDeliveryCount': 3}},
    ]}


class DataPlatformTemplateTests(unittest.TestCase):
    def test_required_secure_data_platform_resources_pass(self):
        self.assertTrue(validate_data_platform(data_platform_template()))

    def test_sql_server_requires_inline_entra_only_admin(self):
        for change in (
            lambda props: props.pop('administrators'),
            lambda props: props['administrators'].__setitem__('azureADOnlyAuthentication', False),
            lambda props: props.__setitem__('administratorLogin', 'sqladmin'),
        ):
            template = data_platform_template()
            change(template['resources'][0]['properties'])
            with self.assertRaisesRegex(ValueError, 'Entra-only administrator'):
                validate_data_platform(template)

    def test_foundry_model_waits_for_project_resource(self):
        template = data_platform_template()
        template['resources'][12].pop('dependsOn')
        with self.assertRaisesRegex(ValueError, 'must wait for its project'):
            validate_data_platform(template)

    def test_storage_keys_public_blobs_and_nonregional_fallback_fail(self):
        for mutate, message in (
            (lambda t: t['resources'][3]['properties'].__setitem__('allowSharedKeyAccess', True), 'Shared Key'),
            (lambda t: t['resources'][7]['properties'].__setitem__('deadLetteringOnMessageExpiration', False), 'dead-letter'),
            (lambda t: t['resources'][-1]['properties'].__setitem__('maxDeliveryCount', 0), 'dead-letter'),
            (lambda t: t['resources'][12]['properties'].__setitem__('spilloverDeploymentName', 'fallback'), 'model version'),
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
    def test_foundation_output_accepts_compiler_api_versions_and_rejects_other_references(self):
        compiler_outputs = (
            FOUNDATION_RESOURCE_GROUP_OUTPUT,
            FOUNDATION_RESOURCE_GROUP_OUTPUT.replace("2022-09-01", "2025-04-01"),
        )
        for output in compiler_outputs:
            with self.subTest(output=output):
                self.assertTrue(valid_foundation_resource_group_output(output))
                template = foundation_template()
                template['outputs']['resourceGroupName']['value'] = output
                validate_foundation_isolation(template)

        unsafe_outputs = (
            FOUNDATION_RESOURCE_GROUP_OUTPUT.replace("2022-09-01", "latest"),
            FOUNDATION_RESOURCE_GROUP_OUTPUT.replace("phonebuddy-{0}-{1}-foundation", "other-{0}-{1}-deployment"),
            "[reference('untrusted').outputs.resourceGroupName.value]",
        )
        for output in unsafe_outputs:
            with self.subTest(output=output):
                self.assertFalse(valid_foundation_resource_group_output(output))
                template = foundation_template()
                template['outputs']['resourceGroupName']['value'] = output
                with self.assertRaisesRegex(ValueError, 'environment resource-group name'):
                    validate_foundation_isolation(template)

    def test_environment_scoped_names_are_distinct(self):
        validate_foundation_isolation(foundation_template())
        names = expected_resource_group_names({
            'dev': 'francecentral',
            'test': 'francecentral',
            'prod': 'unresolved',
        })
        self.assertEqual(names, {
            'dev': 'rg-pb-dev-francecentral-foundation',
            'test': 'rg-pb-test-francecentral-foundation',
            'prod': 'rg-pb-prod-unresolved-foundation',
        })
        self.assertEqual(len(set(names.values())), 3)

    def test_diagnostic_scopes_match_exact_compiled_resource_ids(self):
        cases = (
            (ENVIRONMENT_DIAGNOSTIC_TYPE, ENVIRONMENT_DIAGNOSTIC_NAME,
             "[resourceId('Microsoft.App/managedEnvironments', "
             "format('cae-pb-{0}', parameters('environment')))]",
             "[format('{0}/providers/Microsoft.App/managedEnvironments/{1}', "
             "resourceGroup().id, format('cae-pb-{0}', parameters('environment')))]",
             "[format('Microsoft.App/managedEnvironments/{0}', "
             "format('cae-pb-{0}', parameters('environment')))]",
             "[format('{0}/providers/Microsoft.App/managedEnvironments/{1}', "
             "resourceGroup().id, 'wrong-target', format('cae-pb-{0}', parameters('environment')))]",
             "[format('Microsoft.App/managedEnvironments/{0}', 'wrong-target', "
             "format('cae-pb-{0}', parameters('environment')))]",
             "[resourceId('Microsoft.App/managedEnvironmentsFake', "
             "format('cae-pb-{0}', parameters('environment')))]",
             "[resourceId('Microsoft.App/managedEnvironments', "
             "format('cae-other-{0}', parameters('environment')))]"),
            (APP_DIAGNOSTIC_TYPE, APP_DIAGNOSTIC_NAME,
             "[resourceId('Microsoft.App/containerApps', "
             "format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[format('{0}/providers/Microsoft.App/containerApps/{1}', "
             "resourceGroup().id, format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[format('Microsoft.App/containerApps/{0}', "
             "format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[format('{0}/providers/Microsoft.App/containerApps/{1}', "
             "resourceGroup().id, 'wrong-target', format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[format('Microsoft.App/containerApps/{0}', 'wrong-target', "
             "format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[resourceId('Microsoft.App/containerAppsFake', "
             "format('ca-pb-{0}-release-test', parameters('environment')))]",
             "[resourceId('Microsoft.App/containerApps', "
             "format('ca-pb-{0}-other', parameters('environment')))]"),
        )
        for (resource_type, resource_name, resource_id_form, full_path_form,
             legacy_type_path_form, wrong_extra_argument, wrong_legacy_extra_argument,
             wrong_type, wrong_target) in cases:
            with self.subTest(resource_type=resource_type):
                for scope in (resource_id_form, full_path_form, legacy_type_path_form):
                    self.assertTrue(has_expected_diagnostic_scope(
                        {'scope': scope}, resource_type, resource_name))
                self.assertFalse(has_expected_diagnostic_scope(
                    {'scope': wrong_type}, resource_type, resource_name))
                self.assertFalse(has_expected_diagnostic_scope(
                    {'scope': wrong_target}, resource_type, resource_name))
                self.assertFalse(has_expected_diagnostic_scope(
                    {'scope': wrong_extra_argument}, resource_type, resource_name))
                self.assertFalse(has_expected_diagnostic_scope(
                    {'scope': wrong_legacy_extra_argument}, resource_type, resource_name))
                self.assertFalse(has_expected_diagnostic_scope(
                    {'scope': 42}, resource_type, resource_name))

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

    def test_known_conditional_workload_ignores_are_accepted(self):
        resource_ids = []
        for environment in ('dev', 'test'):
            base = (f'/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/'
                    f'resourceGroups/rg-pb-{environment}-westeurope-foundation/providers/')
            resource_ids.append(base + f'Microsoft.App/containerApps/ca-pb-{environment}-release-test')
            resource_ids.extend(base + f'Microsoft.Insights/scheduledQueryRules/alert-pb-{environment}-{name}'
                                for name in ('health-latency', 'missing-health-telemetry',
                                             'unhealthy-health-response'))

        changes = [{'changeType': 'Ignore', 'resourceId': resource_id}
                   for resource_id in resource_ids]
        self.assertEqual(validate_what_if({'status': 'Succeeded', 'changes': changes}), changes)

    def test_conditional_workload_ignore_allowlist_is_exact_and_scoped(self):
        resource_ids = (
            '/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/resourceGroups/rg-pb-dev-westeurope-foundation/providers/Microsoft.App/containerApps/ca-pb-dev-other',
            '/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/resourceGroups/rg-pb-prod-westeurope-foundation/providers/Microsoft.App/containerApps/ca-pb-prod-release-test',
            '/subscriptions/not-a-guid/resourceGroups/rg-pb-dev-westeurope-foundation/providers/Microsoft.App/containerApps/ca-pb-dev-release-test',
            '/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/resourceGroups/rg-other/providers/Microsoft.Insights/scheduledQueryRules/alert-pb-dev-health-latency',
            '/subscriptions/3787e2b4-802f-4b28-8793-1a32cc410b45/resourceGroups/rg-pb-dev-westeurope-foundation/providers/Microsoft.Insights/scheduledQueryRules/alert-pb-dev-other',
        )
        for resource_id in resource_ids:
            with self.subTest(resource_id=resource_id):
                result = {'status': 'Succeeded', 'changes': [
                    {'changeType': 'Ignore', 'resourceId': resource_id},
                ]}
                with self.assertRaisesRegex(ValueError, 'Unexpected ignored resource'):
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
