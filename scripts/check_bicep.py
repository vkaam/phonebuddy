#!/usr/bin/env python3
"""Compile the pinned Bicep baseline and check its environment contracts."""
import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.34.44'
ENVIRONMENTS = ('dev', 'test', 'prod')
FOUNDRY_API_VERSION = '2024-10-01'
FOUNDRY_MODEL = {
    'dev': ('gpt-5-mini', '2025-08-07', 'GlobalStandard', 10),
    'test': ('gpt-5-mini', '2025-08-07', 'GlobalStandard', 20),
    'prod': ('gpt-5-mini', '2025-08-07', 'GlobalStandard', 50),
}
FOUNDATION_DEPLOYMENT_NAME = (
    "[format('phonebuddy-{0}-{1}-foundation', parameters('environment'), "
    "parameters('location'))]"
)
DATA_PLATFORM_DEPLOYMENT_NAME = (
    "[format('pb-{0}-{1}-data', parameters('environment'), "
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
    for field in ('location', 'owner', 'costCenter', 'sqlAdminObjectId', 'sqlAdminLogin',
                  'foundryModelName', 'foundryModelVersion'):
        value = parameters[field]['value']
        if not isinstance(value, str) or not value.strip() or value.strip().upper() == 'UNRESOLVED':
            raise ValueError(f'{field} must be supplied before deployment')


def validate_foundry_model_evidence(models, capacities, location, model_name,
                                   model_version, deployment_sku, requested_capacity,
                                   today=None):
    """Reject unknown, retired, unlisted or capacity-short regional model configs."""
    today = today or date.today()
    if not isinstance(models, dict) or not isinstance(models.get('value'), list):
        raise ValueError('Missing Foundry model catalog evidence')
    if not isinstance(capacities, dict) or not isinstance(capacities.get('value'), list):
        raise ValueError('Missing Foundry model capacity evidence')
    matches = []
    for item in models['value']:
        model = item.get('model', {}) if isinstance(item, dict) else {}
        if (model.get('format') == 'OpenAI' and model.get('name') == model_name
                and model.get('version') == model_version):
            if str(item.get('location', '')).lower() != location.lower():
                raise ValueError('Foundry catalog returned the pinned model outside the selected region; no geography fallback is allowed')
            matches.append(model)
    if not matches:
        raise ValueError('Pinned Foundry model/version is missing in the selected region')
    lifecycle = {(item.get('lifecycleStatus'),
                  json.dumps(item.get('deprecation'), sort_keys=True)) for item in matches}
    if len(lifecycle) != 1:
        raise ValueError('Pinned Foundry model/version has conflicting lifecycle evidence')
    model = dict(matches[0])
    sku_evidence = {}
    for item in matches:
        for sku in item.get('skus', []):
            if not isinstance(sku, dict) or not sku.get('name'):
                raise ValueError('Foundry model contains malformed SKU lifecycle evidence')
            sku_key = (sku['name'].lower(), json.dumps(sku, sort_keys=True))
            sku_evidence[sku_key] = sku
    model['skus'] = list(sku_evidence.values())
    if model.get('lifecycleStatus') != 'GenerallyAvailable':
        raise ValueError('Foundry model must be GenerallyAvailable')
    deprecation = model.get('deprecation', {}).get('inference')
    if not deprecation:
        raise ValueError('Foundry model inference lifecycle date is missing')
    try:
        if datetime.fromisoformat(deprecation.replace('Z', '+00:00')).date() <= today:
            raise ValueError('Foundry model version is retired or expires today')
    except (TypeError, ValueError) as exc:
        if str(exc) == 'Foundry model version is retired or expires today':
            raise
        raise ValueError('Foundry model inference lifecycle date is invalid') from None

    skus = model.get('skus')
    if not isinstance(skus, list):
        raise ValueError('Foundry model deployment SKU lifecycle evidence is missing')
    sku_entries = [item for item in skus if isinstance(item, dict)
                   and item.get('name', '').lower() == deployment_sku.lower()]
    if len(sku_entries) != 1:
        raise ValueError(f'Foundry model is not available on the {deployment_sku} SKU')
    sku = sku_entries[0]
    sku_retirement = sku.get('deprecationDate')
    if sku_retirement and datetime.fromisoformat(sku_retirement.replace('Z', '+00:00')).date() <= today:
        raise ValueError('Foundry model SKU is retired or expires today')
    capacity_config = sku.get('capacity')
    if not isinstance(capacity_config, dict):
        raise ValueError('Foundry model SKU capacity rules are missing')
    minimum = capacity_config.get('minimum', capacity_config.get('default'))
    maximum = capacity_config.get('maximum')
    step = capacity_config.get('step', 1)
    if (not all(isinstance(value, int) for value in (minimum, maximum, step))
            or step <= 0 or requested_capacity < minimum or requested_capacity > maximum
            or (requested_capacity - minimum) % step):
        raise ValueError('Requested Foundry model capacity violates the regional SKU limits')

    regional = [item for item in capacities['value'] if isinstance(item, dict)
                and str(item.get('location', '')).lower() == location.lower()
                and isinstance(item.get('properties'), dict)
                and item['properties'].get('skuName', '').lower() == deployment_sku.lower()]
    available = [item['properties'].get('availableCapacity') for item in regional]
    if (not available or any(not isinstance(value, int) for value in available)
            or max(available) < requested_capacity):
        raise ValueError('Selected region lacks the requested Foundry model capacity; no geography fallback is allowed')
    return {'location': location, 'model': model_name, 'version': model_version,
            'lifecycleStatus': model['lifecycleStatus'], 'sku': deployment_sku,
            'requestedCapacity': requested_capacity, 'availableCapacity': max(available)}


def validate_data_platform(template):
    """Check critical data-service defaults in the compiled resource-group template."""
    by_type = {}
    for resource in template.get('resources', []):
        by_type.setdefault(resource.get('type'), []).append(resource)
    required = {
        'Microsoft.Sql/servers',
        'Microsoft.Sql/servers/administrators',
        'Microsoft.Sql/servers/azureADOnlyAuthentications',
        'Microsoft.Sql/servers/databases',
        'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies',
        'Microsoft.Storage/storageAccounts',
        'Microsoft.Storage/storageAccounts/blobServices',
        'Microsoft.Storage/storageAccounts/blobServices/containers',
        'Microsoft.ServiceBus/namespaces',
        'Microsoft.ServiceBus/namespaces/queues',
        'Microsoft.ManagedIdentity/userAssignedIdentities',
        'Microsoft.CognitiveServices/accounts',
        'Microsoft.CognitiveServices/accounts/projects',
        'Microsoft.CognitiveServices/accounts/deployments',
        'Microsoft.Authorization/roleAssignments',
    }
    if not required.issubset(by_type):
        raise ValueError('Data platform template is missing required Azure resources')
    sql_auth = by_type['Microsoft.Sql/servers/azureADOnlyAuthentications'][0]['properties']
    if sql_auth.get('azureADOnlyAuthentication') is not True:
        raise ValueError('SQL server must require Microsoft Entra authentication')
    storage = by_type['Microsoft.Storage/storageAccounts'][0]['properties']
    if (storage.get('allowBlobPublicAccess') is not False
            or storage.get('allowSharedKeyAccess') is not False
            or storage.get('supportsHttpsTrafficOnly') is not True):
        raise ValueError('Blob Storage must disable public blobs and Shared Key and require HTTPS')
    blob = by_type['Microsoft.Storage/storageAccounts/blobServices'][0]['properties']
    for policy in ('deleteRetentionPolicy', 'containerDeleteRetentionPolicy'):
        if blob.get(policy, {}).get('enabled') is not True:
            raise ValueError('Blob and container soft-delete retention must be enabled')
    bus = by_type['Microsoft.ServiceBus/namespaces'][0]
    if bus.get('properties', {}).get('disableLocalAuth') is not True:
        raise ValueError('Service Bus must disable SAS/local authentication')
    queues = [resource['properties']
              for resource in by_type['Microsoft.ServiceBus/namespaces/queues']]
    if any(queue.get('deadLetteringOnMessageExpiration') is not True
           or not isinstance(queue.get('maxDeliveryCount'), int)
           or queue['maxDeliveryCount'] < 1 for queue in queues):
        raise ValueError('Service Bus queue must enable dead-letter handling and a delivery limit')
    accounts = by_type['Microsoft.CognitiveServices/accounts']
    speech = next((item for item in accounts if item.get('kind') == 'SpeechServices'), None)
    foundry = next((item for item in accounts if item.get('kind') == 'AIServices'), None)
    if not speech or not foundry:
        raise ValueError('Speech and Foundry accounts are both required')
    for account in (speech, foundry):
        if account.get('properties', {}).get('disableLocalAuth') is not True:
            raise ValueError('Speech and Foundry must disable key-based local authentication')
    deployment = by_type['Microsoft.CognitiveServices/accounts/deployments'][0]
    model = deployment.get('properties', {}).get('model', {})
    if (deployment.get('sku', {}).get('name') != 'GlobalStandard'
            or not model.get('name') or not model.get('version')
            or deployment.get('properties', {}).get('versionUpgradeOption') != 'NoAutoUpgrade'
            or deployment.get('properties', {}).get('spilloverDeploymentName')):
        raise ValueError('Foundry deployment must pin a regional model version without spillover')
    return True


def az_rest(url):
    """Read one Azure Resource Manager endpoint through the active Azure CLI identity."""
    result = subprocess.run(['az', 'rest', '--method', 'get', '--url', url,
                             '--only-show-errors'], cwd=ROOT, text=True,
                            capture_output=True, check=True)
    return json.loads(result.stdout)


def foundry_preflight(subscription_id, location, model_name, model_version,
                      deployment_sku, requested_capacity):
    """Use ARM model lifecycle and capacity APIs; only the requested region may pass."""
    root = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CognitiveServices'
    models_url = f'{root}/locations/{location}/models?api-version={FOUNDRY_API_VERSION}'
    capacities_url = f'{root}/modelCapacities?{urlencode({"api-version": FOUNDRY_API_VERSION, "modelFormat": "OpenAI", "modelName": model_name, "modelVersion": model_version})}'
    return validate_foundry_model_evidence(
        az_rest(models_url), az_rest(capacities_url), location, model_name,
        model_version, deployment_sku, requested_capacity,
    )


def expected_resource_group_names(locations):
    """Build the stable environment- and region-qualified foundation names."""
    if set(locations) != set(ENVIRONMENTS):
        raise ValueError('Locations must be supplied for every environment')
    return {
        environment: f'rg-pb-{environment}-{locations[environment]}-foundation'
        for environment in ENVIRONMENTS
    }


def validate_foundation_isolation(template):
    """Require ordered environment modules and a secret-free root output."""
    deployments = [resource for resource in template.get('resources', [])
                   if resource.get('type') == 'Microsoft.Resources/deployments']
    if len(deployments) != 2:
        raise ValueError('Expected foundation and data-platform deployments')
    deployment = next((item for item in deployments
                       if item.get('name') == FOUNDATION_DEPLOYMENT_NAME), None)
    data_platform = next((item for item in deployments
                          if item.get('name') == DATA_PLATFORM_DEPLOYMENT_NAME), None)
    if not deployment or not data_platform:
        raise ValueError('Foundation deployment names must include the environment and region')
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

    expected_data_parameters = {
        'environment', 'location', 'owner', 'costCenter', 'sqlAdminObjectId',
        'sqlAdminLogin', 'foundryModelName', 'foundryModelVersion',
        'foundryModelCapacity',
    }
    if set(data_platform.get('properties', {}).get('parameters', {})) != expected_data_parameters:
        raise ValueError('Data-platform module inputs must be explicit and secret-free')
    expected_group_scope = (
        "[format('rg-pb-{0}-{1}-foundation', parameters('environment'), "
        "parameters('location'))]"
    )
    if data_platform.get('resourceGroup') != expected_group_scope:
        raise ValueError('Data-platform module must target the selected environment group')
    foundation_dependency = (
        "[subscriptionResourceId('Microsoft.Resources/deployments', "
        "format('phonebuddy-{0}-{1}-foundation', parameters('environment'), "
        "parameters('location')))]"
    )
    if foundation_dependency not in data_platform.get('dependsOn', []):
        raise ValueError('Data-platform deployment must wait for its foundation resource group')

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
                'Microsoft.App/containerApps'}
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
    if set(template.get('outputs', {})) != {'registryName', 'registryServer', 'workloadUrl'}:
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
    parser.add_argument('--foundry-preflight', choices=['dev', 'test', 'prod'],
                        help='check the pinned Foundry model lifecycle and exact regional capacity')
    parser.add_argument('--subscription-id', help='Azure subscription for live Foundry preflight')
    options = parser.parse_args()
    if options.quality_evidence:
        validate_quality_evidence(json.loads(options.quality_evidence.read_text()), options.expected_sha)
        print('Exact-commit Quality check passed')
        return
    if options.foundry_preflight:
        environment = options.foundry_preflight
        subscription_id = options.subscription_id
        if not subscription_id:
            subscription_id = run('az', 'account', 'show', '--query', 'id', '-o', 'tsv').strip()
        if not subscription_id:
            raise ValueError('Azure subscription ID is required')
        location = 'westeurope' if environment in ('dev', 'test') else 'UNRESOLVED'
        if location == 'UNRESOLVED':
            raise ValueError('Production geography is unresolved; no Foundry fallback is allowed')
        model_name, model_version, sku, capacity = FOUNDRY_MODEL[environment]
        evidence = foundry_preflight(subscription_id, location, model_name,
                                     model_version, sku, capacity)
        print(json.dumps(evidence))
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
    data_platform = json.loads(run(binary, 'build', 'infra/modules/data-platform.bicep', '--stdout'))
    validate_data_platform(data_platform)
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
