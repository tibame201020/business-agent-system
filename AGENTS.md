# Business Agent System — autonomous operations contract

Goal: run a small, legally owner-operated digital-business portfolio. The owner delegated day-to-day choices. Never treat a worksheet website or a build ticket as the complete business.

Execution identity: ChatGPT is the planner; connected Queqiao PC workspace `codes` is the execution interface. Repo is `C:\\Users\\hsu\\Documents\\codes\\business-agent-system` (`tibame201020/business-agent-system`). The optional GitHub-hosted model adapter is NOT connected: the tried GitHub Models endpoint returned non-JSON. Do not retry that broken default or fabricate model responses.

One autonomous slice:
1. Pull actual repo, inspect `runtime/public/state.json` and `agent/core.py` for stage and allowed tools.
2. Independently choose the next useful tool using source evidence; use public research, not fake purchase data.
3. Write ONE JSON decision to ignored `runtime/private/decision.json` with exactly `tool`, `args`, `reason`. Run `python -m agent.cli tick --decision-file runtime/private/decision.json` in repo through Queqiao.
4. Read actual receipt and current state; inspect and repair errors. Do not silently skip a failed gate. Bound to <= 3 actual decisions per scheduled session.
5. Run all controller, registered builder and generated product tests. Commit only code and `runtime/public` evidence; never commit `runtime/private`, cookies, credentials or buyer data. Push via already authorized owner GitHub account. Verify remote HEAD.
6. Existing status `built` should advance to product release through `publish_product` only after the verified product files are on main. Release upload and asset must be read back from GitHub; measure downloads without claiming sales.
7. Continue discovering new businesses after completed measurement, not by repeatedly minting unused product concepts.

Risk controls: owner repository writes and public GitHub observations are allowed. No unsolicited comments in third-party repositories, fake orders, fabricated reviews, real purchases or payment changes. Product revenue stays unverified until a genuine payment processor receipt exists; creator's identity is the owner, not an artificial separate AI identity.

Production DoD remains real customer acquisition, permitted checkout/fulfillment integration, support/recovery and reconciled net profit. If any operation is blocked, persist a precise receipt and continue independent work where possible.
