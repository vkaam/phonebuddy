#!/usr/bin/env python3
"""Compile Bicep templates and check their environment contracts."""
import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
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
FOUNDATION_RESOURCE_GROUP_OUTPUT_PATTERN = re.compile(
    r"\[reference\(subscriptionResourceId\('Microsoft\.Resources/deployments', "
    r"format\('phonebuddy-\{0\}-\{1\}-foundation', parameters\('environment'\), "
    r"parameters\('location'\)\)\), '\d{4}-\d{2}-\d{2}'\)\.outputs\.resourceGroupName\.value\]"
)
ENVIRONMENT_DIAGNOSTIC_TYPE = 'Microsoft.App/managedEnvironments'
ENVIRONMENT_DIAGNOSTIC_NAME = "format('cae-pb-{0}', parameters('environment'))"
APP_DIAGNOSTIC_TYPE = 'Microsoft.App/containerApps'
APP_DIAGNOSTIC_NAME = "format('ca-pb-{0}-release-test', parameters('environment'))"


def valid_foundation_resource_group_output(value):
    """Allow compiler-selected API versions while constraining the referenced output."""
    return (value == FOUNDATION_RESOURCE_GROUP_OUTPUT
            or isinstance(value, str)
            and FOUNDATION_RESOURCE_GROUP_OUTPUT_PATTERN.fullmatch(value) is not None)


def split_arm_function_arguments(expression, function_name):
    """Split one ARM expression's top-level arguments without splitting nested calls."""
    prefix = f'{function_name}('
    if not expression.startswith(prefix) or not expression.endswith(')'):
        return None
    body = expression[len(prefix):-1]
    arguments, start, depth, quoted, index = [], 0, 0, False, 0
    while index < len(body):
        character = body[index]
        if character == "'":
            if quoted and index + 1 < len(body) and body[index + 1] == "'":
                index += 2
                continue
            quoted = not quoted
        elif not quoted:
            if character == '(':
                depth += 1
            elif character == ')':
                depth -= 1
                if depth < 0:
                    return None
            elif character == ',' and depth == 0:
                arguments.append(body[start:index].strip())
                start = index + 1
        index += 1
    if quoted or depth != 0:
        return None
    arguments.append(body[start:].strip())
    return arguments


def has_expected_diagnostic_scope(resource, resource_type, resource_name):
    """Match compiler resourceId or full-path forms with the exact type and name."""
    scope = resource.get('scope') if isinstance(resource, dict) else None
    if not isinstance(scope, str) or not (scope.startswith('[') and scope.endswith(']')):
        return False
    expression = scope[1:-1]
    resource_id = split_arm_function_arguments(expression, 'resourceId')
    if resource_id == [f"'{resource_type}'", resource_name]:
        return True

    formatted = split_arm_function_arguments(expression, 'format')
    if not formatted or len(formatted) < 2:
        return False
    template_match = re.fullmatch(r"'((?:[^']|'')*)'", formatted[0])
    if not template_match:
        return False
    template = template_match.group(1).replace("''", "'")
    target_pattern = re.search(
        rf"(?:^|/providers/){re.escape(resource_type)}/\{{([0-9]+)\}}$", template)
    if not target_pattern:
        return False
    target_argument = int(target_pattern.group(1))
    arguments = formatted[1:]
    return target_argument < len(arguments) and arguments[target_argument] == resource_name


def run(*args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True).stdout


def environment_parameters(environment, binary=None):
    """Compile and load one environment's checked-in parameter values."""
    binary = binary or os.environ.get('BICEP', 'bicep')
    parameter_file = f'infra/environments/{environment}.bicepparam'
    compiled = json.loads(run(binary, 'build-params', parameter_file, '--stdout'))
    values = json.loads(compiled['parametersJson'])['parameters']
    if values.get('environment', {}).get('value') != environment:
        raise ValueError(f'{environment} parameter file selects a different environment')
    return values


def deployment_ready(environment, parameters, runtime_overrides=None):
    """Reject placeholders before an operator invokes a deployment."""
    runtime_overrides = runtime_overrides or {}
    if parameters['environment']['value'] != environment:
        raise ValueError('Parameter file does not match the requested environment')
    for field in ('location', 'owner', 'costCenter', 'sqlAdminObjectId', 'sqlAdminLogin',
                  'foundryModelName', 'foundryModelVersion'):
        value = runtime_overrides.get(field, parameters[field]['value'])
        if not isinstance(value, str) or not value.strip() or value.strip().upper() == 'UNRESOLVED':
            raise ValueError(f'{field} must be supplied before deployment')


def runtime_sql_admin_overrides():
    """Read SQL administrator identifiers from process environment, never from source."""
    names = {
        'sqlAdminObjectId': 'PHONEBUDDY_SQL_ADMIN_OBJECT_ID',
        'sqlAdminLogin': 'PHONEBUDDY_SQL_ADMIN_LOGIN',
    }
    return {parameter: os.environ[name] for parameter, name in names.items()
            if name in os.environ}


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
    sql_server = by_type['Microsoft.Sql/servers'][0]['properties']
    sql_auth = sql_server.get('administrators', {})
    if (sql_auth.get('administratorType') != 'ActiveDirectory'
            or sql_auth.get('principalType') != 'User'
            or sql_auth.get('azureADOnlyAuthentication') is not True
            or not sql_auth.get('login') or not sql_auth.get('sid')
            or not sql_auth.get('tenantId')
            or 'administratorLogin' in sql_server
            or 'administratorLoginPassword' in sql_server):
        raise ValueError('SQL server must be created with an Entra-only administrator')
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
    if not any('Microsoft.CognitiveServices/accounts/projects' in dependency
               for dependency in deployment.get('dependsOn', [])
               if isinstance(dependency, str)):
        raise ValueError('Foundry model deployment must wait for its project resource')
    if (deployment.get('sku', {}).get('name') != 'GlobalStandard'
            or not model.get('name') or not model.get('version')
            or deployment.get('properties', {}).get('versionUpgradeOption') != 'NoAutoUpgrade'
            or deployment.get('properties', {}).get('spilloverDeploymentName')):
        raise ValueError('Foundry deployment must pin a model version without spillover')
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
    if (root_output.get('type') != 'string'
            or not valid_foundation_resource_group_output(root_output.get('value'))):
        raise ValueError('Foundation output must contain only the environment resource-group name')
    if set(nested.get('outputs', {})) != expected_outputs:
        raise ValueError('Foundation module outputs may expose only the resource-group name')
    if nested['outputs']['resourceGroupName'].get('value') != FOUNDATION_RESOURCE_GROUP_NAME:
        raise ValueError('Foundation output must resolve to the environment resource group')


def validate_static_site_location(parameters, site):
    """Keep the default unchanged and require the site to use its override."""
    if (parameters.get('staticSiteLocation', {}).get('defaultValue') != "[parameters('location')]"
            or site.get('location') != "[parameters('staticSiteLocation')]"):
        raise ValueError('Static Web App location must default to the workload location and allow an explicit override')


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
    pull_role = resources['Microsoft.Authorization/roleAssignments']
    if (parameters.get('managePullRoleAssignment', {}).get('defaultValue') is not True
            or pull_role.get('condition') != "[parameters('managePullRoleAssignment')]"):
        raise ValueError('Pull-role assignment must be enabled for privileged bootstrap by default')
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
    if (parameters.get('deployStaticSite', {}).get('defaultValue') is not True
            or resources['Microsoft.Web/staticSites'].get('condition')
            != "[parameters('deployStaticSite')]"):
        raise ValueError('Static Web App must remain default-on with an explicit opt-out')
    validate_static_site_location(parameters, resources['Microsoft.Web/staticSites'])
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
    diagnostic_settings = [resource for resource in template['resources']
                           if resource.get('type') == 'Microsoft.Insights/diagnosticSettings']
    environment_diagnostics = next(
        (resource for resource in diagnostic_settings
         if has_expected_diagnostic_scope(
             resource, ENVIRONMENT_DIAGNOSTIC_TYPE, ENVIRONMENT_DIAGNOSTIC_NAME)), None)
    app_diagnostics = next(
        (resource for resource in diagnostic_settings
         if has_expected_diagnostic_scope(
             resource, APP_DIAGNOSTIC_TYPE, APP_DIAGNOSTIC_NAME)), None)
    environment_log_categories = {
        item.get('category')
        for item in environment_diagnostics.get('properties', {}).get('logs', [])
    } if environment_diagnostics else set()
    if not {'ContainerAppConsoleLogs', 'ContainerAppSystemLogs'}.issubset(
            environment_log_categories):
        scopes = [resource.get('scope') for resource in diagnostic_settings]
        raise ValueError(
            'Console and system logs must route from the Container Apps environment; '
            f'compiled diagnostic scopes were {scopes!r}')
    if app_diagnostics is None or app_diagnostics.get('properties', {}).get('logs'):
        raise ValueError('Container App-level diagnostics may route metrics, not logs')
    app_metric_categories = {
        item.get('category')
        for item in app_diagnostics.get('properties', {}).get('metrics', [])
    }
    if 'AllMetrics' not in app_metric_categories:
        raise ValueError('Container App-level diagnostics must route AllMetrics')
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
    if 'substring(Log, indexof(Log' not in alert_queries:
        raise ValueError('Health alert queries must parse timestamp-prefixed console JSON')
    if set(template.get('outputs', {})) != {
            'registryName', 'registryServer', 'workloadUrl', 'logWorkspaceName', 'insightsName'}:
        raise ValueError('Hosting outputs must contain only public resource identifiers')


def validate_what_if(result, expected_scope=None):
    """Fail closed except for known Azure-managed or conditionally omitted resources."""
    if not isinstance(result, dict) or result.get('status') != 'Succeeded' or result.get('error'):
        raise ValueError('What-if did not report success')
    if result.get('potentialChanges') or result.get('diagnostics'):
        raise ValueError('What-if reported unverified changes or diagnostics')
    changes = result.get('changes')
    if not isinstance(changes, list) or not changes:
        raise ValueError('Missing what-if changes')
    allowed = {'Create', 'Modify', 'NoChange', 'Ignore'}
    if any(not isinstance(change, dict) or change.get('changeType') not in allowed
           or not change.get('resourceId') for change in changes):
        raise ValueError('Incomplete or unexpected what-if result')
    if expected_scope:
        scope = expected_scope.rstrip('/').lower()
        if (not re.fullmatch(
                r'/subscriptions/[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
                r'/resourcegroups/rg-pb-dev-francecentral-foundation', scope)
                or any(not change['resourceId'].lower().startswith(scope + '/providers/')
                       for change in changes)):
            raise ValueError('What-if resource is outside the reviewed dev France Central scope')
    ignored = [change for change in changes if change['changeType'] == 'Ignore']
    expected_ignored_id_suffix = (
        '/providers/microsoft.insights/actiongroups/application insights smart detection'
    )
    if any(not (change['resourceId'].lower().endswith(expected_ignored_id_suffix)
               or is_conditional_workload_ignore(change['resourceId'])
               or is_france_data_foundation_ignore(change['resourceId']))
           for change in ignored):
        raise ValueError(
            'Unexpected ignored resource; only Azure-managed Smart Detection and known '
            'conditional dev/test or France Central data-foundation resources may be ignored'
        )
    return changes


def is_conditional_workload_ignore(resource_id):
    """Match only exact release-test resources omitted when deployWorkload is false."""
    segments = resource_id.strip('/').lower().split('/')
    if len(segments) != 8 or segments[0] != 'subscriptions' or segments[2] != 'resourcegroups' or segments[4] != 'providers':
        return False
    if not re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', segments[1]):
        return False

    environment = None
    for candidate in ('dev', 'test'):
        if re.fullmatch(rf'rg-pb-{candidate}-[a-z0-9]+-foundation', segments[3]):
            environment = candidate
            break
    if environment is None:
        return False

    resource_type, resource_name = segments[6], segments[7]
    if segments[5] == 'microsoft.app' and resource_type == 'containerapps':
        return resource_name == f'ca-pb-{environment}-release-test'
    if segments[5] == 'microsoft.insights' and resource_type == 'scheduledqueryrules':
        return resource_name in {
            f'alert-pb-{environment}-health-latency',
            f'alert-pb-{environment}-missing-health-telemetry',
            f'alert-pb-{environment}-unhealthy-health-response',
        }
    return False


def is_france_data_foundation_ignore(resource_id):
    """Allow the separate data template's exact resource families in a France hosting preview."""
    parts = resource_id.strip('/').lower().split('/')
    if (len(parts) < 8 or parts[0] != 'subscriptions'
            or parts[2] != 'resourcegroups' or parts[4] != 'providers'
            or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', parts[1])):
        return False
    group = re.fullmatch(r'rg-pb-(dev|test)-francecentral-foundation', parts[3])
    if not group:
        return False
    environment = group[1]
    suffix = r'[a-z0-9]{13}'
    provider = parts[5]
    tail = parts[6:]
    if provider == 'microsoft.cognitiveservices':
        if len(tail) == 2 and tail[0] == 'accounts':
            return bool(re.fullmatch(rf'cs-pb-{environment}-{suffix}-(foundry|speech)', tail[1]))
        return (len(tail) == 4 and tail[0] == 'accounts'
                and bool(re.fullmatch(rf'cs-pb-{environment}-{suffix}-foundry', tail[1]))
                and tail[2] == 'projects' and tail[3] == f'phonebuddy-{environment}')
    if provider == 'microsoft.managedidentity':
        return tail == ['userassignedidentities', f'id-pb-{environment}-data']
    if provider == 'microsoft.servicebus':
        return (len(tail) == 2 and tail[0] == 'namespaces'
                and bool(re.fullmatch(rf'sbpb{environment}{suffix}', tail[1])))
    if provider == 'microsoft.sql':
        server = (len(tail) in (2, 4) and tail[0] == 'servers'
                  and bool(re.fullmatch(rf'sql-pb-{environment}-{suffix}', tail[1])))
        return bool(server and (len(tail) == 2 or tail[2:] in
                                (['databases', 'master'], ['databases', 'phonebuddy'])))
    if provider == 'microsoft.storage':
        return (len(tail) == 2 and tail[0] == 'storageaccounts'
                and bool(re.fullmatch(rf'pb{environment}{suffix}', tail[1])))
    return False


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
    parser.add_argument('--expected-scope', help='exact resource-group scope for a live what-if')
    parser.add_argument('--quality-evidence', type=Path, help='validate GitHub check-run evidence')
    parser.add_argument('--expected-sha', help='expected commit for Quality evidence')
    parser.add_argument('--deployment-ready', choices=['dev', 'test', 'prod'],
                        help='reject unresolved inputs, including runtime SQL admin overrides')
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
        location = environment_parameters(environment)['location']['value']
        if not isinstance(location, str) or not location.strip() or location.upper() == 'UNRESOLVED':
            raise ValueError('Production geography is unresolved; no Foundry fallback is allowed')
        model_name, model_version, sku, capacity = FOUNDRY_MODEL[environment]
        evidence = foundry_preflight(subscription_id, location, model_name,
                                     model_version, sku, capacity)
        print(json.dumps(evidence))
        return
    if options.what_if_result:
        changes = validate_what_if(json.loads(options.what_if_result.read_text()),
                                   options.expected_scope)
        counts = {kind: sum(item['changeType'] == kind for item in changes)
                  for kind in ('Create', 'Modify', 'NoChange', 'Ignore')}
        print(json.dumps({'whatIfChangeCounts': counts}))
        return
    binary = os.environ.get('BICEP', 'bicep')
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
            deployment_ready(env, values, runtime_sql_admin_overrides())
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
