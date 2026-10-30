targetScope = 'subscription'

@allowed([
  'dev'
  'test'
  'prod'
])
param environment string

@minLength(1)
@maxLength(40)
param location string

@minLength(1)
@maxLength(64)
param owner string

@minLength(1)
@maxLength(64)
param costCenter string

// One deployment owns only its environment's foundation resource group.
module foundation './modules/foundation.bicep' = {
  name: 'phonebuddy-${environment}-foundation'
  params: {
    environment: environment
    location: location
    owner: owner
    costCenter: costCenter
  }
}

output resourceGroupName string = foundation.outputs.resourceGroupName
