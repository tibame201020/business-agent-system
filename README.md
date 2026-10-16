# Business Agent System v0.2 — owner-operated autonomous business controller

This repository is the **Agent System**, not ProfitGuard TW or another one-off product page.

**Execution:** Model/Host decision (ChatGPT via Queqiao, or separately configured API provider) -> authorized stage-specific tool -> evidence/receipt -> persisted portfolio state -> next decision. Model output never bypasses source checks, registered builders, test gates or owner-only publication.

## Implemented
- Durable JSON state and append-only receipts, idempotent tool decisions, safe repeated reads, restart recovery.
- Real public GitHub demand discovery and independent issue inspection; two inspected primary-source issues from different repositories required before an offer can advance.
- Offer decision, price *hypothesis*, deterministic evidence gate, owner-owned GitHub build issue.
- Builder registry: first fully tested plugin `ci_flake_audit`, which generates a downloadable Python CLI from a pinned reviewed implementation and reruns its tests without model-generated code execution. Add more builders as independent capabilities.
- Product publication to a GitHub prerelease with ZIP attachment, idempotent asset reconciliation, and downloads-only measurement. Downloads are NOT sales.
- Registered public owned asset HTTP monitoring, independent controller tests, GitHub Actions regression.
- A host-driven planner mode (`--decision-file runtime/private/decision.json`) lets **ChatGPT itself** make decisions and Queqiao execute. No local LLM needed. Optional standalone API mode is disabled unless a verified BUSINESS_MODEL_URL is set.

## Live first experiment
Demand: NVIDIA/cuvs #2783 and sgl-project/sglang #42752 describe real recurring CI flake triage. Offer `offer-2f73b78f0cd8229cab6d` passed a source gate with willingness-to-pay marked UNVERIFIED. Owner issue #1 was created for a bounded experiment. The registered builder produced `runtime/public/products/offer-2f73b78f0cd8229cab6d`, passed its tests, recorded hashes, published an owner-owned GitHub prerelease and verified the downloaded ZIP. The latest cycle is MEASURED; payment remains UNVERIFIED.

## Commands
- `python -m unittest discover -s tests -v`
- From `templates/ci_flake_audit`: `python -m unittest discover -s tests -v`
- `python -m agent.cli status`
- Host-driven: write one JSON `{ "tool": "...", "args": {}, "reason": "..." }` in the ignored private path, then `python -m agent.cli tick --decision-file runtime/private/decision.json`.
- API-driven only after configuring `BUSINESS_MODEL_URL` and token: `python -m agent.cli tick --max-steps 1`.

See AGENTS.md for no-intervention owner operations. GitHub Actions performs push regression; optional hosted inference runs only if its endpoint is explicitly configured. The historical GitHub Models endpoint returned a non-JSON response in live CI and is not treated as available.

**Not yet accepted as income producing:** real distribution/acquisition conversion, checkout and fulfillment integration, customer support, expense ledger with verified receipts, realized net profit. Never label an issue, product build, download or page view as a paid order.
