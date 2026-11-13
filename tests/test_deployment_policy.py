"""Exercise the release artifact and recovery decisions used by CI."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest

from scripts.deployment_policy import (
    active_candidate_revision_names,
    existing_image_is_reusable,
    recovery_required,
    recovery_revision_action,
    active_revision_action,
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


@unittest.skipUnless(shutil.which('bash'), 'Bash is required to exercise the release step')
class ImagePromotionStepTests(unittest.TestCase):
    def run_promotion(self, scenario):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / '.github/workflows/azure-deploy.yml').read_text()
        step = workflow.split('      - name: Promote the exact image digest', 1)[1]
        script = textwrap.dedent(step.split('        run: |\n', 1)[1].split('      - name:', 1)[0])
        mocks = r"""
az() {
  echo "az $*" >> "$MOCK_LOG"
  case "$*" in
    "acr list "*) echo devregistry ;;
    "acr show "*) echo registry.example ;;
    "acr login "*) : ;;
    "acr repository list "*) echo true ;;
    "acr repository show-tags "*)
      [[ "$MOCK_CASE" == cli_error ]] && return 1
      if [[ "$*" == *changeableAttributes* ]]; then
        [[ "$MOCK_CASE" == writable ]] && echo true || echo false
      elif [[ "$*" == *--detail* && "$MOCK_CASE" != absent ]]; then
        echo "$RELEASE_SHA"
      fi ;;
    "acr repository show "*) printf 'sha256:%064d\n' 0 ;;
    "acr repository update "*) : ;;
    *) return 2 ;;
  esac
}
docker() {
  echo "docker $*" >> "$MOCK_LOG"
  if [[ "$1 $2" == 'image inspect' ]]; then
    if [[ "$MOCK_CASE" == mismatch && "$*" == *registry.example* ]]; then
      echo sha256:other
    else
      echo sha256:matching
    fi
  fi
}
"""
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / 'scripts').mkdir()
            shutil.copy(root / 'scripts/deployment_policy.py', work / 'scripts')
            env = dict(os.environ, MOCK_CASE=scenario, MOCK_LOG=str(work / 'commands'),
                       RESOURCE_GROUP='rg-test', RELEASE_SHA='a' * 40,
                       GITHUB_OUTPUT=str(work / 'output'))
            result = subprocess.run(['bash', '-c', mocks + '\n' + script], cwd=work,
                                    env=env, capture_output=True, text=True)
            log = (work / 'commands').read_text()
            return result, log

    def test_existing_absent_and_unsafe_images(self):
        for scenario, success, push in (
                ('existing', True, False), ('absent', True, True),
                ('writable', False, False), ('mismatch', False, False),
                ('cli_error', False, False)):
            with self.subTest(scenario=scenario):
                result, log = self.run_promotion(scenario)
                self.assertEqual(result.returncode == 0, success, result.stderr)
                self.assertEqual('docker push ' in log, push, log)
                if scenario == 'existing':
                    self.assertIn('docker pull ', log)


class RecoveryPolicyTests(unittest.TestCase):
    def test_partial_apply_or_failed_health_observation_requires_isolation(self):
        self.assertTrue(recovery_required('failure', '', 'skipped', 'skipped'))
        self.assertTrue(recovery_required('success', 'true', 'success', 'failure'))
        self.assertTrue(recovery_required('success', 'true', 'failure', 'skipped'))

    def test_unrelated_failure_or_healthy_observation_does_not_isolate(self):
        self.assertFalse(recovery_required('skipped', '', 'skipped', 'skipped'))
        self.assertFalse(recovery_required('success', 'true', 'success', 'success'))
        self.assertFalse(recovery_required('success', 'true', 'success', 'skipped'))

    def test_missing_or_failed_frontend_deployment_requires_recovery(self):
        self.assertTrue(recovery_required('success', 'true', 'success', 'success', 'failure'))
        self.assertTrue(recovery_required('success', 'true', 'success', 'success', 'skipped'))
        self.assertFalse(recovery_required('success', 'true', 'success', 'success', 'success'))

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

    def test_inactive_duplicate_is_not_manually_activated(self):
        def revision(name, release, image, active, created):
            return {
                'name': name,
                'properties': {
                    'active': active,
                    'createdTime': created,
                    'template': {'containers': [{
                        'image': image,
                        'env': [{'name': 'RELEASE_VERSION', 'value': release}],
                    }]},
                },
            }

        image = 'registry.example/release-test@sha256:' + 'a' * 64
        revisions = [
            revision('older-matching', 'source-sha', image, False, '2026-01-01T00:00:00Z'),
            revision('newer-matching', 'source-sha', image, False, '2026-01-02T00:00:00Z'),
            revision('wrong-digest', 'source-sha', image.replace('a' * 64, 'b' * 64),
                     True, '2026-01-03T00:00:00Z'),
            revision('wrong-source', 'other-sha', image, False, '2026-01-04T00:00:00Z'),
        ]
        self.assertEqual(
            active_revision_action(revisions, 'source-sha', 'a' * 64),
            ('missing', ''),
        )
        self.assertEqual(
            recovery_revision_action(revisions, 'source-sha', 'a' * 64),
            ('none', ''),
        )

    def test_recovery_keeps_exact_active_image_when_no_fallback_exists(self):
        revisions = [{
            'name': 'active-matching',
            'properties': {
                'active': True,
                'createdTime': '2026-01-01T00:00:00Z',
                'template': {'containers': [{
                    'image': 'registry.example/release-test@sha256:' + 'a' * 64,
                    'env': [{'name': 'RELEASE_VERSION', 'value': 'source-sha'}],
                }]},
            },
        }]
        self.assertEqual(
            active_revision_action(revisions, 'source-sha', 'a' * 64),
            ('active', 'active-matching'),
        )
        self.assertEqual(
            recovery_revision_action(revisions, 'source-sha', 'a' * 64),
            ('keep', 'active-matching'),
        )

    def test_recovery_does_not_change_unrelated_revisions(self):
        self.assertEqual(
            recovery_revision_action([], 'source-sha', 'a' * 64),
            ('none', ''),
        )


if __name__ == '__main__':
    unittest.main()
