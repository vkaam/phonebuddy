targetScope = 'resourceGroup'

@allowed(['dev', 'test', 'prod'])
param environment string
param location string = resourceGroup().location
param owner string
param costCenter string
@description('Deploy the workload only after its image has been pushed to this registry.')
param deployWorkload bool = false
@description('Create the Container App pull-role assignment during a privileged bootstrap deployment.')
param managePullRoleAssignment bool = true
@description('Provision the optional Static Web App only where that resource type is available.')
param deployStaticSite bool = true
@description('Static Web App region; defaults to the resource group location unless explicitly selected.')
param staticSiteLocation string = location
@description('SHA-256 image digest without the sha256: prefix; provide 64 zeroes during bootstrap.')
@minLength(64)
@maxLength(64)
param imageDigest string
@description('Nonempty version returned by the readiness endpoint.')
@minLength(1)
param releaseVersion string
@description('Unique lowercase alphanumeric and hyphen suffix for this trusted deployment attempt.')
@minLength(1)
@maxLength(63)
param revisionSuffix string

var suffix = uniqueString(subscription().id, resourceGroup().id)
var tags = { environment: environment, service: 'phonebuddy', owner: owner, costCenter: costCenter }

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'pb${environment}${suffix}'
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'pb-${environment}-${substring(suffix, 0, 10)}'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
    publicNetworkAccess: 'Disabled'
    accessPolicies: []
  }
}

resource site 'Microsoft.Web/staticSites@2023-12-01' = if (deployStaticSite) {
  name: 'stapp-pb-${environment}-${suffix}'
  location: staticSiteLocation
  tags: tags
  sku: { name: 'Free', tier: 'Free' }
  properties: { allowConfigFileUpdates: false }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-pb-${environment}-pull'
  location: location
  tags: tags
}

resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (managePullRoleAssignment) {
  name: guid(registry.id, identity.id, 'acrpull')
  scope: registry
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-pb-${environment}'
  location: location
  tags: tags
  properties: { appLogsConfiguration: { destination: 'azure-monitor' } }
}

resource logWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-pb-${environment}-${substring(suffix, 0, 10)}'
  location: location
  tags: tags
  properties: {
    retentionInDays: 30
    features: { enableLogAccessUsingOnlyResourcePermissions: true }
    sku: { name: 'PerGB2018' }
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-pb-${environment}-${substring(suffix, 0, 10)}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    IngestionMode: 'LogAnalytics'
    WorkspaceResourceId: logWorkspace.id
  }
}

resource environmentDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'phonebuddy-environment-system-logs'
  scope: managedEnvironment
  properties: {
    workspaceId: logWorkspace.id
    logAnalyticsDestinationType: 'Dedicated'
    logs: [
      { category: 'ContainerAppSystemLogs', enabled: true }
      { category: 'ContainerAppConsoleLogs', enabled: true }
    ]
    metrics: [{ category: 'AllMetrics', enabled: true }]
  }
}

resource app 'Microsoft.App/containerApps@2023-05-01' = if (deployWorkload) {
  name: 'ca-pb-${environment}-release-test'
  location: location
  tags: union(tags, { releaseVersion: releaseVersion })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: { external: true, targetPort: 8080, transport: 'auto', allowInsecure: false }
      registries: [{ server: registry.properties.loginServer, identity: identity.id }]
    }
    template: {
      revisionSuffix: revisionSuffix
      containers: [{
        name: 'release-test'
        image: '${registry.properties.loginServer}/release-test@sha256:${imageDigest}'
        env: [{ name: 'RELEASE_VERSION', value: releaseVersion }]
        resources: { cpu: json('0.25'), memory: '0.5Gi' }
        probes: [{ type: 'Readiness', httpGet: { path: '/ready', port: 8080 }, initialDelaySeconds: 2, periodSeconds: 10 }]
      }]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
  dependsOn: managePullRoleAssignment ? [pull] : []
}

resource appDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (deployWorkload) {
  name: 'phonebuddy-health-telemetry'
  scope: app
  properties: {
    workspaceId: logWorkspace.id
    logAnalyticsDestinationType: 'Dedicated'
    metrics: [{ category: 'AllMetrics', enabled: true }]
  }
}

var telemetryRows = 'ContainerAppConsoleLogs | where ContainerAppName == \'${app.name}\' | where Log contains \'"event":"health_request"\' | extend health=parse_json(substring(Log, indexof(Log, \'{\'))) | where todouble(health.duration_ms) >= 0'
var missingTelemetryQuery = 'print telemetryCount=toscalar(${telemetryRows} | where TimeGenerated > ago(5m) | count)'
var unhealthyResponseQuery = 'print failureCount=toscalar(${telemetryRows} | where TimeGenerated > ago(5m) | where toint(health.status) != 200 | count)'
var latencyQuery = 'print p95LatencyMs=toscalar(${telemetryRows} | where TimeGenerated > ago(5m) | summarize percentile(todouble(health.duration_ms), 95))'

resource missingTelemetryAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (deployWorkload) {
  name: 'alert-pb-${environment}-missing-health-telemetry'
  kind: 'LogAlert'
  location: location
  tags: tags
  properties: {
    displayName: 'Phonebuddy ${environment}: missing health telemetry'
    description: 'Fails closed when no synthetic health telemetry is observed in a five-minute window.'
    severity: 2
    enabled: true
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    scopes: [logWorkspace.id]
    criteria: {
      allOf: [{
        query: missingTelemetryQuery
        timeAggregation: 'Maximum'
        metricMeasureColumn: 'telemetryCount'
        operator: 'LessThan'
        threshold: 1
        failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
      }]
    }
    autoMitigate: true
  }
}

resource unhealthyResponseAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (deployWorkload) {
  name: 'alert-pb-${environment}-unhealthy-health-response'
  kind: 'LogAlert'
  location: location
  tags: tags
  properties: {
    displayName: 'Phonebuddy ${environment}: unhealthy health response'
    description: 'Fires when a synthetic health request returns a non-success status.'
    severity: 1
    enabled: true
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    scopes: [logWorkspace.id]
    criteria: {
      allOf: [{
        query: unhealthyResponseQuery
        timeAggregation: 'Maximum'
        metricMeasureColumn: 'failureCount'
        operator: 'GreaterThan'
        threshold: 0
        failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
      }]
    }
    autoMitigate: true
  }
}

resource latencyAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (deployWorkload) {
  name: 'alert-pb-${environment}-health-latency'
  kind: 'LogAlert'
  location: location
  tags: tags
  properties: {
    displayName: 'Phonebuddy ${environment}: health response latency'
    description: 'Fires when the p95 health response latency reaches two seconds in a five-minute window.'
    severity: 2
    enabled: true
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    scopes: [logWorkspace.id]
    criteria: {
      allOf: [{
        query: latencyQuery
        timeAggregation: 'Maximum'
        metricMeasureColumn: 'p95LatencyMs'
        operator: 'GreaterThanOrEqual'
        threshold: 2000
        failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
      }]
    }
    autoMitigate: true
  }
}

output registryName string = registry.name
output registryServer string = registry.properties.loginServer
output workloadUrl string = deployWorkload ? 'https://${app.properties.configuration.ingress.fqdn}' : ''
output logWorkspaceName string = logWorkspace.name
output insightsName string = insights.name
