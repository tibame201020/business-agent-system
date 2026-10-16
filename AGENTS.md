# Business Agent System — autonomous operations contract

Goal: run a small, legally owner-operated digital-business portfolio. The owner delegated day-to-day choices. Never treat a worksheet website or a build ticket as the complete business.

Execution identity: ChatGPT is the planner; connected Queqiao PC workspace `codes` is the execution interface. Repo is `C:\\Users\\hsu\\Documents\\codes\\business-agent-system` (`tibame201020/business-agent-system`). The optional GitHub-hosted model adapter is NOT connected: the tried GitHub Models endpoint returned non-JSON. Do not retry that broken default or fabricate model responses.

One autonomous slice:
1. Pull actual repo, inspect `runtime/public/state.json` and `agent/core.py` for stage and allowed tools.
2. Independently choose the next useful tool using source evidence; use public research, not fake purchase data.
3. Write ONE JSON decision to ignored `runtime/private/decision.json` with exactly `tool`, `args`, `reason`. Run `python -m agent.cli tick --decision-file runtime/private/decision.json` in repo through Queqiao.
4. Read actual receipt and current state; inspect and repair errors. Do not silently skip a failed gate. Bound to <= 3 actual decisions per scheduled session.
5. Run all controller, registered builder and generated product tests. Commit only code and `runtime/public` evidence; never commit `runtime/private`, cookies, credentials or buyer data. Push via already authorized owner GitHub account. Verify remote HEAD.
6. Existing state is `measured` for the first beta. Start a new bounded `discover` cycle, but do not neglect the published beta: monitor download/feedback evidence, decide whether to improve or retire with real measurements. For any new offer, move `built` to `publish_product` only after verified files are on main, then `measure_product`.
7. Do not repeatedly mint concepts without building, distributing and measuring the current bounded experiment.

Risk controls: owner repository writes and public GitHub observations are allowed. No unsolicited comments in third-party repositories, fake orders, fabricated reviews, real purchases or payment changes. Product revenue stays unverified until a genuine payment processor receipt exists; creator's identity is the owner, not an artificial separate AI identity.

Production DoD remains real customer acquisition, permitted checkout/fulfillment integration, support/recovery and reconciled net profit. If any operation is blocked, persist a precise receipt and continue independent work where possible.
