# Gateway and TURN runtime contract

`../media.bicep` provisions the pilot media network and a single Linux VM. It
defaults to `deployMedia=false`; a group deployment creates no media resources
unless an operator explicitly opts in. It is separate from the foundation and
hosting deployments and has not been deployed by this change.

## Network and access boundary

The template allocates one environment VNet with separate gateway and
`AzureBastionSubnet` subnets. Supply a non-overlapping IPv4 VNet prefix. The VM
has a static public IPv4 address for media and a static private address for
internal control. Public inbound is limited to:

| Protocol and port | Purpose |
| --- | --- |
| TCP 443 | Asterisk secure WebSocket signaling and TLS |
| UDP/TCP 3478 | TURN allocations |
| UDP/TCP 5349 | TURN over TLS |
| UDP 10000–20000 | Bounded RTP/WebRTC media |

SSH is permitted only from the VNet's Bastion subnet. The VM has no public SSH
rule; ARI and other control endpoints must remain private in the selected
gallery image. Bastion is a billable service and the VM is always on. Review
current prices, quota and the deployment preview before enabling media capacity.

The generated Azure DNS label is only a stable public endpoint for discovery.
Create the approved custom DNS A record for `gatewayFqdn` and issue a certificate
whose SAN includes that name. The certificate and private key are runtime
inputs and must be mounted at `/run/phonebuddy/certificates/`; they are never
template parameters or repository files.

## Versioned image and runtime configuration

Provide `galleryImageVersionId` as the resource ID of a specific Azure Compute
Gallery image version, never an image alias or `latest`, and set `releaseVersion`
to the corresponding reviewed source revision. The image must contain the
supported Asterisk and coturn releases, required modules, the versioned
configuration in this directory, and the runtime renderer. Record image build
provenance and verify the produced image before deploying it. No provider
credentials or long-lived credentials belong in the image.

The Asterisk templates expose one test-only WebRTC endpoint and an Echo
extension (`700`); no Fonzer account is needed. The coturn template uses
time-limited shared-secret authentication, quota limits, the fixed media range,
TLS 1.2 or newer, and peer-address restrictions. The test password and TURN
shared secret are required at runtime through protected environment values.
Render configurations with:

```sh
python3 -B infra/gateway/render_config.py --output-dir /run/phonebuddy/runtime
```

Run that command as the gateway service account with `GATEWAY_PRIVATE_IP`,
`GATEWAY_PUBLIC_IP`, `GATEWAY_FQDN`, `WEBRTC_TEST_PASSWORD`, and
`TURN_SHARED_SECRET` supplied by the approved secret/configuration service.
The renderer writes owner-only files and does not print the values. Never place
these values in Bicep parameters, command-line arguments, CI artifacts or source
control. Production provider credentials are not part of this controlled test.

Before accepting a release, validate the rendered Asterisk configuration with
`asterisk -C <rendered-config-dir> -rx 'core show settings'`, check that the WSS
listener is on 443 and ARI is loopback/private, and validate the TURN config
with `turnserver --check-config --config <rendered-turnserver.conf>` using the
selected image's supported command. Exact command support depends on the pinned
upstream releases.

## Controlled call and forced TURN

The live acceptance path is a browser using the temporary `phonebuddy-test`
credential to register over WSS and call extension 700. Use an isolated browser
with a synthetic media device; configure its ICE policy to `relay` and point it
only at this deployment's TURN/TLS endpoint. Capture browser and gateway stats
showing both sent and received audio bytes, a successful TURN candidate pair,
the certificate hostname, and the gateway's private management boundary.
Repeat from a restricted network and retain source SHA, image version, run log,
and redacted test result. A passing unit test or successful Bicep deployment is
not a substitute for this call. This live call has not yet been run.

## Update, drain and rollback

Do not replace the VM image while calls are active. The gateway operator must
first remove the instance from new-call routing, verify that new registrations
and dialogs are not being admitted, wait for active channels to end, and retain
the call count and release identity as evidence. If active calls do not drain
within the reviewed maintenance window, stop the update and escalate; do not
force termination to meet a schedule. The pilot has one VM, so maintenance
interrupts new calls and does not provide transparent failover for active calls.

Deploy a new immutable image version only after the configuration and controlled
call checks pass. Keep the previous image version and deployment parameters.
On failed readiness or call checks, stop admission, restore the previous image
version through a reviewed redeployment, and repeat the full health and call
checks. Do not delete disks or shared resources as a rollback shortcut. These
steps describe the required operator procedure; automated drain orchestration
and an Azure execution have not been verified by this change.

## Validation

The repository Bicep check compiles `infra/media.bicep` and checks the opt-in
default, image version input, static IPs, reviewed ingress set, Bastion-only SSH,
Trusted Launch and secret-free outputs. Python tests validate the renderer's
input and file permissions. Azure what-if, image build provenance, certificate
readback, live forced-TURN call, and drain/rollback exercise remain external
acceptance gates.
