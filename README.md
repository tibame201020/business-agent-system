# Business Agent System v0.1

Goal: operate a repeatable digital-business discovery and execution portfolio on behalf of the owner. This repo is the AGENT runtime, not a storefront or a worksheet.

Actual v0.1: model-driven decision per tick, scoped tool invocation, independent public-demand evidence collection, two-source offer gate, durable append-only operation receipts and restart-safe state, build-experiment dispatch to an owner repository issue, monitoring of owner-owned assets. A rejected or unavailable model must fail closed, never fall back to invented AI decisions.

Architecture: Controller -> Model Planner -> Tool contract -> Research/Inspection/Evaluation/Build Dispatch/Asset Audit -> Durable state -> Next tick. Provider interchangeable by env. GitHub Actions runner supplies a short-lived owner token scoped to models read, issues write and contents write. Only public business state is committed to the public repo. No buyer data or account secrets.

This is an actual controller and first bounded operation slice, not yet a finished income-producing company. Remaining commerce acceptance: an agent-built verified MVP, real distribution/acquisition, owner-authorized checkout and delivery, cost ledger and verified net revenue. Queueing a build Issue is explicitly NOT product completion.

Commands:
- python -m unittest discover -s tests -v
- python -m agent.cli status
- python -m agent.cli tick --max-steps 3

Live inference uses BUSINESS_MODEL_URL, BUSINESS_MODEL_NAME and BUSINESS_MODEL_TOKEN or Actions GITHUB_TOKEN. GitHub Models API availability is an empirical CI verification condition, not an assumed entitlement.
