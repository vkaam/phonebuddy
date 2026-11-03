using '../main.bicep'

param environment = 'prod'
param location = 'UNRESOLVED' // Set only after geography and quota approval.
param owner = 'UNRESOLVED'
param costCenter = 'UNRESOLVED'
param sqlAdminObjectId = 'UNRESOLVED'
param sqlAdminLogin = 'UNRESOLVED'
param foundryModelName = 'gpt-5-mini'
param foundryModelVersion = '2025-08-07'
