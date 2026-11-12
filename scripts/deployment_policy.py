#!/usr/bin/env python3
"""Small, deterministic policy checks used by the trusted release workflow."""
import argparse
import json
import os
from pathlib import Path
import re
import sys


def verify_current_source(release_sha, main_sha):
    """Reject a queued deployment after a newer main commit has landed."""
    if (not isinstance(release_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', release_sha)
            or not isinstance(main_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', main_sha)
            or release_sha != main_sha):
        raise ValueError('Release source is not the current main commit')


def verify_artifact_manifest(manifest, source_sha, run_id, run_attempt):
    """Require artifact provenance to match one completed CI run exactly."""
    if not isinstance(manifest, dict):
        raise ValueError('Image artifact manifest must be an object')
    schema_version = manifest.get('schema_version')
    actual_run_id = manifest.get('workflow_run_id')
    actual_attempt = manifest.get('workflow_run_attempt')
    if (isinstance(schema_version, bool) or schema_version != 1
            or manifest.get('source_sha') != source_sha
            or not isinstance(actual_run_id, int) or isinstance(actual_run_id, bool)
            or actual_run_id != run_id
            or not isinstance(actual_attempt, int) or isinstance(actual_attempt, bool)
            or actual_attempt != run_attempt
            or manifest.get('image_tag') != f'phonebuddy-release-test:{source_sha}'
            or manifest.get('image_archive') != 'release-test.tar.gz'):
        raise ValueError('Image artifact does not match the successful main CI run')


def existing_image_is_reusable(write_enabled, local_image_id, remote_image_id):
    """Permit duplicate source-SHA pushes only for the same locked image."""
    return (isinstance(write_enabled, str) and write_enabled.strip().casefold() == 'false'
            and isinstance(local_image_id, str) and bool(local_image_id.strip())
            and isinstance(remote_image_id, str) and bool(remote_image_id.strip())
            and local_image_id == remote_image_id)


def recovery_required(deploy_outcome, deploy_succeeded, observe_outcome):
    """Isolate only a partial Bicep apply or failed post-deploy observation."""
    if deploy_outcome == 'failure':
        return True
    return deploy_succeeded == 'true' and observe_outcome == 'failure'


def active_candidate_revision_names(revisions, release_version):
    """Select only active revisions that serve the candidate release version."""
    if not isinstance(revisions, list) or not release_version:
        raise ValueError('Revision data and release version are required')
    candidates = set()
    for revision in revisions:
        if not isinstance(revision, dict):
            continue
        properties = revision.get('properties')
        if not isinstance(properties, dict) or properties.get('active') is not True:
            continue
        name = revision.get('name')
        template = properties.get('template')
        containers = template.get('containers') if isinstance(template, dict) else None
        if not isinstance(name, str) or not name or not isinstance(containers, list):
            continue
        for container in containers:
            if not isinstance(container, dict) or not isinstance(container.get('env'), list):
                continue
            if any(isinstance(item, dict) and item.get('name') == 'RELEASE_VERSION'
                   and item.get('value') == release_version for item in container['env']):
                candidates.add(name)
                break
    return sorted(candidates)


def matching_revision_names(revisions, release_version, image_digest):
    """Return revisions bound to both the release source and immutable image."""
    if not isinstance(revisions, list) or not release_version or not image_digest:
        raise ValueError('Revision data, release version, and image digest are required')
    expected_image_suffix = f'@sha256:{image_digest}'
    candidates = []
    for revision in revisions:
        if not isinstance(revision, dict):
            continue
        properties = revision.get('properties')
        name = revision.get('name')
        template = properties.get('template') if isinstance(properties, dict) else None
        containers = template.get('containers') if isinstance(template, dict) else None
        if not isinstance(name, str) or not name or not isinstance(containers, list):
            continue
        matches = False
        for container in containers:
            if not isinstance(container, dict) or not isinstance(container.get('env'), list):
                continue
            version_matches = any(
                isinstance(item, dict) and item.get('name') == 'RELEASE_VERSION'
                and item.get('value') == release_version for item in container['env']
            )
            image = container.get('image')
            if version_matches and isinstance(image, str) and image.endswith(expected_image_suffix):
                matches = True
                break
        if matches:
            candidates.append((str(properties.get('createdTime', '')), name,
                               properties.get('active') is True))
    return [name for _, name, _ in sorted(candidates, reverse=True)]


def active_matching_revision_names(revisions, release_version, image_digest):
    """Return only active revisions with the exact source and immutable image."""
    matching = set(matching_revision_names(revisions, release_version, image_digest))
    return sorted(
        revision['name'] for revision in revisions
        if isinstance(revision, dict) and revision.get('name') in matching
        and isinstance(revision.get('properties'), dict)
        and revision['properties'].get('active') is True
    )


def active_revision_action(revisions, release_version, image_digest):
    """Require an active revision bound to the exact source and image."""
    active = active_matching_revision_names(revisions, release_version, image_digest)
    if active:
        return 'active', active[0]
    return 'missing', ''


def recovery_revision_action(revisions, release_version, image_digest):
    """Report the exact active revision without changing Single-mode traffic."""
    active = active_matching_revision_names(revisions, release_version, image_digest)
    if active:
        return 'keep', active[0]
    return 'none', ''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)

    manifest = commands.add_parser('verify-manifest')
    manifest.add_argument('--path', required=True, type=Path)
    manifest.add_argument('--source-sha', required=True)
    manifest.add_argument('--run-id', required=True, type=int)
    manifest.add_argument('--run-attempt', required=True, type=int)

    image = commands.add_parser('verify-existing-image')
    image.add_argument('--write-enabled', required=True)
    image.add_argument('--local-image-id', required=True)
    image.add_argument('--remote-image-id', required=True)

    recovery = commands.add_parser('recovery-required')
    recovery.add_argument('--deploy-outcome', required=True)
    recovery.add_argument('--deploy-succeeded', required=True)
    recovery.add_argument('--observe-outcome', required=True)

    revisions = commands.add_parser('candidate-revisions')
    revisions.add_argument('--path', required=True, type=Path)
    revisions.add_argument('--release-version', required=True)

    ensure_revision = commands.add_parser('ensure-active-revision')
    ensure_revision.add_argument('--path', required=True, type=Path)
    ensure_revision.add_argument('--release-version', required=True)
    ensure_revision.add_argument('--image-digest', required=True)

    recovery_plan = commands.add_parser('recovery-revision-action')
    recovery_plan.add_argument('--path', required=True, type=Path)
    recovery_plan.add_argument('--release-version', required=True)
    recovery_plan.add_argument('--image-digest', required=True)

    source = commands.add_parser('verify-current-source')
    source.add_argument('--release-sha', required=True)
    source.add_argument('--main-sha', required=True)

    options = parser.parse_args(argv)
    try:
        if options.command == 'verify-manifest':
            verify_artifact_manifest(
                json.loads(options.path.read_text(encoding='utf-8')),
                options.source_sha, options.run_id, options.run_attempt,
            )
            print('Image artifact provenance matches its source run')
            return 0
        if options.command == 'verify-existing-image':
            if not existing_image_is_reusable(
                    options.write_enabled, options.local_image_id, options.remote_image_id):
                raise ValueError('Existing source-SHA image is mutable or does not match the CI artifact')
            print('Existing source-SHA image is locked and matches the CI artifact')
            return 0
        if options.command == 'candidate-revisions':
            result = active_candidate_revision_names(
                json.loads(options.path.read_text(encoding='utf-8')),
                options.release_version,
            )
            for name in result:
                print(name)
            return 0
        if options.command == 'ensure-active-revision':
            revisions_data = json.loads(options.path.read_text(encoding='utf-8'))
            action, name = active_revision_action(
                revisions_data, options.release_version, options.image_digest,
            )
            print(f'{action}\t{name}')
            return 0
        if options.command == 'recovery-revision-action':
            action, name = recovery_revision_action(
                json.loads(options.path.read_text(encoding='utf-8')),
                options.release_version, options.image_digest,
            )
            print(f'{action}\t{name}')
            return 0
        if options.command == 'verify-current-source':
            verify_current_source(options.release_sha, options.main_sha)
            print('Release source is the current main commit')
            return 0
        required = recovery_required(
            options.deploy_outcome, options.deploy_succeeded, options.observe_outcome,
        )
        value = f'required={str(required).lower()}\n'
        output = os.environ.get('GITHUB_OUTPUT')
        if output:
            with open(output, 'a', encoding='utf-8') as target:
                target.write(value)
        else:
            sys.stdout.write(value)
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
