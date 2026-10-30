#!/usr/bin/env python3
"""Compile the pinned Bicep baseline and check its environment contracts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.34.44'


def run(*args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True).stdout


def deployment_ready(environment, parameters):
    """Reject placeholders before an operator invokes a deployment."""
    if parameters['environment']['value'] != environment:
        raise ValueError('Parameter file does not match the requested environment')
    for field in ('location', 'owner', 'costCenter'):
        value = parameters[field]['value']
        if not isinstance(value, str) or not value.strip() or value.strip().upper() == 'UNRESOLVED':
            raise ValueError(f'{field} must be supplied before deployment')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment-ready', choices=['dev', 'test', 'prod'],
                        help='also reject unresolved inputs for this environment')
    options = parser.parse_args()
    binary = os.environ.get('BICEP', 'bicep')
    version = run(binary, '--version')
    if not version.startswith('Bicep CLI version ' + VERSION + ' '):
        raise ValueError('Expected Bicep CLI version ' + VERSION)
    run(binary, 'lint', 'infra/main.bicep')
    template = json.loads(run(binary, 'build', 'infra/main.bicep', '--stdout'))
    allowed = template['parameters']['environment']['allowedValues']
    if allowed != ['dev', 'test', 'prod']:
        raise ValueError('Unexpected environment allowlist')
    for env in allowed:
        params = json.loads(run(binary, 'build-params',
                                f'infra/environments/{env}.bicepparam', '--stdout'))
        values = json.loads(params['parametersJson'])['parameters']
        if values['environment']['value'] != env:
            raise ValueError(f'{env} parameter file selects a different environment')
        if options.deployment_ready == env:
            deployment_ready(env, values)
    # Compiler must reject an invalid environment rather than only warn.
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / 'invalid.bicepparam'
        bad.write_text("using '" + str(ROOT / 'infra/main.bicep') + "'\nparam environment = 'invalid'\nparam location = 'westeurope'\nparam owner = 'test'\nparam costCenter = 'test'\n")
        result = subprocess.run([binary, 'build-params', str(bad), '--stdout'],
                                cwd=ROOT, text=True, capture_output=True)
        if result.returncode == 0:
            raise ValueError('Invalid environment unexpectedly compiled')
    print('Bicep baseline checks passed')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Bicep check failed: {exc}', file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr, file=sys.stderr)
        sys.exit(1)
