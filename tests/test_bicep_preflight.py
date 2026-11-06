"""Deployment preflight rejects unresolved or mismatched environment inputs."""
import unittest
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from scripts.check_bicep import (
    FOUNDATION_DEPLOYMENT_NAME,
    FOUNDATION_RESOURCE_GROUP_NAME,
    FOUNDATION_RESOURCE_GROUP_OUTPUT,
    deployment_ready,
    expected_resource_group_names,
    validate_foundation_isolation,
    validate_media,
    validate_what_if,
    validate_quality_evidence,
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


def media_template():
    ports = (
        ('Tcp', '443'), ('Udp', '3478'), ('Tcp', '3478'),
        ('Tcp', '5349'), ('Udp', '5349'), ('Udp', '10000-20000'), ('Tcp', '22'),
    )
    return {
        'parameters': {
            'deployMedia': {'defaultValue': False},
            'imageGalleryName': {},
            'imageGalleryResourceGroup': {},
            'gatewayImageName': {},
            'gatewayImageVersion': {},
            'releaseVersion': {},
        },
        'resources': [
            {'type': 'Microsoft.Network/virtualNetworks', 'properties': {}},
            {'type': 'Microsoft.Network/networkSecurityGroups', 'properties': {
                'securityRules': [
                    {'properties': {'direction': 'Inbound', 'protocol': protocol,
                                   'destinationPortRange': port,
                                   'sourceAddressPrefix': ('10.65.0.64/26' if port == '22'
                                                           else 'Internet')}}
                    for protocol, port in ports
                ] + [
                    {'properties': {'direction': 'Outbound', 'access': access,
                                   'protocol': protocol, 'destinationPortRange': port,
                                   'destinationAddressPrefix': destination, 'priority': priority}}
                    for access, protocol, port, destination, priority in (
                        ('Allow', 'Udp', '53', 'Internet', 200),
                        ('Allow', 'Udp', '53', 'AzurePlatformDNS', 205),
                        ('Allow', 'Udp', '123', 'Internet', 210),
                        ('Allow', 'Udp', '123', 'AzurePlatformTime', 215),
                        ('Allow', 'Tcp', '443', 'Internet', 220),
                        ('Allow', 'Tcp', '5061', 'Internet', 230),
                        ('Allow', 'Udp', '10000-20000', 'Internet', 240),
                        ('Deny', '*', '*', 'Internet', 4096),
                    )
                ],
            }},
            {'type': 'Microsoft.Network/publicIPAddresses', 'properties': {
                'publicIPAllocationMethod': 'Static', 'publicIPAddressVersion': 'IPv4',
            }},
            {'type': 'Microsoft.Network/networkInterfaces', 'properties': {
                'ipConfigurations': [{'properties': {
                    'privateIPAllocationMethod': 'Static',
                    'publicIPAddress': {'id': '/public-ip'},
                }}],
            }},
            {'type': 'Microsoft.Network/bastionHosts', 'properties': {
                'ipConfigurations': [{'name': 'configuration'}],
            }},
            {'type': 'Microsoft.Compute/virtualMachines', 'properties': {
                'storageProfile': {'imageReference': {
                    'id': "[resourceId(parameters('imageGalleryResourceGroup'), 'Microsoft.Compute/galleries/images/versions', parameters('imageGalleryName'), parameters('gatewayImageName'), parameters('gatewayImageVersion'))]",
                }},
                'osProfile': {'linuxConfiguration': {'disablePasswordAuthentication': True}},
                'securityProfile': {'securityType': 'TrustedLaunch', 'uefiSettings': {
                    'secureBootEnabled': True, 'vTpmEnabled': True,
                }},
            }},
        ],
        'outputs': {'mediaDeploymentEnabled': {'type': 'bool'}},
    }


class MediaTemplateSecurityTests(unittest.TestCase):
    def test_complete_opt_in_media_template_passes(self):
        validate_media(media_template())

    def test_media_deployment_must_remain_opt_in(self):
        template = media_template()
        template['parameters']['deployMedia']['defaultValue'] = True
        with self.assertRaisesRegex(ValueError, 'opt-in'):
            validate_media(template)

    def test_public_ssh_rule_fails(self):
        template = media_template()
        ssh = next(rule['properties'] for rule in
                   template['resources'][1]['properties']['securityRules']
                   if rule['properties'].get('destinationPortRange') == '22')
        ssh['sourceAddressPrefix'] = 'Internet'
        with self.assertRaisesRegex(ValueError, 'private Bastion subnet'):
            validate_media(template)

    def test_unbounded_rtp_range_fails(self):
        template = media_template()
        rtp = next(rule['properties'] for rule in
                   template['resources'][1]['properties']['securityRules']
                   if rule['properties'].get('destinationPortRange') == '10000-20000')
        rtp['destinationPortRange'] = '*'
        with self.assertRaisesRegex(ValueError, 'bounded RTP'):
            validate_media(template)

    def test_mutable_image_and_password_authentication_fail(self):
        template = media_template()
        template['resources'][5]['properties']['storageProfile']['imageReference'].pop('id')
        with self.assertRaisesRegex(ValueError, 'versioned Compute Gallery image'):
            validate_media(template)

        template = media_template()
        template['resources'][5]['properties']['osProfile']['linuxConfiguration'][
            'disablePasswordAuthentication'] = False
        with self.assertRaisesRegex(ValueError, 'password authentication'):
            validate_media(template)

    def test_missing_bastion_or_unpinned_gallery_input_fails(self):
        template = media_template()
        template['resources'] = [
            resource for resource in template['resources']
            if resource['type'] != 'Microsoft.Network/bastionHosts'
        ]
        with self.assertRaisesRegex(ValueError, 'Bastion'):
            validate_media(template)

        template = media_template()
        template['parameters']['gatewayImageVersion']['defaultValue'] = 'latest'
        with self.assertRaisesRegex(ValueError, 'explicitly selected version'):
            validate_media(template)

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
