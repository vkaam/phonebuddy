targetScope = 'resourceGroup'

@allowed([
  'dev'
  'test'
  'prod'
])
param environment string
param location string = resourceGroup().location
param owner string
param costCenter string

@description('Microsoft Entra object ID for the SQL administrator. Replace UNRESOLVED before deployment.')
param sqlAdminObjectId string = 'UNRESOLVED'

@description('Microsoft Entra administrator name for SQL. Replace UNRESOLVED before deployment.')
param sqlAdminLogin string = 'UNRESOLVED'

@description('Foundry model identity checked by scripts/check_bicep.py --foundry-preflight.')
param foundryModelName string = 'gpt-5-mini'

@description('Pinned Foundry model version checked against subscription capacity and lifecycle before deployment.')
param foundryModelVersion string = '2025-08-07'

@minValue(1)
@description('GlobalStandard deployment capacity units. Must be checked against subscription quota before deployment.')
param foundryModelCapacity int = 10

var suffix = uniqueString(subscription().id, resourceGroup().id)
var tags = {
  environment: environment
  service: 'phonebuddy'
  owner: owner
  costCenter: costCenter
}
var retentionDays = environment == 'prod' ? 35 : environment == 'test' ? 14 : 7
var sqlCapacity = environment == 'prod' ? 2 : 1
var sqlMaxSizeBytes = environment == 'prod' ? 107374182400 : 26843545600
var sqlBackupRedundancy = environment == 'prod' ? 'Zone' : 'Local'
var sqlAutoPauseDelay = environment == 'prod' ? -1 : 60
var storageSkuName = environment == 'prod' ? 'Standard_ZRS' : 'Standard_LRS'
var serviceBusSku = environment == 'prod'
  ? { name: 'Premium', tier: 'Premium', capacity: 1 }
  : { name: 'Standard', tier: 'Standard' }
var queueTimeToLive = environment == 'prod' ? 'P30D' : environment == 'test' ? 'P7D' : 'P1D'
var foundryModelDeploymentName = 'chat'

resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-pb-${environment}-data'
  location: location
  tags: tags
}

resource sqlServer 'Microsoft.Sql/servers@2023-08-01' = {
  name: 'sql-pb-${environment}-${suffix}'
  location: location
  tags: tags
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: 'User'
      login: sqlAdminLogin
      sid: sqlAdminObjectId
      tenantId: tenant().tenantId
      azureADOnlyAuthentication: true
    }
  }
}

resource callDatabase 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: sqlServer
  name: 'phonebuddy'
  location: location
  tags: tags
  sku: {
    name: 'GP_S_Gen5_${sqlCapacity}'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: sqlCapacity
  }
  properties: {
    minCapacity: json('0.5')
    autoPauseDelay: sqlAutoPauseDelay
    maxSizeBytes: sqlMaxSizeBytes
    requestedBackupStorageRedundancy: sqlBackupRedundancy
  }
}

resource sqlBackupRetention 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies@2023-08-01' = {
  parent: callDatabase
  name: 'default'
  properties: {
    retentionDays: retentionDays
  }
}

resource blobStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'pb${environment}${suffix}'
  location: location
  tags: tags
  sku: {
    name: storageSkuName
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Enabled'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: blobStorage
  name: 'default'
  properties: {
    isVersioningEnabled: true
    deleteRetentionPolicy: {
      enabled: true
      days: retentionDays
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: retentionDays
    }
  }
}

resource callsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'calls'
  properties: {
    publicAccess: 'None'
  }
}

resource blobDataRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(blobStorage.id, workloadIdentity.id, 'storage-blob-data-contributor')
  scope: blobStorage
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

resource serviceBus 'Microsoft.ServiceBus/namespaces@2024-01-01' = {
  name: 'sbpb${environment}${suffix}'
  location: location
  tags: tags
  sku: serviceBusSku
  properties: {
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    minimumTlsVersion: '1.2'
  }
}

resource callEventsQueue 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: serviceBus
  name: 'call-events'
  properties: {
    deadLetteringOnMessageExpiration: true
    defaultMessageTimeToLive: queueTimeToLive
    maxDeliveryCount: 5
    lockDuration: 'PT1M'
    enablePartitioning: true
    requiresDuplicateDetection: true
    duplicateDetectionHistoryTimeWindow: 'PT10M'
  }
}

resource foundationSmokeQueue 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: serviceBus
  name: 'foundation-smoke'
  properties: {
    deadLetteringOnMessageExpiration: true
    defaultMessageTimeToLive: 'P1D'
    maxDeliveryCount: 3
    lockDuration: 'PT1M'
    enablePartitioning: true
  }
}

resource serviceBusSenderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBus.id, workloadIdentity.id, 'service-bus-data-sender')
  scope: serviceBus
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39')
  }
}

resource serviceBusReceiverRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBus.id, workloadIdentity.id, 'service-bus-data-receiver')
  scope: serviceBus
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0')
  }
}

resource speech 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'cs-pb-${environment}-${suffix}-speech'
  location: location
  tags: tags
  kind: 'SpeechServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: 'cs-pb-${environment}-${suffix}-speech'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource speechUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(speech.id, workloadIdentity.id, 'cognitive-services-speech-user')
  scope: speech
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f2dc8367-1007-4938-bd23-fe263f013447')
  }
}

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'cs-pb-${environment}-${suffix}-foundry'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'cs-pb-${environment}-${suffix}-foundry'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: false
  }
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: 'phonebuddy-${environment}'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'Phonebuddy ${environment}'
    description: 'Environment-scoped Phonebuddy inference project.'
  }
}

resource foundryModel 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: foundryModelDeploymentName
  dependsOn: [
    foundryProject
  ]
  sku: {
    name: 'GlobalStandard'
    capacity: foundryModelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: foundryModelName
      version: foundryModelVersion
    }
    versionUpgradeOption: 'NoAutoUpgrade'
  }
}

resource foundryInferenceRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundry.id, workloadIdentity.id, 'cognitive-services-openai-user')
  scope: foundry
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  }
}

output workloadIdentityClientId string = workloadIdentity.properties.clientId
output workloadIdentityPrincipalId string = workloadIdentity.properties.principalId
output sqlServerName string = sqlServer.name
output sqlDatabaseName string = callDatabase.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output storageAccountName string = blobStorage.name
output storageContainerName string = callsContainer.name
output serviceBusNamespaceName string = serviceBus.name
output serviceBusQueueName string = callEventsQueue.name
output serviceBusSmokeQueueName string = foundationSmokeQueue.name
output speechEndpoint string = 'https://${speech.name}.cognitiveservices.azure.com'
output foundryEndpoint string = 'https://${foundry.name}.services.ai.azure.com'
output foundryProjectName string = foundryProject.name
output foundryDeploymentName string = foundryModel.name
