@description('Globally unique name for the dedicated factory coordination storage account.')
@minLength(3)
@maxLength(24)
param storageAccountName string

@description('Object ID of the trusted coordination service identity (not worker identities).')
param coordinatorPrincipalId string

param location string = resourceGroup().location

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    isVersioningEnabled: true
    deleteRetentionPolicy: { enabled: true, days: 30 }
    containerDeleteRetentionPolicy: { enabled: true, days: 30 }
  }
}

resource leases 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'task-leases'
  properties: { publicAccess: 'None' }
}

resource coordinatorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(leases.id, coordinatorPrincipalId, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: leases
  properties: {
    principalId: coordinatorPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

output blobEndpoint string = storage.properties.primaryEndpoints.blob
output containerName string = leases.name
