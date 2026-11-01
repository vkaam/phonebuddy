"""Deployment preflight rejects unresolved or mismatched environment inputs."""
import unittest

from scripts.check_bicep import (
    FOUNDATION_DEPLOYMENT_NAME,
    FOUNDATION_RESOURCE_GROUP_NAME,
    FOUNDATION_RESOURCE_GROUP_OUTPUT,
    deployment_ready,
    validate_foundation_isolation,
)


def params(environment='dev', location='westeurope', owner='team', cost_center='123'):
    return {key: {'value': value} for key, value in {
        'environment': environment, 'location': location,
        'owner': owner, 'costCenter': cost_center,
    }.items()}


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
        }],
        'outputs': {'resourceGroupName': {
            'type': 'string', 'value': FOUNDATION_RESOURCE_GROUP_OUTPUT,
        }},
    }


class FoundationIsolationTests(unittest.TestCase):
    def test_environment_scoped_names_are_distinct(self):
        names = validate_foundation_isolation(foundation_template())
        self.assertEqual(names, {
            'dev': 'rg-pb-dev-foundation',
            'test': 'rg-pb-test-foundation',
            'prod': 'rg-pb-prod-foundation',
        })
        self.assertEqual(len(set(names.values())), 3)

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


if __name__ == '__main__':
    unittest.main()
