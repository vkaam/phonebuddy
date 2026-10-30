"""Deployment preflight rejects unresolved or mismatched environment inputs."""
import unittest

from scripts.check_bicep import deployment_ready


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


if __name__ == '__main__':
    unittest.main()
