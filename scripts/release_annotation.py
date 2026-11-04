#!/usr/bin/env python3
"""Write a source-bound deployment annotation to Application Insights."""
import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import uuid


RESOURCE_ID = re.compile(
    r'^/subscriptions/[0-9a-f-]+/resourceGroups/[^/]+/'
    r'providers/Microsoft\.Insights/components/[^/]+$', re.IGNORECASE
)
ENVIRONMENTS = ('dev', 'test')


def create_annotation(resource_id, environment, release_version, commit_sha, workflow_ref,
                      run=subprocess.run):
    if not RESOURCE_ID.fullmatch(resource_id):
        raise ValueError('Application Insights resource ID is invalid')
    if environment not in ENVIRONMENTS:
        raise ValueError('Release annotations are limited to dev and test')
    if not release_version or len(release_version) > 128:
        raise ValueError('Release version must be between 1 and 128 characters')
    if not re.fullmatch(r'[0-9a-f]{40,64}', commit_sha):
        raise ValueError('Commit SHA must be a full hexadecimal object ID')
    if not workflow_ref or len(workflow_ref) > 256:
        raise ValueError('Workflow reference is required and must be bounded')

    payload = {
        'Id': str(uuid.uuid4()),
        'AnnotationName': f'phonebuddy-{environment}-{release_version}',
        'EventTime': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'Category': 'Deployment',
        'Properties': json.dumps({
            'Environment': environment,
            'ReleaseVersion': release_version,
            'SourceCommit': commit_sha,
            'Workflow': workflow_ref,
        }, separators=(',', ':'), sort_keys=True),
    }
    run([
        'az', 'rest', '--method', 'put',
        '--url', f'https://management.azure.com{resource_id}/Annotations?api-version=2015-05-01',
        '--headers', 'Content-Type=application/json',
        '--body', json.dumps(payload, separators=(',', ':')),
        '--output', 'none',
    ], check=True, capture_output=True, text=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resource-id', required=True)
    parser.add_argument('--environment', required=True, choices=ENVIRONMENTS)
    parser.add_argument('--release-version', required=True)
    parser.add_argument('--commit-sha', required=True)
    parser.add_argument('--workflow-ref', required=True)
    args = parser.parse_args(argv)
    try:
        create_annotation(args.resource_id, args.environment, args.release_version,
                          args.commit_sha, args.workflow_ref)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.error(f'Could not record release annotation: {error}')
    print('Application Insights release annotation recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
