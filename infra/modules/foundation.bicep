targetScope = 'subscription'

@allowed([
  'dev'
  'test'
  'prod'
])
param environment string
param location string
param owner string
param costCenter string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-pb-${environment}-${location}-foundation'
  location: location
  tags: {
    environment: environment
    service: 'phonebuddy'
    owner: owner
    costCenter: costCenter
  }
}

output resourceGroupName string = resourceGroup.name
