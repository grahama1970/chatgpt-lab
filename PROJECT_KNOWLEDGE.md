# Project Knowledge: chatgpt-lab

**Last updated:** 2026-06-26 18:02 EDT by agent
**Status:** Active development

## Current Understanding

- PhatGPT-LAB is a GitHub-backed control plane for proving ChatGPT/WebGPT can drive bounded software improvement through durable repo state, CI evidence, and iteration records.
- The project now has a proven WebGPT-to-GitHub-Actions bridge: WebGPT writes `agent-state/next-command.json`; `.github/workflows/webgpt-command-dispatcher.yml` wakes on that path-filtered push; it dispatches `.github/workflows/agent-dispatch.yml`; the executor writes `agent-state/last-result.json`.
- Direct WebGPT `workflow_dispatch` is unavailable in the current connector, but the file-write bridge works for the bounded `echo_hello` command.
- The first safe mutation command is proven through the bridge. `apply_text_patch` requires a schema-validated payload, only allows selected `monocle-man-site/**` text files, and refuses unless the old text appears exactly once.
- The current proof command is `apply-text-patch-proof-001`; `agent-state/last-result.json` records `status: PASS`, executor run `28245515891`, WebGPT command commit `5450331fcf932ddcbf79cbea490005f250c7d29e`, and result commit `064f5fd5b2b52bd1874c205edaeb616f7eae0533`.
- Follow-on proof for the mutated commit exists: Source Check run `28245666829`, Monocle Benchmark run `28245666824`, GitHub Pages live proof run `28245666963`, and `delivery-proof/monocle-man/latest/deployment-proof.json` records `status: PASS`.
- This proves the narrow GitHub memory/executor loop, one bounded source mutation, one WebGPT-created PR loop, real merge, and post-merge Pages proof. It does not prove broad autonomous project ownership, arbitrary command execution, or Tailscale/WebGPT reachability to the local broker.
- The intended operating model is now explicit: WebGPT controls the task, names required skills/contracts, creates or updates GitHub issues/PRs/tasks, the Codex cloud agent implements GitHub-native code changes, GitHub Actions/Pages produce proof, and PhatGPT-LAB records the iteration.
- WebGPT deliverables should be executable GitHub work packets, not advisory prose: exact objective, skills, files, validation command, deployment/evidence expectation, and fail-closed verdict rules.
- The next cloud-agent handoff artifact is `.github/workflows/assign-copilot-agent.yml`. It uses GitHub's public-preview Agent Tasks API to start a Copilot cloud-agent task for a bounded issue and records `agent-state/last-result.json`.
- The handoff workflow is not proven until `COPILOT_AGENT_TASK_TOKEN` is configured and a run against issue #5 either starts a Copilot task or records `BLOCKED_CLOUD_AGENT_AUTH` / `BLOCKED_CLOUD_AGENT_API`.
- The local-worker architecture should reject vague PRs/issues before doing work. `scripts/phatgpt_local_worker_cycle.py` now provides the first dry-run slice: inspect one GitHub PR/issue, require a `phatgpt-task:v1` JSON block, validate allowed commands/paths/evidence/stop condition, and write a local-subagent receipt.
- The preferred MVP trigger is GitHub event or `opencode serve` -> OpenCode primary dispatcher -> role subagent. Cron/local worker execution remains a fallback watchdog and deterministic smoke harness, not the primary architecture.
- The MVP event loop uses four shared agent contracts under `/home/graham/workspace/experiments/agent-skills/agents`: `phatgpt-coder` for the only mutating implementation role, `phatgpt-reviewer` for read-only pass/needs-changes/blocked review, `phatgpt-researcher` for optional task-block preparation/refusal, and `phatgpt-deployer` for dry-run release/deploy gate receipts.
- The PhatGPT coder, reviewer, researcher, and deployer must follow `best-practices-github-ticket`: ticket type, target, route/agent metadata, required proof, lease-before-work, separate repair/review/release, proof-based comments/closure, and reviewer PR comments as the trace.
- Subagent receipt summaries may be mirrored into `$memory` collection `subagent_memory` for recall, but canonical proof remains GitHub PR comments, CI run IDs, raw receipt files, screenshots, and deployment proof JSON.
- The OpenCode/GitHub event loop has a narrow PR-scope proof in PR #8: the valid task block triggered a coder change to `monocle-man-site/src/main.jsx`, checks passed at head `146d51dc54b977dab01470a0ae288af38b9f7813`, and the reviewer commented `PASS`. This does not prove live deployment ownership because Pages deployment is skipped on PR branches.
- PR #9 is the first WebGPT-created PR test and is useful negative evidence: it had an empty body, no `best-practices-github-ticket` metadata, and no `phatgpt-task:v1` block, so the worker refused it with a PR comment instead of inferring work.
- PR #10 is the first valid WebGPT-created loop proof. WebGPT created branch `webgpt-mvp-loop-caption-002` and a valid PR task block; OpenCode applied the bounded Monocle caption change; local reviewer re-ran checks on the PR branch; a local rebase from a non-`github-actions[bot]` identity cleared the `action_required` check state; the dry-run deployer reached `WOULD_MERGE` on head `1bdc732c671ceedeed728e01c498b50ed24ccd78`; PR #10 was squash-merged as `d4c013ce98fd78ef4efcbdc716ec8523db9afaed`; and post-merge Pages proof passed for classifier commit `0d987970d268a212b31683881d2391c0c015a577`.
- The PR #10 post-merge proof run is `28265880104`; `delivery-proof/monocle-man/latest/deployment-proof.json` records `status: PASS`, `blocking_network_errors_count: 0`, `expected_third_party_network_warnings_count: 4`, and screenshots for desktop, modal, mobile, and mobile menu. The tracked release receipt is `iterations/2026-06-26-webgpt-mvp-loop-caption-002/release-receipt.json`.
- `controller-state/current.json` is the evidence-derived bounded controller surface. It is generated and checked by `scripts/update_controller_state.py` from the PR #10 release receipt and live Pages proof; the current state is `READY_FOR_NEXT_TASK`, and the next action is for WebGPT to create a bounded PR/issue with a valid `phatgpt-task:v1` block.
- WebGPT-created PRs must use `.github/pull_request_template.md`. The `target.pr` field can be `null` when the task block lives in the PR being processed, which avoids requiring WebGPT to know the PR number before opening the PR.
- The OpenCode GitHub event workflow model is configured through repository variables. Current smoke configuration uses `PHATGPT_OPENCODE_MODEL=opencode/deepseek-v4-flash-free` and `PHATGPT_OPENCODE_VARIANT=medium`; earlier `opencode/gpt-5.5` attempts were blocked by account balance, and unqualified `gpt-5.5` failed CLI validation because OpenCode requires `provider/model`.
- The local `opencode serve` broker surface is reachable through the scillm-managed Docker service. `docker-opencode-serve-1` was rebuilt/recreated from `docker-opencode-serve`, listens on `127.0.0.1:4098`, returns `401 Unauthorized` without Basic auth, and `http://127.0.0.1:4001/v1/scillm/opencode/health` returns `status: ok`, `health.healthy: true`, OpenCode `1.17.12`. Tailscale is active at `100.102.12.64`, but `opencode serve` and scillm are bound to localhost, so remote Tailscale broker access is intentionally not proven or exposed for this MVP.

## Recent Decisions

| Date | Decision | Why |
|------|----------|-----|
| 2026-06-26 | Initialize project knowledge | Enable shared human/agent context |
| 2026-06-26 | Use path-filtered push as the WebGPT dispatch bridge | WebGPT can write repo files but cannot directly call GitHub `workflow_dispatch`; GitHub Actions can bridge that gap from a trusted workflow. |
| 2026-06-26 | Keep `agent-dispatch.yml` as the bounded executor | The proxy only translates a repo-state write into a workflow dispatch; command execution stays allowlisted and validated. |
| 2026-06-26 | Treat `apply_text_patch` as the first safe mutation command | It gives WebGPT a narrow way to edit source without arbitrary shell access or broad file rewrites. |
| 2026-06-26 | Use WebGPT as controller and Codex cloud as GitHub-native implementer | The experiment should prove a deployed GitHub/Actions/Pages loop without relying on the local project agent as the implementer. |
| 2026-06-26 | Draft the minimal Agent Tasks API workflow before a GitHub App design | The next question is only whether PhatGPT-LAB can hand issue #5 to Copilot cloud and observe a receipt; service-account architecture is premature. |
| 2026-06-26 | Require implementation-ready PR/issue task blocks before local worker execution | The local subagent must refuse vague work with a receipt instead of inferring architecture, acceptance criteria, or proof standards. |
| 2026-06-26 | Prefer GitHub event or `opencode serve` over cron as the MVP trigger | OpenCode can be driven by GitHub events or HTTP/OpenAPI server, and the primary agent can route to PhatGPT subagents. Cron/local worker remains fallback/smoke. |
| 2026-06-26 | Split MVP event loop into coder, reviewer, optional researcher, and dry-run deployer agents | The coder is the only mutating role; the reviewer is read-only and returns pass/needs-changes/blocked; the researcher prepares task blocks or refuses vague work; the deployer only checks release gates and writes receipts. |
| 2026-06-26 | Make `best-practices-github-ticket` mandatory for PhatGPT event agents | PRs/issues are the queue contract; agents must lease one ticket, honor route metadata, preserve proof, comment verdicts in the PR, and keep repair and review separate. |
| 2026-06-26 | Use OpenCode OAuth `opencode/gpt-5.5` medium as the default event agent model | Repository secret `OPENCODE_API_KEY` is required; run `28257657868` showed unqualified `gpt-5.5` fails CLI validation, while local `opencode models opencode` lists `opencode/gpt-5.5`. |
| 2026-06-26 | Add a PR template and allow `target.pr: null` for in-PR task blocks | WebGPT cannot reliably know the PR number before opening a PR; the dispatcher can treat `null` as the current PR while still refusing missing or malformed task contracts. |
| 2026-06-26 | Treat `opencode serve` as locally available and Tailscale exposure as a future gate | The proven MVP loop uses GitHub events, not remote broker calls; the scillm-managed Docker service is healthy on localhost, while Tailscale exposure remains intentionally unproven because the services bind to `127.0.0.1`. |
| 2026-06-26 | Classify Google `/js/th/` embed-helper aborts as expected third-party warnings | Live Pages proof showed the YouTube no-cookie embed can abort a Google helper script during modal lifecycle; first-party failures and unrelated third-party failures remain blocking. |
| 2026-06-26 | Add evidence-derived `controller-state/current.json` as the repeatable next-action surface | WebGPT should not infer the next move from prose; Source Check now validates that controller state matches tracked release and Pages proof evidence. |

## Open Questions

- [ ] Add code-review and design-review receipts for the migrated Monocle source, workflows, and live screenshots.
- [x] Classify YouTube/no-cookie embed lifecycle aborts, including the observed Google `/js/th/` helper script abort, as expected third-party warnings while preserving fail-closed first-party network handling.
- [ ] Implement Slice 002 dry-run local-subagent refusal/receipt path.
- [x] Add a bounded controller state file and Source Check gate: `controller-state/current.json` is generated from release proof and `scripts/update_controller_state.py --check` fails on drift.
- [x] Prove WebGPT can create a bounded GitHub PR with a valid `phatgpt-task:v1` block: PR #10 (`webgpt-mvp-loop-caption-002`) was created by WebGPT, carried the task block, triggered the PhatGPT OpenCode event worker, and reached dry-run deployer `WOULD_MERGE` after real GitHub checks passed on the latest head.
- [x] Prove the PR #10 release lane through real merge and post-merge live Pages proof: squash merge `d4c013ce98fd78ef4efcbdc716ec8523db9afaed`, Pages run `28265880104`, proof commit `26b82c4`, and release receipt `iterations/2026-06-26-webgpt-mvp-loop-caption-002/release-receipt.json`.
- [ ] Configure `COPILOT_AGENT_TASK_TOKEN` and run `Assign Copilot Agent` for issue #5.
- [x] Trigger `.github/workflows/opencode-phatgpt.yml` from a real PR comment and preserve PR trace comments for a valid task block in PR #8.
- [x] Validate `opencode serve` locally as the broker control surface: Docker service `docker-opencode-serve-1` is healthy, direct `:4098` requests require auth, and scillm health reports OpenCode `1.17.12`.
- [x] Decide Tailscale broker exposure for this MVP: not required for the proven GitHub-event loop; current services bind to `127.0.0.1`, so remote Tailscale exposure remains a separate future gate.
- [x] Keep the local worker as fallback/smoke only after the OpenCode event path is tested; PR #10 has both OpenCode event evidence and local reviewer/deployer fail-closed receipts.
- [ ] Add bounded execution mode only after the dry-run receipt path is accepted.

## Key Files

| File | Purpose |
|------|---------|
| PROJECT_KNOWLEDGE.md | Shared project knowledge |
| README.md | Human entry point and current project summary |
| agent-state/next-command.json | WebGPT-writable command envelope |
| agent-state/last-result.json | GitHub Actions result receipt |
| controller-state/current.json | Evidence-derived current controller state and next action |
| .github/workflows/webgpt-command-dispatcher.yml | Path-filtered proxy that turns WebGPT file writes into workflow dispatches |
| .github/workflows/agent-dispatch.yml | Bounded executor workflow |
| .github/workflows/assign-copilot-agent.yml | Manual Agent Tasks API handoff test for Copilot cloud |
| scripts/validate_agent_state.py | Validates agent-state command/result contracts |
| scripts/apply_text_patch.py | Applies one schema-validated exact text replacement for safe mutation tests |
| scripts/start_copilot_agent_task.py | Starts a bounded Copilot cloud-agent task and writes a fail-closed receipt |
| scripts/phatgpt_local_worker_cycle.py | Short-lived PR/issue worker that validates or refuses structured local task blocks |
| scripts/phatgpt_deployer_cycle.py | Dry-run release/deploy gate checker that writes deployer receipts |
| scripts/phatgpt_review_deployer_receipt.py | Read-only reviewer for deployer receipts |
| scripts/phatgpt_memory_sync.py | Optional compact `$memory` index writer for receipt summaries |
| scripts/update_controller_state.py | Generates/checks `controller-state/current.json` from tracked release proof |
| .github/workflows/opencode-phatgpt.yml | GitHub-event OpenCode dispatcher workflow for the PhatGPT MVP |
| .opencode/agents/phatgpt-dispatcher.md | Primary OpenCode event router |
| .opencode/agents/phatgpt-coder.md | Repo-local OpenCode coder subagent prompt |
| .opencode/agents/phatgpt-reviewer.md | Repo-local OpenCode reviewer subagent prompt |
| .opencode/agents/phatgpt-researcher.md | Repo-local OpenCode researcher subagent prompt |
| .opencode/agents/phatgpt-deployer.md | Repo-local OpenCode deployer subagent prompt |
| schemas/pr-local-task.schema.json | Machine-readable `phatgpt-task:v1` PR/issue task contract |
| ../agent-skills/agents/phatgpt-coder/ | Shared mutating coder subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-reviewer/ | Shared read-only reviewer subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-researcher/ | Shared optional researcher/task-spec subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-deployer/ | Shared dry-run deployer/releaser subagent contract for the MVP loop |
| docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md | Operating contract for the GitHub memory/executor loop |

## Infrastructure State

<!-- Auto-populated from /project-state --quick -->
