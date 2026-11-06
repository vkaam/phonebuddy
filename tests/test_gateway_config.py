"""Gateway config rendering validates inputs and keeps rendered secrets private."""
from pathlib import Path
import tempfile
import unittest

from infra.gateway.render_config import render, runtime_values


def runtime():
    return {
        'GATEWAY_PRIVATE_IP': '10.65.0.4',
        'GATEWAY_PUBLIC_IP': '20.30.40.50',
        'GATEWAY_FQDN': 'media.dev.phonebuddy.example',
        'WEBRTC_TEST_PASSWORD': 'a' * 40,
        'TURN_SHARED_SECRET': 'b' * 48,
    }


class GatewayRuntimeValidationTests(unittest.TestCase):
    def test_runtime_values_require_addresses_domain_and_secrets(self):
        self.assertEqual(runtime_values(runtime())['GATEWAY_FQDN'],
                         'media.dev.phonebuddy.example')
        for name, value in (
            ('GATEWAY_PRIVATE_IP', '20.30.40.50'),
            ('GATEWAY_PUBLIC_IP', '10.0.0.1'),
            ('GATEWAY_FQDN', 'not a hostname'),
            ('TURN_SHARED_SECRET', 'short'),
        ):
            values = runtime()
            values[name] = value
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    runtime_values(values)

    def test_missing_runtime_secret_fails_closed(self):
        values = runtime()
        del values['TURN_SHARED_SECRET']
        with self.assertRaisesRegex(ValueError, 'TURN_SHARED_SECRET'):
            runtime_values(values)


class GatewayConfigRenderingTests(unittest.TestCase):
    def test_turn_configuration_uses_secret_auth_and_denies_private_peers(self):
        template = (Path(__file__).resolve().parents[1]
                    / 'infra/gateway/coturn/turnserver.conf.template').read_text(encoding='utf-8')
        self.assertIn('use-auth-secret', template)
        self.assertIn('static-auth-secret=__TURN_SHARED_SECRET__', template)
        self.assertIn('denied-peer-ip=10.0.0.0-10.255.255.255', template)
        self.assertIn('allowed-peer-ip=__GATEWAY_PRIVATE_IP__', template)
        self.assertNotIn('no-loopback-peers', template)
        self.assertNotIn('no-cli', template)
        self.assertNotIn('min-tls-version=', template)

    def test_templates_render_without_leaking_values_to_console_or_filesystem_modes(self):
        values = runtime()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'runtime'
            names = render(output, values)
            self.assertEqual(names, ('http.conf', 'pjsip.conf', 'turnserver.conf'))
            self.assertEqual(output.stat().st_mode & 0o777, 0o700)
            for name in names:
                content = (output / name).read_text(encoding='utf-8')
                self.assertNotRegex(content, r'__[A-Z0-9_]+__')
                self.assertEqual((output / name).stat().st_mode & 0o777, 0o600)
            self.assertIn(values['WEBRTC_TEST_PASSWORD'],
                          (output / 'pjsip.conf').read_text(encoding='utf-8'))
            self.assertIn(values['TURN_SHARED_SECRET'],
                          (output / 'turnserver.conf').read_text(encoding='utf-8'))

    def test_symlink_targets_are_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protected = root / 'protected'
            protected.write_text('untouched', encoding='utf-8')
            output = root / 'runtime'
            output.symlink_to(protected)
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                render(output, runtime())
            self.assertEqual(protected.read_text(encoding='utf-8'), 'untouched')


if __name__ == '__main__':
    unittest.main()
