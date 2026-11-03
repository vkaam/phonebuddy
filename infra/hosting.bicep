targetScope = 'resourceGroup'

@allowed(['dev', 'test', 'prod'])
param environment string
param location string = resourceGroup().location
param owner string
param costCenter string
@description('Deploy the workload only after its image has been pushed to this registry.')
param deployWorkload bool = false
@description('SHA-256 image digest without the sha256: prefix; provide 64 zeroes during bootstrap.')
@minLength(64)
@maxLength(64)
param imageDigest string
@description('Nonempty version returned by the readiness endpoint.')
@minLength(1)
param releaseVersion string

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

resource site 'Microsoft.Web/staticSites@2023-12-01' = {
  name: 'stapp-pb-${environment}-${suffix}'
  location: location
  tags: tags
  sku: { name: 'Free', tier: 'Free' }
  properties: { allowConfigFileUpdates: false }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-pb-${environment}-pull'
  location: location
  tags: tags
}

resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
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

resource app 'Microsoft.App/containerApps@2023-05-01' = if (deployWorkload) {
  name: 'ca-pb-${environment}-release-test'
  location: location
  tags: tags
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
  dependsOn: [pull]
}

output registryName string = registry.name
output registryServer string = registry.properties.loginServer
output workloadUrl string = deployWorkload ? 'https://${app.properties.configuration.ingress.fqdn}' : ''
