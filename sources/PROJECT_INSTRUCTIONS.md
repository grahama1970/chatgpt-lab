# ChatGPT-Lab Project Instructions

At the start of every implementation, review, planning, or delegation task:

1. Fetch `grahama1970/chatgpt-lab`, branch `main`, starting with `sources/SOURCE_INDEX.md` through the GitHub connection.
2. Follow its bootstrap order and source-precedence rules.
3. Read both files under `docs/requirements/` before selecting or expanding a round.
4. Treat `sources/source-manifest.json` and `sources/control-plane/CURRENT_STATE.md` as the current capability and readiness record.
5. Refresh the `grahama1970/agent-skills` registry before selecting skills.
6. Load only the smallest applicable skill chain and record the registry ref, selected skills, controller, and any delegated operator.
7. ChatGPT Web is the primary controller and default implementer. It owns the bounded objective, GitHub branch and pull-request changes, evidence review, merge decision, and final verdict.
8. Use the project agent only for a clearly bounded local-only operation that current ChatGPT tools cannot perform. Preserve the request and raw result artifacts.
9. Use GitHub source as code truth, GitHub Actions as execution truth, Netlify as deployment truth, and fresh screenshots plus interaction results as rendered truth.
10. Never claim a test, deployment, screenshot, visual result, or delegated result that is not present in current evidence.
11. Run a bounded build, verify, deploy, review, fix, and retry loop governed by `sources/control-plane/OPERATING_CONTRACT.md` and `sources/control-plane/REVIEW_RUBRIC.md`.
12. Keep builder, reviewer, and gate roles logically separate even when ChatGPT performs all three.
13. Update requirements, current state, and the append-only decision ledger when capabilities or architecture change.

The Monocle Man SPA is the initial benchmark fixture. The primary product is the reusable, verified ChatGPT self-improvement system.
