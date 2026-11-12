targetScope = 'resourceGroup'

@allowed(['dev', 'test', 'prod'])
param environment string
param location string = resourceGroup().location
param owner string
param costCenter string

@description('Media capacity creates billable Azure resources and is disabled until explicitly enabled.')
param deployMedia bool = false

@description('Azure Compute Gallery containing the reviewed gateway image.')
param imageGalleryName string
@description('Resource group containing the Azure Compute Gallery.')
param imageGalleryResourceGroup string
@description('Azure Compute Gallery image definition name for the gateway.')
param gatewayImageName string
@description('Exact Azure Compute Gallery image version, never an alias such as latest.')
@minLength(1)
param gatewayImageVersion string

@description('Immutable release identifier recorded on the VM, such as a source commit SHA.')
@minLength(7)
param releaseVersion string

@description('DNS name covered by the TLS certificate installed in the reviewed gateway image.')
@minLength(3)
param gatewayFqdn string

@description('Non-overlapping private address space for this environment media VNet.')
param vnetAddressPrefix string

@description('SSH public key used only through Azure Bastion; password login is disabled.')
@minLength(80)
param adminSshPublicKey string

@description('Linux VM size. Confirm media capacity and regional quota before deployment.')
param gatewayVmSize string = 'Standard_B2ms'

var tags = {
  environment: environment
  service: 'phonebuddy-media'
  owner: owner
  costCenter: costCenter
  releaseVersion: releaseVersion
}
var vnetName = 'vnet-pb-${environment}-media'
var gatewaySubnetPrefix = cidrSubnet(vnetAddressPrefix, 2, 0)
var bastionSubnetPrefix = cidrSubnet(vnetAddressPrefix, 2, 1)
var privateGatewayAddress = cidrHost(gatewaySubnetPrefix, 4)
var gatewayName = 'vm-pb-${environment}-media'
var gatewayPublicIpName = 'pip-pb-${environment}-media'
var bastionPublicIpName = 'pip-pb-${environment}-bastion'
var nsgName = 'nsg-pb-${environment}-media'

resource mediaNetwork 'Microsoft.Network/virtualNetworks@2024-05-01' = if (deployMedia) {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: [vnetAddressPrefix] }
    subnets: [
      {
        name: 'gateway'
        properties: {
          addressPrefix: gatewaySubnetPrefix
          networkSecurityGroup: { id: mediaNsg.id }
        }
      }
      {
        name: 'AzureBastionSubnet'
        properties: { addressPrefix: bastionSubnetPrefix }
      }
    ]
  }
}

resource mediaNsg 'Microsoft.Network/networkSecurityGroups@2024-05-01' = if (deployMedia) {
  name: nsgName
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowWebRtcSignalingTls'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowTurnUdp'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '3478'
        }
      }
      {
        name: 'AllowTurnTcp'
        properties: {
          priority: 120
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '3478'
        }
      }
      {
        name: 'AllowTurnTlsTcp'
        properties: {
          priority: 130
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '5349'
        }
      }
      {
        name: 'AllowTurnTlsUdp'
        properties: {
          priority: 140
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '5349'
        }
      }
      {
        name: 'AllowBoundedRtpUdp'
        properties: {
          priority: 150
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          destinationPortRange: '10000-20000'
        }
      }
      {
        name: 'AllowSshFromBastionSubnet'
        properties: {
          priority: 160
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: bastionSubnetPrefix
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
      {
        name: 'AllowDnsUdp'
        properties: {
          priority: 200
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '53'
        }
      }
      {
        name: 'AllowAzurePlatformDns'
        properties: {
          priority: 205
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'AzurePlatformDNS'
          destinationPortRange: '53'
        }
      }
      {
        name: 'AllowNtpUdp'
        properties: {
          priority: 210
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '123'
        }
      }
      {
        name: 'AllowAzurePlatformTime'
        properties: {
          priority: 215
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'AzurePlatformTime'
          destinationPortRange: '123'
        }
      }
      {
        name: 'AllowHttpsEgress'
        properties: {
          priority: 220
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowSipTlsEgress'
        properties: {
          priority: 230
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '5061'
        }
      }
      {
        name: 'AllowRtpUdpEgress'
        properties: {
          priority: 240
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Udp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '10000-20000'
        }
      }
      {
        name: 'DenyOtherInternetEgress'
        properties: {
          priority: 4096
          direction: 'Outbound'
          access: 'Deny'
          protocol: '*'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource gatewayPublicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = if (deployMedia) {
  name: gatewayPublicIpName
  location: location
  sku: { name: 'Standard', tier: 'Regional' }
  tags: tags
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
    idleTimeoutInMinutes: 10
    dnsSettings: { domainNameLabel: 'pb-${environment}-${uniqueString(resourceGroup().id)}' }
  }
}

resource bastionPublicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = if (deployMedia) {
  name: bastionPublicIpName
  location: location
  sku: { name: 'Standard', tier: 'Regional' }
  tags: tags
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
    idleTimeoutInMinutes: 10
  }
}

resource bastion 'Microsoft.Network/bastionHosts@2024-05-01' = if (deployMedia) {
  name: 'bas-pb-${environment}-media'
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: {
    disableCopyPaste: true
    enableFileCopy: false
    enableIpConnect: false
    enableShareableLink: false
    enableTunneling: false
    ipConfigurations: [
      {
        name: 'configuration'
        properties: {
          publicIPAddress: { id: bastionPublicIp.id }
          subnet: { id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, 'AzureBastionSubnet') }
        }
      }
    ]
    scaleUnits: 2
  }
}

resource gatewayNic 'Microsoft.Network/networkInterfaces@2024-05-01' = if (deployMedia) {
  name: '${gatewayName}-nic'
  location: location
  tags: tags
  properties: {
    ipConfigurations: [
      {
        name: 'gateway'
        properties: {
          privateIPAllocationMethod: 'Static'
          privateIPAddress: privateGatewayAddress
          subnet: { id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, 'gateway') }
          publicIPAddress: { id: gatewayPublicIp.id }
        }
      }
    ]
    networkSecurityGroup: { id: mediaNsg.id }
  }
  dependsOn: [mediaNetwork]
}

resource gateway 'Microsoft.Compute/virtualMachines@2024-03-01' = if (deployMedia) {
  name: gatewayName
  location: location
  tags: union(tags, { gatewayFqdn: gatewayFqdn })
  properties: {
    hardwareProfile: { vmSize: gatewayVmSize }
    securityProfile: {
      securityType: 'TrustedLaunch'
      uefiSettings: { secureBootEnabled: true, vTpmEnabled: true }
    }
    osProfile: {
      computerName: gatewayName
      adminUsername: 'pbadmin'
      linuxConfiguration: {
        disablePasswordAuthentication: true
        provisionVMAgent: true
        ssh: {
          publicKeys: [
            {
              path: '/home/pbadmin/.ssh/authorized_keys'
              keyData: adminSshPublicKey
            }
          ]
        }
      }
    }
    storageProfile: {
      imageReference: {
        id: resourceId(imageGalleryResourceGroup, 'Microsoft.Compute/galleries/images/versions', imageGalleryName, gatewayImageName, gatewayImageVersion)
      }
      osDisk: {
        name: '${gatewayName}-os'
        createOption: 'FromImage'
        deleteOption: 'Delete'
        managedDisk: { storageAccountType: 'StandardSSD_LRS' }
      }
    }
    networkProfile: {
      networkInterfaces: [{ id: gatewayNic.id, properties: { primary: true } }]
    }
    diagnosticsProfile: {
      bootDiagnostics: { enabled: true }
    }
  }
  dependsOn: [bastion]
}

output mediaDeploymentEnabled bool = deployMedia
output gatewayPublicIpAddress string = deployMedia ? gatewayPublicIp.properties.ipAddress : ''
output gatewayDnsLabel string = deployMedia ? gatewayPublicIp.properties.dnsSettings.fqdn : ''
output gatewayPrivateAddress string = deployMedia ? privateGatewayAddress : ''
output gatewayReleaseVersion string = deployMedia ? releaseVersion : ''
