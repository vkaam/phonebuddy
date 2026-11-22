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
            'SQL_SERVER': ('UNRESOLVED', 'evil.example.com', 'changeme',
                           'sql-pb-dev-abc123', 'sql-pb-dev-abc123.database.windows.net.evil.com'),
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
        deploy = (workflows / 'azure-deploy.yml').read_text()
        recover = (workflows / 'azure-recover.yml').read_text()
        for text in (deploy, recover):
            self.assertIn('vars.PHONEBUDDY_DEV_SQL_SERVER', text)
        # Normal deploys keep the strict preflight before any preview or deployment.
        self.assertLess(deploy.index('scripts/api_settings.py --output'),
                        deploy.index('az deployment group what-if'))
        self.assertEqual(deploy.count('@"$RUNNER_TEMP/api-settings.json"'), 2)
        # Both recovery paths filter to what the target release's own template declares.
        self.assertEqual(deploy.count('@"$RUNNER_TEMP/recovery-api-settings.json"'), 2)
        self.assertEqual(recover.count('@"$RUNNER_TEMP/api-settings.json"'), 2)
        filter_call = 'scripts/api_settings.py --template "$RUNNER_TEMP/recovery-hosting.json"'
        for text in (deploy, recover):
            self.assertIn(filter_call, text)
            self.assertLess(text.index(filter_call), text.index('recovery-api-settings.json"')
                            if text is deploy else text.index('@"$RUNNER_TEMP/api-settings.json"'))
        self.assertNotIn('scripts/api_settings.py --output', recover)
        for line in recover.splitlines():
            if '${{ steps.release.outputs' in line or '${{ steps.web-deploy.outputs' in line:
                # Step outputs reach scripts only through env, never inline in run: blocks.
                self.assertRegex(line, r'^\s+[A-Za-z_]+: \$\{\{ steps\.[\w.-]+ \}\}$')
        self.assertNotIn('secrets.PHONEBUDDY', deploy)


class RecoveryTemplateFilterTest(unittest.TestCase):
    NEW = ('entraTenantId', 'entraApiClientId', 'sqlServer', 'sqlDatabase',
           'sqlManagedIdentityClientId')

    def template(self, directory, extra):
        path = Path(directory) / 'recovery-hosting.json'
        parameters = {'environment': {'type': 'string'}, 'releaseVersion': {'type': 'string'}}
        parameters.update({name: {'type': 'string'} for name in extra})
        path.write_text(json.dumps({'parameters': parameters}), encoding='utf-8')
        return path

    def run_main(self, template, env, output):
        with mock.patch.dict(os.environ, env, clear=True):
            return api_settings.main(['--template', str(template), '--output', str(output)])

    def test_pre_change_template_gets_no_settings_and_is_not_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            template = self.template(directory, ())
            output = Path(directory) / 'out.json'
            self.assertEqual(api_settings.declared_settings(template), {})
            # Unset variables must not block recovery of an older release.
            self.assertEqual(self.run_main(template, {}, output), 0)
            self.assertEqual(json.loads(output.read_text())['parameters'], {})

    def test_post_change_template_keeps_all_five_and_stays_strict(self):
        with tempfile.TemporaryDirectory() as directory:
            template = self.template(directory, self.NEW)
            output = Path(directory) / 'out.json'
            self.assertEqual(len(api_settings.declared_settings(template)), 5)
            self.assertEqual(self.run_main(template, GOOD, output), 0)
            self.assertEqual(set(json.loads(output.read_text())['parameters']), set(self.NEW))
            self.assertEqual(self.run_main(template, {}, output), 1)

    def test_partial_template_keeps_only_declared_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            template = self.template(directory, ('sqlServer',))
            output = Path(directory) / 'out.json'
            self.assertEqual(self.run_main(template, {'SQL_SERVER': GOOD['SQL_SERVER']}, output), 0)
            self.assertEqual(set(json.loads(output.read_text())['parameters']), {'sqlServer'})

    def test_database_name_matches_the_api_pattern(self):
        self.assertEqual(len(api_settings.problems({**GOOD, 'SQL_DATABASE': 'phone.buddy'})), 1)
        self.assertEqual(api_settings.problems({**GOOD, 'SQL_DATABASE': 'phone_buddy-1'}), [])


if __name__ == '__main__':
    unittest.main()
