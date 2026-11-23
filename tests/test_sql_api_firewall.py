"""The API's SQL access is managed firewall rules for its outbound IPs (issue 152)."""
import copy
import re
import unittest
from pathlib import Path

from scripts import database_release as dr
from scripts.check_bicep import unexpected_what_if_diagnostics, validate_sql_api_firewall, validate_what_if

ROOT = Path(__file__).resolve().parents[1]


def compiled():
    return {'resources': [{
        'condition': "[parameters('deployWorkload')]",
        'type': 'Microsoft.Resources/deployments',
        'name': 'sql-api-firewall',
        'properties': {
            'parameters': {'outboundIpAddresses': {'value':
                "[reference(resourceId('Microsoft.App/containerApps', 'x'), "
                "'2023-05-01').outboundIpAddresses]"}},
            'template': {
                'variables': {'rulePrefix': 'pb-api-egress-'},
                'resources': [{
                    'copy': {'name': 'apiEgress', 'count': '[length(parameters(\'ips\'))]'},
                    'type': 'Microsoft.Sql/servers/firewallRules',
                    'name': "[format('{0}/{1}', 'sql', format('{0}{1}', "
                            "variables('rulePrefix'), copyIndex()))]",
                    'properties': {'startIpAddress': "[parameters('ips')[copyIndex()]]",
                                   'endIpAddress': "[parameters('ips')[copyIndex()]]"}}]}}}]}


class SqlApiFirewallTests(unittest.TestCase):
    def test_reviewed_shape_passes(self):
        validate_sql_api_firewall(compiled())

    def test_unsafe_shapes_are_rejected(self):
        def mutate(change):
            template = copy.deepcopy(compiled())
            change(template['resources'][0])
            return template
        rule = lambda d: d['properties']['template']['resources'][0]
        cases = {
            'unconditional': lambda d: d.pop('condition'),
            'release prefix': lambda d: d['properties']['template']['variables'].update(
                rulePrefix='pb-release-'),
            'allow all azure': lambda d: rule(d)['properties'].update(
                startIpAddress='0.0.0.0', endIpAddress='0.0.0.0'),
            'range': lambda d: rule(d)['properties'].update(endIpAddress='255.255.255.255'),
            'not looped': lambda d: rule(d).pop('copy'),
            'fixed ips': lambda d: d['properties']['parameters'].update(
                outboundIpAddresses={'value': ['1.2.3.4']}),
        }
        for label, change in cases.items():
            with self.subTest(label), self.assertRaises(ValueError):
                validate_sql_api_firewall(mutate(change))
        with self.assertRaises(ValueError):
            validate_sql_api_firewall({'resources': []})

    def test_bicep_sources_use_outbound_ips_and_a_distinct_prefix(self):
        module = (ROOT / 'infra/modules/sql-firewall-rules.bicep').read_text()
        hosting = (ROOT / 'infra/hosting.bicep').read_text()
        self.assertIn("var rulePrefix = 'pb-api-egress-'", module)
        self.assertIn('Microsoft.Sql/servers/firewallRules@', module)
        self.assertNotIn('0.0.0.0', re.sub(r'//.*', '', module))
        self.assertIn('= if (deployWorkload)', hosting.split('module sqlApiFirewall')[1].split('\n')[0])
        self.assertIn('outboundIpAddresses: app.properties.outboundIpAddresses', hosting)

    def test_managed_rule_names_can_never_match_the_release_sweep_prefix(self):
        self.assertFalse('pb-api-egress-0'.startswith(dr.FIREWALL_PREFIX))
        self.assertFalse(dr.FIREWALL_PREFIX.startswith('pb-api-egress-'))

    def diagnostic(self, name='sql-api-firewall', group='rg-pb-dev-francecentral-foundation',
                   code='NestedDeploymentShortCircuited', level='Warning'):
        return {'code': code, 'level': level, 'target': None, 'message':
                "The nested deployment '/subscriptions/43c19721-4a1d-49ed-954b-5e8a29b346b1/"
                f"resourceGroups/{group}/providers/Microsoft.Resources/deployments/{name}' at "
                "line '1' could not be expanded because of copy count expressions."}

    def test_only_the_reviewed_short_circuit_diagnostic_is_tolerated(self):
        self.assertEqual(unexpected_what_if_diagnostics([self.diagnostic()]), [])
        for bad in (self.diagnostic(name='other'), self.diagnostic(group='rg-pb-test-x'),
                    self.diagnostic(code='Other'), self.diagnostic(level='Error')):
            self.assertEqual(unexpected_what_if_diagnostics([bad]), [bad])
        result = {'status': 'Succeeded', 'diagnostics': [self.diagnostic()], 'changes': [{
            'changeType': 'Modify', 'resourceId':
            '/subscriptions/43c19721-4a1d-49ed-954b-5e8a29b346b1/resourceGroups/'
            'rg-pb-dev-francecentral-foundation/providers/Microsoft.App/containerApps/x'}]}
        self.assertTrue(validate_what_if(result))
        result['diagnostics'].append(self.diagnostic(name='other'))
        with self.assertRaisesRegex(ValueError, 'unverified'):
            validate_what_if(result)


if __name__ == '__main__':
    unittest.main()
