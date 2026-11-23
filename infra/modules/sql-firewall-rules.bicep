targetScope = 'resourceGroup'

@description('Name of the existing Azure SQL server (not the hostname).')
@minLength(1)
param sqlServerName string

@description('Outbound IPv4 addresses of the API Container App, as reported by the app itself. Received as a module parameter so the loop is evaluated after the app exists.')
param outboundIpAddresses array

// Rule names must never start with pb-release-: that prefix belongs to the release runner's
// temporary rules, which scripts/database_release.py sweeps by prefix.
var rulePrefix = 'pb-api-egress-'

resource server 'Microsoft.Sql/servers@2023-08-01' existing = {
  name: sqlServerName
}

// One single-address rule per outbound IP, named by position so a changed IP updates its rule in
// place and a redeploy is idempotent. Never the 0.0.0.0 "allow Azure services" range.
resource apiEgress 'Microsoft.Sql/servers/firewallRules@2023-08-01' = [for (ip, index) in outboundIpAddresses: {
  parent: server
  name: '${rulePrefix}${index}'
  properties: {
    startIpAddress: ip
    endIpAddress: ip
  }
}]

output ruleNames array = [for (ip, index) in outboundIpAddresses: '${rulePrefix}${index}']
