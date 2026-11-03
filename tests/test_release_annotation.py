"""Test source-bound Application Insights release annotation requests."""
import json
import unittest

from scripts.release_annotation import create_annotation


class ReleaseAnnotationTests(unittest.TestCase):
    def test_annotation_is_deployment_scoped_and_contains_only_release_metadata(self):
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return None

        create_annotation(
            '/subscriptions/12345678-1234-1234-1234-123456789abc/resourceGroups/rg/providers/Microsoft.Insights/components/appi',
            'dev', 'release-abc', 'a' * 40, 'vkaam/phonebuddy/.github/workflows/azure-health-gate.yml@refs/heads/main', run,
        )
        command, kwargs = calls[0]
        payload = json.loads(command[command.index('--body') + 1])
        self.assertEqual(command[1:3], ['rest', '--method'])
        self.assertEqual(payload['Category'], 'Deployment')
        properties = json.loads(payload['Properties'])
        self.assertEqual(properties['Environment'], 'dev')
        self.assertEqual(properties['ReleaseVersion'], 'release-abc')
        self.assertEqual(properties['SourceCommit'], 'a' * 40)
        self.assertTrue(kwargs['check'])
        self.assertTrue(kwargs['capture_output'])

    def test_untrusted_resource_ids_and_production_annotations_are_rejected(self):
        with self.assertRaises(ValueError):
            create_annotation('https://example.invalid', 'dev', 'release', 'a' * 40, 'workflow')
        with self.assertRaises(ValueError):
            create_annotation(
                '/subscriptions/123/resourceGroups/rg/providers/Microsoft.Insights/components/appi',
                'prod', 'release', 'a' * 40, 'workflow', lambda *_args, **_kwargs: None,
            )


if __name__ == '__main__':
    unittest.main()
