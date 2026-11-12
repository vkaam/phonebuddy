"""Exercise immutable release-state and automatic-recovery policies."""
import io
import unittest
from urllib.error import HTTPError

from scripts.release_recovery import (
    AzureBlobStore,
    ReleaseStateError,
    has_destructive_infrastructure_change,
    manual_recovery_decision,
    recovery_decision,
    validate_manifest,
)


def release(source_sha, *, version=1, compatible=None, mode='none'):
    if compatible is None:
        compatible = [version]
    return {
        'schema_version': 1,
        'source_sha': source_sha * 40,
        'workflow_run_id': 1234,
        'workflow_run_attempt': 1,
        'image_digest': 'sha256:' + 'a' * 64,
        'frontend_blob': f'releases/{source_sha * 40}/1234-1/web.tar.gz',
        'frontend_sha256': 'b' * 64,
        'configuration': {
            'environment': 'dev',
            'resource_group': 'rg-pb-dev-francecentral-foundation',
            'container_app': 'ca-pb-dev-release-test',
            'static_site_name': 'stapp-pb-dev-abc123',
            'static_site_location': 'eastus2',
            'container_image_digest': 'a' * 64,
            'hosting_template_sha256': 'd' * 64,
            'release_schema_sha256': 'e' * 64,
        },
        'release_configuration_sha256': 'c' * 64,
        'schema_compatibility': {
            'version': version,
            'compatible_versions': compatible,
            'migration_mode': mode,
        },
    }


class ReleaseManifestTests(unittest.TestCase):
    def test_valid_manifest_is_accepted(self):
        manifest = release('a')
        self.assertIs(validate_manifest(manifest), manifest)

    def test_manifest_requires_exact_immutable_artifact_metadata(self):
        cases = [
            ('schema_version', True),
            ('source_sha', 'short'),
            ('image_digest', 'latest'),
            ('workflow_run_attempt', False),
            ('frontend_blob', '../web.tar.gz'),
            ('frontend_sha256', 'bad'),
            ('configuration', []),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                manifest = release('a')
                manifest[key] = value
                with self.assertRaises(ReleaseStateError):
                    validate_manifest(manifest)

    def test_schema_contract_must_be_self_compatible_and_supported(self):
        manifest = release('a', compatible=[2], version=1)
        with self.assertRaisesRegex(ReleaseStateError, 'support its own'):
            validate_manifest(manifest)
        manifest = release('a', mode='unknown')
        with self.assertRaisesRegex(ReleaseStateError, 'migration_mode'):
            validate_manifest(manifest)


class RecoveryDecisionTests(unittest.TestCase):
    def test_first_release_stops_without_automatic_recovery(self):
        self.assertEqual(
            recovery_decision(release('a'), None),
            (False, 'no_last_known_good_release'),
        )

    def test_compatible_prior_release_is_eligible(self):
        prior = release('a', compatible=[1, 2])
        candidate = release('b', version=2, mode='expand')
        self.assertEqual(
            recovery_decision(candidate, prior),
            (True, 'compatible_last_known_good_release'),
        )

    def test_schema_contract_destructive_infra_and_retries_fail_closed(self):
        prior = release('a', compatible=[1, 2])
        self.assertEqual(
            recovery_decision(release('b', version=3), prior),
            (False, 'last_known_good_does_not_support_candidate_schema'),
        )
        self.assertEqual(
            recovery_decision(release('b', version=2, mode='contract'), prior),
            (False, 'contract_migration_cannot_auto_rollback'),
        )
        self.assertEqual(
            recovery_decision(release('b', version=2), prior, destructive_changes=True),
            (False, 'destructive_infrastructure_change'),
        )
        self.assertEqual(
            recovery_decision(release('b', version=2), prior, attempt=2),
            (False, 'recovery_attempt_limit'),
        )

    def test_invalid_or_already_promoted_state_is_not_used(self):
        self.assertFalse(recovery_decision(release('a'), {'source_sha': 'bad'})[0])
        self.assertEqual(
            recovery_decision(release('a'), release('a')),
            (False, 'candidate_is_already_last_known_good'),
        )

    def test_destructive_what_if_is_detected_and_invalid_result_fails_closed(self):
        self.assertTrue(has_destructive_infrastructure_change({
            'changes': [{'changeType': 'Delete', 'resourceType': 'Microsoft.Storage/storageAccounts'}],
        }))
        self.assertTrue(has_destructive_infrastructure_change({
            'changes': [{
                'changeType': 'Modify',
                'resourceType': 'Microsoft.Sql/servers/databases',
                'delta': [{'propertyChangeType': 'Delete'}],
            }],
        }))
        self.assertFalse(has_destructive_infrastructure_change({
            'changes': [{'changeType': 'Modify', 'resourceType': 'Microsoft.App/containerApps'}],
        }))
        with self.assertRaisesRegex(ReleaseStateError, 'changes array'):
            has_destructive_infrastructure_change({})

    def test_manual_recovery_requires_schema_compatibility_and_current_evidence(self):
        current = release('b', version=2, compatible=[1, 2], mode='expand')
        target = release('a', compatible=[1, 2])
        self.assertEqual(
            manual_recovery_decision(target, current),
            (True, 'operator_selected_compatible_immutable_release'),
        )
        self.assertEqual(
            manual_recovery_decision(target, None),
            (False, 'no_current_release_schema_evidence'),
        )
        incompatible = release('a', compatible=[1])
        self.assertEqual(
            manual_recovery_decision(incompatible, current),
            (False, 'selected_release_does_not_support_current_schema'),
        )


class _Response:
    def __init__(self, status, body=b'', headers=None):
        self.status = status
        self._body = body
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self._body


class BlobStoreTests(unittest.TestCase):
    def test_get_returns_payload_and_etag(self):
        calls = []

        def opener(request, timeout):
            calls.append((request, timeout))
            return _Response(200, b'{"source_sha":"abc"}', {'ETag': '"v1"'})

        store = AzureBlobStore('pbdevstate123', 'release-state', 'token', opener)
        body, etag = store.get('releases/abc/manifest.json')
        self.assertEqual(body, b'{"source_sha":"abc"}')
        self.assertEqual(etag, '"v1"')
        request, timeout = calls[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertEqual(request.full_url,
                         'https://pbdevstate123.blob.core.windows.net/release-state/'
                         'releases/abc/manifest.json')
        self.assertEqual(timeout, 30)

    def test_put_requires_compare_and_swap_or_create_only(self):
        requests = []

        def opener(request, timeout):
            requests.append(request)
            return _Response(201, headers={'ETag': '"v2"'})

        store = AzureBlobStore('pbdevstate123', 'release-state', 'token', opener)
        with self.assertRaisesRegex(ReleaseStateError, 'ETag or create-only'):
            store.put('latest.json', b'{}')
        self.assertEqual(store.put('latest.json', b'{}', etag='"v1"'), '"v2"')
        self.assertEqual(requests[0].get_header('If-match'), '"v1"')
        store.put('releases/a/manifest.json', b'{}', create_only=True)
        self.assertEqual(requests[1].get_header('If-none-match'), '*')

    def test_concurrent_state_write_is_rejected(self):
        def opener(_request, timeout):
            raise HTTPError('https://example.test', 412, 'precondition failed', {}, io.BytesIO())

        store = AzureBlobStore('pbdevstate123', 'release-state', 'token', opener)
        with self.assertRaisesRegex(ReleaseStateError, 'changed concurrently'):
            store.put('latest.json', b'{}', etag='"old"')

    def test_blob_names_and_credentials_are_validated(self):
        with self.assertRaisesRegex(ReleaseStateError, 'account name'):
            AzureBlobStore('UPPERCASE', 'release-state', 'token')
        with self.assertRaisesRegex(ReleaseStateError, 'OAuth token'):
            AzureBlobStore('pbdevstate123', 'release-state', '')

    def test_blob_get_404_is_missing_and_not_an_error(self):
        def opener(_request, timeout):
            raise HTTPError('https://example.test', 404, 'missing', {}, io.BytesIO())

        store = AzureBlobStore('pbdevstate123', 'release-state', 'token', opener)
        self.assertEqual(store.get('last-known-good.json'), (None, None))


if __name__ == '__main__':
    unittest.main()
