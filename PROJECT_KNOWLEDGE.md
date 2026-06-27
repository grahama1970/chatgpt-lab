# Project Knowledge: chatgpt-lab

**Last updated:** 2026-06-27 by agent
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
- The next protocol slice is goal locking. PR 1 is contract-only: `goals/current.json` stores the active human-approved immutable goal, `schemas/goal-capsule.schema.json`, `schemas/agent-handoff.schema.json`, `schemas/human-interjection.schema.json`, and `schemas/generated-ticket.schema.json` define the durable contract, and `scripts/validate_goal_capsule.py` plus `scripts/validate_agent_ticket_contracts.py` validate examples before any orchestrator, cron, GitHub mutation, lease acquisition, or WebGPT runtime call is added.
- PR 2 is constrained to dry-run route parsing over local GitHub issue-thread fixtures. `scripts/agent_ticket_route.py route-fixture` reads fixture JSON, extracts embedded goal-locked contract blocks, checks trusted-human authority, validates active goal hash and explicit `next.subagent`, enforces goal-change-to-goal-guardian routing, detects legacy `phatgpt-task:v1` as non-routable, and emits `chatgpt_lab.route_decision.v1` with `would_mutate: false`.
- PR 13 schema normalization adds `schemas/agent-common.schema.json` and explicit `github` projection blocks to actionable contracts. The projection is validation-only: schemas and Python validators check that `next:<subagent>` and `executor:<executor>` labels match the JSON route and that generated ticket create fields match the ticket draft, but no code applies labels, posts comments, or creates tickets.
- PR 14 added the compact Tau authoring contract for agents that should not emit verbose GitHub projection JSON. `tau.agent_handoff.v1`, `tau.generated_ticket.v1`, and `tau.human_goal_change.v1` keep only GitHub target, goal hash, previous subagent, context, result or ticket/new-goal payload, rationale, next agent, required evidence, and stop condition. Tau validators derive dry-run route labels and enforce goal/authority rules; they do not mutate GitHub.
- PR 15 should add the first no-mutation GitHub-state orchestrator dry run. `scripts/agent_ticket_orchestrator.py` fetches issue/PR JSON through `gh ... view --json` or reads saved GitHub-state fixtures, converts them into router fixtures, and emits a dry-run route decision with `would_mutate: false`. It must not post comments, edit labels, create tickets, acquire leases, dispatch agents, call WebGPT, or install cron.
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
| 2026-06-27 | Start the goal-locked harness as contracts and validators only | The immutable human goal, explicit `next.subagent`, and fail-closed WebGPT/handoff contracts must validate before runtime orchestration, cron, leases, or GitHub mutation are introduced. |
| 2026-06-27 | Make PR 2 dry-run route parsing over local issue-thread fixtures only | The router should answer what the orchestrator would do without posting comments, editing labels, creating tickets, acquiring leases, dispatching agents, calling WebGPT, installing cron, or triggering workflows. |
| 2026-06-27 | Add GitHub projection as a validation contract before mutation | Agent, human, and WebGPT JSON should be almost isomorphic to GitHub create/comment/label operations, but the harness must validate projections before any future orchestrator applies them. |
| 2026-06-27 | Split compact Tau authoring from strict internal projection contracts | Smaller agents and WebGPT should emit a short handoff/ticket/goal-change JSON; Tau derives labels and validates authority while the stricter `chatgpt_lab.*` schemas remain the normalized internal contract. |
| 2026-06-27 | Keep the first GitHub-state orchestrator slice dry-run only | Fetching or reading GitHub state may prove route selection, but mutation waits for later lease/receipt slices. |

## Open Questions

- [ ] Add code-review and design-review receipts for the migrated Monocle source, workflows, and live screenshots.
- [x] Classify YouTube/no-cookie embed lifecycle aborts, including the observed Google `/js/th/` helper script abort, as expected third-party warnings while preserving fail-closed first-party network handling.
- [ ] Implement Slice 002 dry-run local-subagent refusal/receipt path.
- [ ] Prove the goal-locked harness PR 1 contract slice: goal capsule hash, human interjection, generated ticket, agent handoff examples, validators, and Source Check integration only.
- [ ] Prove the goal-locked harness PR 2 dry-run route parser: issue-thread fixtures, trusted-human authority, active goal hash, explicit `next.subagent`, goal-change routing, legacy detection, and `route_decision.v1` output with no GitHub mutation.
- [ ] Prove PR 13 schema normalization: common definitions, GitHub projection fields, projection-label validation, generated-ticket create-field matching, and no runtime mutation.
- [ ] Prove PR 14 compact Tau contracts: short agent-facing handoff/ticket/goal-change examples, Tau validators, route-decision normalization, fail-closed goal/agent/authority tests, and no GitHub mutation.
- [ ] Prove PR 15 no-mutation GitHub-state orchestrator: saved GitHub-state fixtures, `gh ... view --json` conversion, Tau comment routing, legacy task refusal, dry-run route decisions, and Source Check integration.
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
| goals/current.json | Active human-approved immutable goal capsule and deterministic goal hash |
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
| scripts/validate_goal_capsule.py | Validates `goals/current.json` and its deterministic goal hash |
| scripts/validate_agent_ticket_contracts.py | Validates goal-locked handoff, human interjection, and generated-ticket examples |
| scripts/agent_ticket_route.py | Dry-run route parser for local GitHub issue-thread fixtures |
| scripts/validate_agent_ticket_route.py | Validates route parser fixtures and expected route decisions |
| scripts/agent_ticket_orchestrator.py | No-mutation GitHub-state dry-run router over fetched or saved issue/PR JSON |
| scripts/validate_agent_ticket_orchestrator.py | Validates saved GitHub-state orchestrator fixtures |
| scripts/tau_contracts.py | Validates compact Tau agent-facing contracts and normalizes them to dry-run route decisions |
| scripts/validate_tau_contracts.py | Validates compact Tau examples |
| .github/workflows/opencode-phatgpt.yml | GitHub-event OpenCode dispatcher workflow for the PhatGPT MVP |
| .opencode/agents/phatgpt-dispatcher.md | Primary OpenCode event router |
| .opencode/agents/phatgpt-coder.md | Repo-local OpenCode coder subagent prompt |
| .opencode/agents/phatgpt-reviewer.md | Repo-local OpenCode reviewer subagent prompt |
| .opencode/agents/phatgpt-researcher.md | Repo-local OpenCode researcher subagent prompt |
| .opencode/agents/phatgpt-deployer.md | Repo-local OpenCode deployer subagent prompt |
| schemas/pr-local-task.schema.json | Machine-readable `phatgpt-task:v1` PR/issue task contract |
| schemas/goal-capsule.schema.json | Machine-readable active-goal capsule contract |
| schemas/agent-common.schema.json | Shared route, executor, GitHub projection, and label definitions for actionable harness contracts |
| schemas/agent-handoff.schema.json | Machine-readable subagent handoff contract |
| schemas/human-interjection.schema.json | Machine-readable human authority and route contract |
| schemas/generated-ticket.schema.json | Machine-readable WebGPT-generated ticket proposal contract |
| schemas/route-decision.schema.json | Machine-readable dry-run route/refusal decision contract |
| schemas/github-thread-fixture.schema.json | Machine-readable local GitHub issue/PR thread fixture contract |
| schemas/tau-agent-handoff.schema.json | Compact agent-facing handoff contract |
| schemas/tau-generated-ticket.schema.json | Compact WebGPT/ChatGPT ticket-draft contract |
| schemas/tau-human-goal-change.schema.json | Compact trusted-human goal-change contract |
| ../agent-skills/agents/phatgpt-coder/ | Shared mutating coder subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-reviewer/ | Shared read-only reviewer subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-researcher/ | Shared optional researcher/task-spec subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-deployer/ | Shared dry-run deployer/releaser subagent contract for the MVP loop |
| docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md | Operating contract for the GitHub memory/executor loop |
| docs/requirements/GOAL_LOCKED_AGENT_HARNESS.md | Contracts-only goal-lock harness slice |

## Infrastructure State

<!-- Auto-populated from /project-state --quick -->
