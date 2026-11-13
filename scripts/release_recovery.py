#!/usr/bin/env python3
"""Validate immutable release records and protect last-known-good state."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SCHEMA_VERSION = 1
MAX_AUTOMATIC_RECOVERY_ATTEMPTS = 1
_SHA = re.compile(r'^[0-9a-f]{40}$')
_DIGEST = re.compile(r'^sha256:[0-9a-f]{64}$')
_COMPATIBILITY_MODES = {'none', 'expand', 'contract'}


class ReleaseStateError(ValueError):
    """Raised when release state is invalid or cannot be updated safely."""


def validate_manifest(manifest):
    """Validate the durable, non-secret release manifest and return it."""
    if not isinstance(manifest, dict):
        raise ReleaseStateError('Release manifest must be an object')
    if (isinstance(manifest.get('schema_version'), bool)
            or manifest.get('schema_version') != SCHEMA_VERSION):
        raise ReleaseStateError('Unsupported release manifest schema')
    if not isinstance(manifest.get('source_sha'), str) or not _SHA.fullmatch(manifest['source_sha']):
        raise ReleaseStateError('source_sha must be a full lowercase commit SHA')
    if not isinstance(manifest.get('image_digest'), str) or not _DIGEST.fullmatch(manifest['image_digest']):
        raise ReleaseStateError('image_digest must be an immutable sha256 digest')
    if (not isinstance(manifest.get('workflow_run_id'), int)
            or isinstance(manifest.get('workflow_run_id'), bool)
            or manifest['workflow_run_id'] <= 0):
        raise ReleaseStateError('workflow_run_id must be a positive integer')
    if (not isinstance(manifest.get('workflow_run_attempt'), int)
            or isinstance(manifest.get('workflow_run_attempt'), bool)
            or manifest['workflow_run_attempt'] <= 0):
        raise ReleaseStateError('workflow_run_attempt must be a positive integer')
    expected_frontend_blob = (
        f"releases/{manifest['source_sha']}/"
        f"{manifest['workflow_run_id']}-{manifest['workflow_run_attempt']}/web.tar.gz"
    )
    if manifest.get('frontend_blob') != expected_frontend_blob:
        raise ReleaseStateError('frontend_blob must identify this release’s immutable bundle')
    if (not isinstance(manifest.get('frontend_sha256'), str)
            or not re.fullmatch(r'[0-9a-f]{64}', manifest['frontend_sha256'])):
        raise ReleaseStateError('frontend_sha256 must be a lowercase SHA-256 digest')
    configuration = manifest.get('configuration')
    if not isinstance(configuration, dict):
        raise ReleaseStateError('configuration must be an object')
    if (configuration.get('environment') != 'dev'
            or not isinstance(configuration.get('resource_group'), str)
            or not re.fullmatch(r'rg-pb-dev-[a-z0-9-]+', configuration['resource_group'])
            or not isinstance(configuration.get('container_app'), str)
            or not re.fullmatch(r'ca-pb-dev-[a-z0-9-]+', configuration['container_app'])
            or not isinstance(configuration.get('static_site_name'), str)
            or (configuration['static_site_name'] and not re.fullmatch(
                r'stapp-pb-dev-[a-z0-9-]+', configuration['static_site_name']))
            or not isinstance(configuration.get('static_site_location'), str)
            or not re.fullmatch(r'[a-z0-9]+', configuration['static_site_location'])
            or configuration.get('container_image_digest') != manifest['image_digest'].removeprefix('sha256:')):
        raise ReleaseStateError('configuration contains unsupported deployment values')
    for key in ('hosting_template_sha256', 'release_schema_sha256'):
        if not isinstance(configuration.get(key), str) or not re.fullmatch(
                r'[0-9a-f]{64}', configuration[key]):
            raise ReleaseStateError(f'configuration.{key} must be a lowercase SHA-256 digest')
    schema = manifest.get('schema_compatibility')
    if not isinstance(schema, dict):
        raise ReleaseStateError('schema_compatibility must be an object')
    current = schema.get('version')
    compatible = schema.get('compatible_versions')
    mode = schema.get('migration_mode')
    if isinstance(current, bool) or not isinstance(current, int) or current < 0:
        raise ReleaseStateError('schema_compatibility.version must be a nonnegative integer')
    if (not isinstance(compatible, list) or not compatible
            or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in compatible)
            or len(set(compatible)) != len(compatible)):
        raise ReleaseStateError('compatible_versions must be a nonempty list of unique nonnegative integers')
    if current not in compatible:
        raise ReleaseStateError('A release must support its own schema version')
    if mode not in _COMPATIBILITY_MODES:
        raise ReleaseStateError('migration_mode must be none, expand, or contract')
    if not isinstance(manifest.get('release_configuration_sha256'), str) or not re.fullmatch(
            r'[0-9a-f]{64}', manifest['release_configuration_sha256']):
        raise ReleaseStateError('release_configuration_sha256 must be a lowercase SHA-256 digest')
    return manifest


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def recovery_decision(candidate, last_good, destructive_changes=False, attempt=1):
    """Return a fail-closed automatic recovery decision and reason."""
    try:
        validate_manifest(candidate)
    except ReleaseStateError as error:
        return False, f'invalid_candidate:{error}'
    if attempt > MAX_AUTOMATIC_RECOVERY_ATTEMPTS:
        return False, 'recovery_attempt_limit'
    if not isinstance(last_good, dict):
        return False, 'no_last_known_good_release'
    try:
        validate_manifest(last_good)
    except ReleaseStateError as error:
        return False, f'invalid_last_known_good:{error}'
    if candidate['source_sha'] == last_good['source_sha']:
        return False, 'candidate_is_already_last_known_good'
    if destructive_changes:
        return False, 'destructive_infrastructure_change'
    candidate_schema = candidate['schema_compatibility']
    prior_schema = last_good['schema_compatibility']
    if candidate_schema['migration_mode'] == 'contract':
        return False, 'contract_migration_cannot_auto_rollback'
    if candidate_schema['version'] not in prior_schema['compatible_versions']:
        return False, 'last_known_good_does_not_support_candidate_schema'
    return True, 'compatible_last_known_good_release'


def manual_recovery_decision(target, current_release):
    """Require current schema evidence before an operator selects an older app."""
    try:
        validate_manifest(target)
    except ReleaseStateError as error:
        return False, f'invalid_target:{error}'
    if not isinstance(current_release, dict):
        return False, 'no_current_release_schema_evidence'
    try:
        validate_manifest(current_release)
    except ReleaseStateError as error:
        return False, f'invalid_current_release:{error}'
    if target['source_sha'] == current_release['source_sha']:
        return True, 'release_is_already_current'
    if target['schema_compatibility']['migration_mode'] == 'contract':
        return False, 'contract_release_cannot_be_manually_recovered'
    current_schema = current_release['schema_compatibility']['version']
    if current_schema not in target['schema_compatibility']['compatible_versions']:
        return False, 'selected_release_does_not_support_current_schema'
    return True, 'operator_selected_compatible_immutable_release'


def has_destructive_infrastructure_change(what_if):
    """Fail closed when Azure What-If includes a resource deletion or replacement."""
    if not isinstance(what_if, dict) or not isinstance(what_if.get('changes'), list):
        raise ReleaseStateError('Azure What-If result must contain a changes array')
    for change in what_if['changes']:
        if not isinstance(change, dict):
            continue
        if str(change.get('changeType', '')).casefold() in {'delete', 'replace'}:
            return True
        if str(change.get('changeType', '')).casefold() == 'modify':
            resource_type = str(change.get('resourceType', '')).casefold()
            delta = change.get('delta')
            if resource_type.startswith(('microsoft.sql/', 'microsoft.storage/')):
                if isinstance(delta, list) and any(
                        isinstance(item, dict)
                        and str(item.get('propertyChangeType', '')).casefold() == 'delete'
                        for item in delta):
                    return True
    return False


class AzureBlobStore:
    """Small Azure Blob REST client using the active Azure CLI OAuth token."""

    def __init__(self, account, container, token, opener=urlopen):
        if not re.fullmatch(r'[a-z0-9]{3,24}', account or ''):
            raise ReleaseStateError('Invalid Azure Storage account name')
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?', container or ''):
            raise ReleaseStateError('Invalid Azure Blob container name')
        if not token:
            raise ReleaseStateError('Azure Storage OAuth token is required')
        self.account = account
        self.container = container
        self.token = token
        self.opener = opener

    def _url(self, blob):
        parts = [quote(part, safe='') for part in blob.split('/') if part]
        if not parts:
            raise ReleaseStateError('Blob path is required')
        return f'https://{self.account}.blob.core.windows.net/{self.container}/' + '/'.join(parts)

    def _request(self, method, blob, body=None, headers=None):
        request_headers = {
            'Authorization': f'Bearer {self.token}',
            'x-ms-date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'x-ms-version': '2023-11-03',
        }
        request_headers.update(headers or {})
        request = Request(self._url(blob), data=body, headers=request_headers, method=method)
        try:
            with self.opener(request, timeout=30) as response:
                return response.status, response.read(), response.headers
        except HTTPError as error:
            if error.code == 404:
                headers = error.headers
                error.close()
                return 404, b'', headers
            if error.code == 412:
                error.close()
                raise ReleaseStateError('Release state changed concurrently; refusing stale update') from error
            if error.code == 409 and error.headers.get('x-ms-error-code') == 'BlobAlreadyExists':
                error.close()
                raise ReleaseStateError('Release blob already exists') from error
            error.close()
            raise ReleaseStateError(f'Azure Blob request failed with HTTP {error.code}') from error
        except (TimeoutError, URLError) as error:
            raise ReleaseStateError('Azure Blob request failed before a response was received') from error

    def get(self, blob):
        status, body, headers = self._request('GET', blob)
        if status == 404:
            return None, None
        if status != 200:
            raise ReleaseStateError(f'Unexpected Azure Blob GET status {status}')
        return body, headers.get('ETag')

    def put(self, blob, body, *, etag=None, create_only=False, content_type='application/octet-stream'):
        headers = {
            'x-ms-blob-type': 'BlockBlob',
            'Content-Type': content_type,
            'Content-Length': str(len(body)),
        }
        if create_only:
            headers['If-None-Match'] = '*'
        elif etag:
            headers['If-Match'] = etag
        else:
            raise ReleaseStateError('State updates require an ETag or create-only condition')
        status, _, response_headers = self._request('PUT', blob, body, headers)
        if status not in (201, 202):
            raise ReleaseStateError(f'Unexpected Azure Blob PUT status {status}')
        return response_headers.get('ETag')


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseStateError(f'Cannot read JSON file {path}: {error}') from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    validate = subparsers.add_parser('validate')
    validate.add_argument('--manifest', required=True, type=Path)
    create = subparsers.add_parser('create-manifest')
    create.add_argument('--source-sha', required=True)
    create.add_argument('--run-id', required=True, type=int)
    create.add_argument('--run-attempt', required=True, type=int)
    create.add_argument('--image-digest', required=True)
    create.add_argument('--frontend-blob', required=True)
    create.add_argument('--frontend-archive', required=True, type=Path)
    create.add_argument('--configuration', required=True, type=Path)
    create.add_argument('--schema-compatibility', required=True, type=Path)
    create.add_argument('--output', required=True, type=Path)
    whatif = subparsers.add_parser('check-what-if')
    whatif.add_argument('--path', required=True, type=Path)
    whatif.add_argument('--output', type=Path)
    decision = subparsers.add_parser('decide')
    decision.add_argument('--candidate', required=True, type=Path)
    decision.add_argument('--last-good', type=Path)
    decision.add_argument('--destructive-changes', action='store_true')
    decision.add_argument('--attempt', type=int, default=1)
    manual = subparsers.add_parser('manual-decision')
    manual.add_argument('--target', required=True, type=Path)
    manual.add_argument('--current', required=True, type=Path)
    put = subparsers.add_parser('blob-put')
    put.add_argument('--account', required=True)
    put.add_argument('--container', required=True)
    put.add_argument('--blob', required=True)
    put.add_argument('--file', required=True, type=Path)
    condition = put.add_mutually_exclusive_group(required=True)
    condition.add_argument('--if-match')
    condition.add_argument('--create-only', action='store_true')
    put.add_argument('--idempotent', action='store_true')
    get = subparsers.add_parser('blob-get')
    get.add_argument('--account', required=True)
    get.add_argument('--container', required=True)
    get.add_argument('--blob', required=True)
    get.add_argument('--output', required=True, type=Path)
    get.add_argument('--etag-output', type=Path)
    get.add_argument('--allow-missing', action='store_true')
    publish = subparsers.add_parser('publish-last-good')
    publish.add_argument('--account', required=True)
    publish.add_argument('--container', required=True)
    publish.add_argument('--manifest', required=True, type=Path)
    publish.add_argument('--expected-etag', type=Path)
    options = parser.parse_args(argv)
    try:
        if options.command == 'validate':
            validate_manifest(_load_json(options.manifest))
            print('Release manifest is valid')
            return 0
        if options.command == 'create-manifest':
            configuration = _load_json(options.configuration)
            schema = _load_json(options.schema_compatibility)
            manifest = {
                'schema_version': SCHEMA_VERSION,
                'source_sha': options.source_sha,
                'workflow_run_id': options.run_id,
                'workflow_run_attempt': options.run_attempt,
                'image_digest': options.image_digest,
                'frontend_blob': options.frontend_blob,
                'frontend_sha256': sha256_file(options.frontend_archive),
                'configuration': configuration,
                'release_configuration_sha256': hashlib.sha256(canonical_json(configuration)).hexdigest(),
                'schema_compatibility': schema,
            }
            validate_manifest(manifest)
            options.output.parent.mkdir(parents=True, exist_ok=True)
            options.output.write_bytes(canonical_json(manifest))
            print('Release manifest created')
            return 0
        if options.command == 'check-what-if':
            destructive = has_destructive_infrastructure_change(_load_json(options.path))
            result = f'destructive={str(destructive).lower()}\n'
            if options.output:
                options.output.parent.mkdir(parents=True, exist_ok=True)
                options.output.write_text(result, encoding='utf-8')
            sys.stdout.write(result)
            return 1 if destructive else 0
        if options.command == 'decide':
            good = _load_json(options.last_good) if options.last_good else None
            allowed, reason = recovery_decision(
                _load_json(options.candidate), good,
                destructive_changes=options.destructive_changes,
                attempt=options.attempt,
            )
            print(f'eligible={str(allowed).lower()}')
            print(f'reason={reason}')
            return 0
        if options.command == 'manual-decision':
            allowed, reason = manual_recovery_decision(
                _load_json(options.target), _load_json(options.current),
            )
            print(f'eligible={str(allowed).lower()}')
            print(f'reason={reason}')
            return 0
        token = os.environ.get('AZURE_STORAGE_OAUTH_TOKEN', '')
        store = AzureBlobStore(options.account, options.container, token)
        if options.command == 'blob-put':
            body = options.file.read_bytes()
            try:
                store.put(options.blob, body, etag=options.if_match, create_only=options.create_only,
                          content_type='application/json' if options.file.suffix == '.json'
                          else 'application/octet-stream')
            except ReleaseStateError as error:
                if not (options.create_only and options.idempotent
                        and str(error) in ('Release state changed concurrently; refusing stale update',
                                           'Release blob already exists')):
                    raise
                existing, _etag = store.get(options.blob)
                if existing != body:
                    raise ReleaseStateError('Immutable release blob already exists with different content') from error
            print('Blob write succeeded')
            return 0
        if options.command == 'publish-last-good':
            candidate = _load_json(options.manifest)
            validate_manifest(candidate)
            existing_body, current_etag = store.get('last-known-good.json')
            if existing_body is not None:
                existing = json.loads(existing_body.decode('utf-8'))
                validate_manifest(existing)
                if existing['source_sha'] == candidate['source_sha']:
                    print('Release is already last known good; state unchanged')
                    return 0
            expected = options.expected_etag.read_text(encoding='utf-8').strip() if options.expected_etag else ''
            if expected != (current_etag or ''):
                raise ReleaseStateError('Last-known-good changed during this release; refusing stale update')
            store.put('last-known-good.json', canonical_json(candidate), etag=current_etag,
                      create_only=current_etag is None, content_type='application/json')
            print('Last-known-good state advanced after successful observation')
            return 0
        body, etag = store.get(options.blob)
        if body is None:
            if options.command == 'blob-get' and options.allow_missing:
                if options.etag_output:
                    options.etag_output.parent.mkdir(parents=True, exist_ok=True)
                    options.etag_output.write_text('', encoding='utf-8')
                print('Blob does not exist; no prior release is recorded')
                return 0
            print('Blob does not exist', file=sys.stderr)
            return 2
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_bytes(body)
        if options.etag_output:
            options.etag_output.parent.mkdir(parents=True, exist_ok=True)
            options.etag_output.write_text(etag or '', encoding='utf-8')
        print(f'Blob downloaded; etag={etag or "unavailable"}')
        return 0
    except (OSError, ReleaseStateError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
