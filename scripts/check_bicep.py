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
ENVIRONMENTS = ('dev', 'test', 'prod')
FOUNDATION_DEPLOYMENT_NAME = "[format('phonebuddy-{0}-foundation', parameters('environment'))]"
FOUNDATION_RESOURCE_GROUP_NAME = "[format('rg-pb-{0}-foundation', parameters('environment'))]"
FOUNDATION_RESOURCE_GROUP_OUTPUT = (
    "[reference(subscriptionResourceId('Microsoft.Resources/deployments', "
    "format('phonebuddy-{0}-foundation', parameters('environment'))), "
    "'2022-09-01').outputs.resourceGroupName.value]"
)


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


def validate_foundation_isolation(template):
    """Require one environment-scoped resource group and a secret-free output."""
    deployments = [resource for resource in template.get('resources', [])
                   if resource.get('type') == 'Microsoft.Resources/deployments']
    if len(deployments) != 1:
        raise ValueError('Expected exactly one environment foundation deployment')
    deployment = deployments[0]
    if deployment.get('name') != FOUNDATION_DEPLOYMENT_NAME:
        raise ValueError('Foundation deployment name must include the environment')
    module_parameters = deployment.get('properties', {}).get('parameters', {})
    if module_parameters.get('environment') != {
            'value': "[parameters('environment')]"}:
        raise ValueError('Foundation module must forward the selected environment')
    expected_module_parameters = {
        name: {'value': f"[parameters('{name}')]"}
        for name in ('environment', 'location', 'owner', 'costCenter')
    }
    if module_parameters != expected_module_parameters:
        raise ValueError('Foundation module inputs must forward only the selected environment values')

    nested = deployment.get('properties', {}).get('template', {})
    if set(nested.get('parameters', {})) != {'environment', 'location', 'owner', 'costCenter'}:
        raise ValueError('Foundation parameters must not contain secrets or unrelated inputs')
    groups = [resource for resource in nested.get('resources', [])
              if resource.get('type') == 'Microsoft.Resources/resourceGroups']
    if len(groups) != 1 or groups[0].get('name') != FOUNDATION_RESOURCE_GROUP_NAME:
        raise ValueError('Foundation resource group name must include the environment')
    if groups[0].get('tags', {}).get('environment') != "[parameters('environment')]":
        raise ValueError('Foundation resource group must be tagged with its environment')

    expected_outputs = {'resourceGroupName'}
    if set(template.get('outputs', {})) != expected_outputs:
        raise ValueError('Foundation outputs may expose only the resource-group name')
    root_output = template['outputs']['resourceGroupName']
    if root_output.get('type') != 'string' or root_output.get('value') != FOUNDATION_RESOURCE_GROUP_OUTPUT:
        raise ValueError('Foundation output must contain only the environment resource-group name')
    if set(nested.get('outputs', {})) != expected_outputs:
        raise ValueError('Foundation module outputs may expose only the resource-group name')
    if nested['outputs']['resourceGroupName'].get('value') != FOUNDATION_RESOURCE_GROUP_NAME:
        raise ValueError('Foundation output must resolve to the environment resource group')
    return {environment: f'rg-pb-{environment}-foundation' for environment in ENVIRONMENTS}


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
    if allowed != list(ENVIRONMENTS):
        raise ValueError('Unexpected environment allowlist')
    resource_group_names = validate_foundation_isolation(template)
    if len(set(resource_group_names.values())) != len(ENVIRONMENTS):
        raise ValueError('Foundation resource-group names must be unique per environment')
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
