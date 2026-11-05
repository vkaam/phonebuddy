targetScope = 'subscription'

@allowed([
  'dev'
  'test'
  'prod'
])
param environment string

@minLength(1)
@maxLength(37)
param location string

@minLength(1)
@maxLength(64)
param owner string

@minLength(1)
@maxLength(64)
param costCenter string

@description('Microsoft Entra object ID that administers Azure SQL. Deployment remains blocked while this is UNRESOLVED.')
param sqlAdminObjectId string = 'UNRESOLVED'

@description('Microsoft Entra administrator name for Azure SQL. Deployment remains blocked while this is UNRESOLVED.')
param sqlAdminLogin string = 'UNRESOLVED'

@description('Foundry model name pinned in the environment deployment.')
param foundryModelName string = 'gpt-5-mini'

@description('Foundry model version pinned in the environment deployment.')
param foundryModelVersion string = '2025-08-07'

// One deployment owns only its environment's foundation resource group.
module foundation './modules/foundation.bicep' = {
  name: 'phonebuddy-${environment}-${location}-foundation'
  params: {
    environment: environment
    location: location
    owner: owner
    costCenter: costCenter
  }
}

module dataPlatform './modules/data-platform.bicep' = {
  name: 'pb-${environment}-${location}-data'
  scope: resourceGroup('rg-pb-${environment}-${location}-foundation')
  dependsOn: [
    foundation
  ]
  params: {
    environment: environment
    location: location
    owner: owner
    costCenter: costCenter
    sqlAdminObjectId: sqlAdminObjectId
    sqlAdminLogin: sqlAdminLogin
    foundryModelName: foundryModelName
    foundryModelVersion: foundryModelVersion
    foundryModelCapacity: environment == 'prod' ? 50 : environment == 'test' ? 20 : 10
  }
}

output resourceGroupName string = foundation.outputs.resourceGroupName
