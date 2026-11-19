# PhoneBuddy

A planned Azure-hosted browser VoIP client with SIP connectivity, Dutch/English call transcription, and evidence-linked summaries.

The first release is an internal pilot. The architecture prepares for multiple organizations through explicit organization boundaries in identity, authorization, telephony configuration, storage, and background processing.

See the [software and delivery plan](docs/software-plan.md) for the proposed architecture, Bicep infrastructure, agentic software factory, validation gates, and delivery roadmap.

The [quality and delivery baseline](docs/quality-and-delivery.md) describes CI,
local checks, PR safety assessment, GitHub activation, and future release gates.

The [autonomous development assessment and plan](docs/autonomous-development-plan.md)
records current factory gaps, live GitHub policy findings, and the staged Backlog
roadmap from unattended PR production to bounded automatic delivery.

The [factory workflow](docs/issue-backlog-governance.md) describes how work
moves from an approved GitHub issue to a Backlog.md task, a pull request and a
merge, and which checks guard each step.

Status: delivery foundation in progress. No application or cloud infrastructure has been deployed.
