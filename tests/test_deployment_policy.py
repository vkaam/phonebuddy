"""Exercise the release artifact and recovery decisions used by CI."""
import unittest

from scripts.deployment_policy import (
    active_candidate_revision_names,
    existing_image_is_reusable,
    recovery_required,
    verify_artifact_manifest,
    verify_current_source,
)


class ArtifactPolicyTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            'schema_version': 1,
            'source_sha': 'a' * 40,
            'workflow_run_id': 12345,
            'workflow_run_attempt': 2,
            'image_tag': f"phonebuddy-release-test:{'a' * 40}",
            'image_archive': 'release-test.tar.gz',
        }

    def test_exact_source_run_and_attempt_are_required(self):
        verify_artifact_manifest(self.manifest, 'a' * 40, 12345, 2)
        for field, value in (
                ('source_sha', 'b' * 40),
                ('workflow_run_id', 54321),
                ('workflow_run_attempt', 1),
                ('image_tag', 'phonebuddy-release-test:other'),
                ('image_archive', 'other.tar.gz'),
                ('schema_version', 2),
                ('schema_version', True),
                ('workflow_run_id', True),
                ('workflow_run_attempt', 2.0)):
            with self.subTest(field=field):
                tampered = dict(self.manifest, **{field: value})
                with self.assertRaisesRegex(ValueError, 'does not match'):
                    verify_artifact_manifest(tampered, 'a' * 40, 12345, 2)

    def test_queued_release_is_rejected_after_main_advances(self):
        verify_current_source('a' * 40, 'a' * 40)
        with self.assertRaisesRegex(ValueError, 'current main'):
            verify_current_source('a' * 40, 'b' * 40)
        with self.assertRaisesRegex(ValueError, 'current main'):
            verify_current_source('short', 'short')

    def test_duplicate_trigger_reuses_only_the_same_immutable_image(self):
        self.assertTrue(existing_image_is_reusable('false', 'sha256:abc', 'sha256:abc'))
        self.assertFalse(existing_image_is_reusable('true', 'sha256:abc', 'sha256:abc'))
        self.assertFalse(existing_image_is_reusable('None', 'sha256:abc', 'sha256:abc'))
        self.assertFalse(existing_image_is_reusable('false', 'sha256:abc', 'sha256:other'))
        self.assertFalse(existing_image_is_reusable('false', '', 'sha256:abc'))


class RecoveryPolicyTests(unittest.TestCase):
    def test_partial_apply_or_failed_health_observation_requires_isolation(self):
        self.assertTrue(recovery_required('failure', '', 'skipped'))
        self.assertTrue(recovery_required('success', 'true', 'failure'))

    def test_unrelated_failure_or_healthy_observation_does_not_isolate(self):
        self.assertFalse(recovery_required('skipped', '', 'skipped'))
        self.assertFalse(recovery_required('success', 'true', 'success'))
        self.assertFalse(recovery_required('success', 'true', 'skipped'))

    def test_recovery_selects_only_active_revision_for_failed_release(self):
        def revision(name, release, active):
            return {
                'name': name,
                'properties': {
                    'active': active,
                    'template': {'containers': [{'env': [
                        {'name': 'RELEASE_VERSION', 'value': release},
                    ]}]},
                },
            }

        revisions = [
            revision('old-healthy', 'old-sha', True),
            revision('candidate', 'candidate-sha', True),
            revision('inactive-candidate', 'candidate-sha', False),
        ]
        self.assertEqual(
            active_candidate_revision_names(revisions, 'candidate-sha'),
            ['candidate'],
        )
        self.assertEqual(active_candidate_revision_names(revisions, 'missing'), [])
        with self.assertRaisesRegex(ValueError, 'Revision data'):
            active_candidate_revision_names({}, 'candidate-sha')


if __name__ == '__main__':
    unittest.main()
