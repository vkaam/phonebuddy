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
FOUNDATION_DEPLOYMENT_NAME = (
    "[format('phonebuddy-{0}-{1}-foundation', parameters('environment'), "
    "parameters('location'))]"
)
FOUNDATION_RESOURCE_GROUP_NAME = (
    "[format('rg-pb-{0}-{1}-foundation', parameters('environment'), "
    "parameters('location'))]"
)
FOUNDATION_RESOURCE_GROUP_OUTPUT = (
    "[reference(subscriptionResourceId('Microsoft.Resources/deployments', "
    "format('phonebuddy-{0}-{1}-foundation', parameters('environment'), "
    "parameters('location'))), "
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


def expected_resource_group_names(locations):
    """Build the stable environment- and region-qualified foundation names."""
    if set(locations) != set(ENVIRONMENTS):
        raise ValueError('Locations must be supplied for every environment')
    return {
        environment: f'rg-pb-{environment}-{locations[environment]}-foundation'
        for environment in ENVIRONMENTS
    }


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


def validate_hosting(template):
    """Check security-critical defaults in the compiled pilot template."""
    resources = {r['type']: r for r in template.get('resources', [])}
    required = {'Microsoft.ContainerRegistry/registries', 'Microsoft.KeyVault/vaults',
                'Microsoft.Web/staticSites', 'Microsoft.ManagedIdentity/userAssignedIdentities',
                'Microsoft.Authorization/roleAssignments', 'Microsoft.App/managedEnvironments',
                'Microsoft.App/containerApps', 'Microsoft.OperationalInsights/workspaces',
                'Microsoft.Insights/components', 'Microsoft.Insights/diagnosticSettings',
                'Microsoft.Insights/scheduledQueryRules'}
    if not required.issubset(resources):
        raise ValueError('Hosting template is missing required resources')
    registry = resources['Microsoft.ContainerRegistry/registries']['properties']
    vault = resources['Microsoft.KeyVault/vaults']['properties']
    if registry.get('adminUserEnabled') is not False:
        raise ValueError('Registry administrator must be disabled')
    if (vault.get('enableRbacAuthorization') is not True
            or vault.get('publicNetworkAccess') != 'Disabled'
            or vault.get('enablePurgeProtection') is not True):
        raise ValueError('Vault must use RBAC, disable public access and protect against purge')
    parameters = template['parameters']
    digest = parameters['imageDigest']
    if digest.get('minLength') != 64 or digest.get('maxLength') != 64 or 'defaultValue' in digest:
        raise ValueError('Image digest must be supplied as 64 characters')
    if parameters['releaseVersion'].get('minLength') != 1 or 'defaultValue' in parameters['releaseVersion']:
        raise ValueError('A nonempty release version must be supplied')
    image = resources['Microsoft.App/containerApps']['properties']['template']['containers'][0]['image']
    expected_image = ("[format('{0}/release-test@sha256:{1}', "
                      "reference(resourceId('Microsoft.ContainerRegistry/registries', "
                      "format('pb{0}{1}', parameters('environment'), variables('suffix'))), "
                      "'2023-07-01').loginServer, parameters('imageDigest'))]")
    if image != expected_image:
        raise ValueError('Workload image must use the provisioned registry and digest')
    if parameters['deployWorkload'].get('defaultValue') is not False:
        raise ValueError('Workload deployment must be opt-in')
    workspace = resources['Microsoft.OperationalInsights/workspaces']['properties']
    if workspace.get('retentionInDays') != 30:
        raise ValueError('Health telemetry retention must be explicitly bounded to 30 days')
    insights = resources['Microsoft.Insights/components']
    insight_properties = insights.get('properties', {})
    if (insights.get('kind') != 'web'
            or insight_properties.get('IngestionMode') != 'LogAnalytics'
            or 'Microsoft.OperationalInsights/workspaces'
            not in insight_properties.get('WorkspaceResourceId', '')):
        raise ValueError('Application Insights must use the bounded Log Analytics workspace')
    alerts = [resource for resource in template.get('resources', [])
              if resource.get('type') == 'Microsoft.Insights/scheduledQueryRules']
    if len(alerts) != 3 or any(resource.get('kind') != 'LogAlert'
                              or resource.get('properties', {}).get('evaluationFrequency') != 'PT5M'
                              or resource.get('properties', {}).get('windowSize') != 'PT5M'
                              for resource in alerts):
        raise ValueError('Expected three five-minute health telemetry log alerts')
    alert_queries = '\n'.join(
        condition.get('query', '')
        for resource in alerts
        for condition in resource.get('properties', {}).get('criteria', {}).get('allOf', [])
    ) + json.dumps(template.get('variables', {}), sort_keys=True)
    for signal in ('health_request', 'health.status', 'health.duration_ms'):
        if signal not in alert_queries:
            raise ValueError(f'Health alert queries must cover {signal}')
    if set(template.get('outputs', {})) != {
            'registryName', 'registryServer', 'workloadUrl', 'logWorkspaceName', 'insightsName'}:
        raise ValueError('Hosting outputs must contain only public resource identifiers')


def validate_what_if(result):
    """Fail closed when Azure returns no usable preview or an uncertain change."""
    if not isinstance(result, dict) or result.get('status') != 'Succeeded' or result.get('error'):
        raise ValueError('What-if did not report success')
    if result.get('potentialChanges') or result.get('diagnostics'):
        raise ValueError('What-if reported unverified changes or diagnostics')
    changes = result.get('changes')
    if not isinstance(changes, list) or not changes:
        raise ValueError('Missing what-if changes')
    allowed = {'Create', 'Modify', 'NoChange'}
    if any(not isinstance(change, dict) or change.get('changeType') not in allowed
           or not change.get('resourceId') for change in changes):
        raise ValueError('Incomplete or unexpected what-if result')
    return changes


def validate_quality_evidence(pages, expected_sha):
    """Require the latest GitHub Actions Quality check for the exact source."""
    if (not isinstance(pages, list) or not pages or not expected_sha
            or any(not isinstance(page, dict) or not isinstance(page.get('check_runs'), list)
                   for page in pages)):
        raise ValueError('Missing Quality check evidence')
    runs = [run for page in pages for run in page['check_runs']
            if isinstance(run, dict) and run.get('name') == 'Quality'
            and run.get('head_sha') == expected_sha
            and isinstance(run.get('app'), dict)
            and run['app'].get('slug') == 'github-actions']
    if not runs or any(not isinstance(run.get('id'), int) for run in runs):
        raise ValueError('Missing Quality check for this commit')
    latest = max(runs, key=lambda run: run['id'])
    if latest.get('status') != 'completed' or latest.get('conclusion') != 'success':
        raise ValueError('Latest Quality check is not successful')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--what-if-result', type=Path, help='validate an Azure what-if JSON result')
    parser.add_argument('--quality-evidence', type=Path, help='validate GitHub check-run evidence')
    parser.add_argument('--expected-sha', help='expected commit for Quality evidence')
    parser.add_argument('--deployment-ready', choices=['dev', 'test', 'prod'],
                        help='also reject unresolved inputs for this environment')
    options = parser.parse_args()
    if options.quality_evidence:
        validate_quality_evidence(json.loads(options.quality_evidence.read_text()), options.expected_sha)
        print('Exact-commit Quality check passed')
        return
    if options.what_if_result:
        changes = validate_what_if(json.loads(options.what_if_result.read_text()))
        counts = {kind: sum(item['changeType'] == kind for item in changes)
                  for kind in ('Create', 'Modify', 'NoChange')}
        print(json.dumps({'whatIfChangeCounts': counts}))
        return
    binary = os.environ.get('BICEP', 'bicep')
    version = run(binary, '--version')
    if not version.startswith('Bicep CLI version ' + VERSION + ' '):
        raise ValueError('Expected Bicep CLI version ' + VERSION)
    run(binary, 'lint', 'infra/main.bicep')
    run(binary, 'lint', 'infra/hosting.bicep')
    hosting = json.loads(run(binary, 'build', 'infra/hosting.bicep', '--stdout'))
    validate_hosting(hosting)
    template = json.loads(run(binary, 'build', 'infra/main.bicep', '--stdout'))
    allowed = template['parameters']['environment']['allowedValues']
    if allowed != list(ENVIRONMENTS):
        raise ValueError('Unexpected environment allowlist')
    validate_foundation_isolation(template)
    locations = {}
    for env in allowed:
        params = json.loads(run(binary, 'build-params',
                                f'infra/environments/{env}.bicepparam', '--stdout'))
        values = json.loads(params['parametersJson'])['parameters']
        if values['environment']['value'] != env:
            raise ValueError(f'{env} parameter file selects a different environment')
        location = values['location']['value']
        locations[env] = location
        if options.deployment_ready == env:
            deployment_ready(env, values)
    resource_group_names = expected_resource_group_names(locations)
    if len(set(resource_group_names.values())) != len(ENVIRONMENTS):
        raise ValueError('Foundation resource-group names must be unique by environment and region')
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
