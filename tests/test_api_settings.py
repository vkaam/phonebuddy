"""Cover API runtime settings preflight and their hosting/workflow wiring."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import api_settings
from scripts.check_bicep import validate_api_container

ROOT = Path(__file__).resolve().parents[1]
GOOD = {
    'ENTRA_TENANT_ID': '11111111-2222-3333-4444-555555555555',
    'ENTRA_API_CLIENT_ID': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    'SQL_SERVER': 'sql-pb-dev-abc123.database.windows.net',
    'SQL_DATABASE': 'phonebuddy',
    'SQL_MANAGED_IDENTITY_CLIENT_ID': '99999999-8888-7777-6666-555555555555',
}


class ApiSettingsTests(unittest.TestCase):
    def test_real_public_values_pass_and_become_arm_parameters(self):
        self.assertEqual(api_settings.problems(GOOD), [])
        parameters = api_settings.arm_parameters(GOOD)['parameters']
        self.assertEqual(parameters['entraTenantId']['value'], GOOD['ENTRA_TENANT_ID'])
        self.assertEqual(set(parameters), {
            'entraTenantId', 'entraApiClientId', 'sqlServer', 'sqlDatabase',
            'sqlManagedIdentityClientId'})

    def test_missing_values_are_named(self):
        for name in GOOD:
            values = {**GOOD, name: ''}
            messages = api_settings.problems(values)
            self.assertEqual(len(messages), 1)
            self.assertIn(f'{name} is missing', messages[0])
        self.assertEqual(len(api_settings.problems({})), len(GOOD))

    def test_placeholders_and_malformed_values_fail(self):
        bad = {
            'ENTRA_TENANT_ID': ('UNRESOLVED', '00000000-0000-0000-0000-000000000000',
                                'not-a-guid', '<tenant-id>'),
            'ENTRA_API_CLIENT_ID': ('placeholder', 'TODO'),
            'SQL_SERVER': ('UNRESOLVED', 'evil.example.com', 'changeme'),
            'SQL_DATABASE': ('tbd', '', ' '),
            'SQL_MANAGED_IDENTITY_CLIENT_ID': ('unresolved', '0' * 8 + '-0000-0000-0000-' + '0' * 12),
        }
        for name, values in bad.items():
            for value in values:
                with self.subTest(name=name, value=value):
                    messages = api_settings.problems({**GOOD, name: value})
                    self.assertEqual(len(messages), 1)
                    self.assertTrue(messages[0].startswith(name))

    def test_cli_refuses_without_writing_and_writes_when_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'settings.json'
            with mock.patch.dict(os.environ, {**GOOD, 'SQL_SERVER': 'UNRESOLVED'}):
                with mock.patch('sys.stderr'):
                    self.assertEqual(api_settings.main(['--output', str(output)]), 1)
            self.assertFalse(output.exists())
            with mock.patch.dict(os.environ, GOOD):
                self.assertEqual(api_settings.main(['--output', str(output)]), 0)
            self.assertEqual(json.loads(output.read_text())['parameters']['sqlDatabase']['value'],
                             'phonebuddy')


def api_app():
    env = [{'name': name, 'value': value} for name, value in {
        'RELEASE_VERSION': "[parameters('releaseVersion')]",
        'ENTRA_TENANT_ID': "[parameters('entraTenantId')]",
        'ENTRA_API_CLIENT_ID': "[parameters('entraApiClientId')]",
        'WEB_ORIGIN': "[if(parameters('deployStaticSite'), format('https://{0}', "
                      "reference(resourceId('Microsoft.Web/staticSites', 'x'), "
                      "'2023-12-01').defaultHostname), '')]",
        'SQL_SERVER': "[parameters('sqlServer')]",
        'SQL_DATABASE': "[parameters('sqlDatabase')]",
        'SQL_MANAGED_IDENTITY_CLIENT_ID': "[parameters('sqlManagedIdentityClientId')]",
    }.items()]
    return {'properties': {
        'configuration': {'ingress': {'external': True, 'targetPort': 8080,
                                      'allowInsecure': False}},
        'template': {'containers': [{'env': env}]},
    }}


def api_parameters():
    return {name: {'type': 'string', 'minLength': 1} for name in (
        'entraTenantId', 'entraApiClientId', 'sqlServer', 'sqlDatabase',
        'sqlManagedIdentityClientId')}


class ApiContainerTemplateTests(unittest.TestCase):
    def test_reviewed_template_passes(self):
        validate_api_container(api_parameters(), api_app())

    def test_unsafe_variants_fail(self):
        def mutate(change):
            app = copy.deepcopy(api_app())
            change(app['properties'])
            return app

        cases = {
            'insecure ingress': (lambda p: p['configuration']['ingress'].update(allowInsecure=True),
                                 'insecure'),
            'wrong port': (lambda p: p['configuration']['ingress'].update(targetPort=80), 'port 8080'),
            'secret': (lambda p: p['configuration'].update(secrets=[{'name': 'x'}]), 'secrets'),
            'secretRef': (lambda p: p['template']['containers'][0]['env'].append(
                {'name': 'SQL_PASSWORD', 'secretRef': 'x'}), 'plain public'),
            'extra env': (lambda p: p['template']['containers'][0]['env'].append(
                {'name': 'EXTRA', 'value': 'x'}), 'exactly'),
            'literal origin': (lambda p: p['template']['containers'][0]['env'][3].update(
                value='https://example.com'), 'WEB_ORIGIN'),
            'literal tenant': (lambda p: p['template']['containers'][0]['env'][1].update(
                value='UNRESOLVED'), 'ENTRA_TENANT_ID'),
        }
        for label, (change, message) in cases.items():
            with self.subTest(label), self.assertRaisesRegex(ValueError, message):
                validate_api_container(api_parameters(), mutate(change))

    def test_parameters_must_be_required(self):
        parameters = api_parameters()
        parameters['sqlServer']['defaultValue'] = 'UNRESOLVED'
        with self.assertRaisesRegex(ValueError, 'sqlServer'):
            validate_api_container(parameters, api_app())

    def test_bicep_and_workflows_are_wired(self):
        hosting = (ROOT / 'infra/hosting.bicep').read_text()
        for name in ('ENTRA_TENANT_ID', 'ENTRA_API_CLIENT_ID', 'WEB_ORIGIN', 'SQL_SERVER',
                     'SQL_DATABASE', 'SQL_MANAGED_IDENTITY_CLIENT_ID', 'RELEASE_VERSION'):
            self.assertIn(f"name: '{name}'", hosting)
        self.assertIn('allowInsecure: false', hosting)
        self.assertIn("https://${site.properties.defaultHostname}", hosting)
        self.assertNotIn('secretRef', hosting)
        workflows = ROOT / '.github/workflows'
        ci = (workflows / 'ci.yml').read_text()
        self.assertIn('--file services/api/Dockerfile', ci)
        for name in ('azure-deploy.yml', 'azure-recover.yml'):
            text = (workflows / name).read_text()
            self.assertIn('scripts/api_settings.py', text)
            self.assertIn('vars.PHONEBUDDY_DEV_SQL_SERVER', text)
            self.assertLess(text.index('scripts/api_settings.py'),
                            text.index('az deployment group what-if'))
            self.assertEqual(text.count('@"$RUNNER_TEMP/api-settings.json"'),
                             text.count('az deployment group'))
        deploy = (workflows / 'azure-deploy.yml').read_text()
        self.assertEqual(deploy.count('@"$RUNNER_TEMP/api-settings.json"'), 4)
        self.assertLess(deploy.index('scripts/api_settings.py'),
                        deploy.index('az deployment group create'))
        self.assertNotIn('secrets.PHONEBUDDY', deploy)


if __name__ == '__main__':
    unittest.main()
