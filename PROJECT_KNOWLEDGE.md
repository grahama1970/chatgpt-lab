# Project Knowledge: chatgpt-lab

**Last updated:** 2026-06-26 13:07 EDT by agent
**Status:** Active development

## Current Understanding

- PhatGPT-LAB is a GitHub-backed control plane for proving ChatGPT/WebGPT can drive bounded software improvement through durable repo state, CI evidence, and iteration records.
- The project now has a proven WebGPT-to-GitHub-Actions bridge: WebGPT writes `agent-state/next-command.json`; `.github/workflows/webgpt-command-dispatcher.yml` wakes on that path-filtered push; it dispatches `.github/workflows/agent-dispatch.yml`; the executor writes `agent-state/last-result.json`.
- Direct WebGPT `workflow_dispatch` is unavailable in the current connector, but the file-write bridge works for the bounded `echo_hello` command.
- The first safe mutation command is proven through the bridge. `apply_text_patch` requires a schema-validated payload, only allows selected `monocle-man-site/**` text files, and refuses unless the old text appears exactly once.
- The current proof command is `apply-text-patch-proof-001`; `agent-state/last-result.json` records `status: PASS`, executor run `28245515891`, WebGPT command commit `5450331fcf932ddcbf79cbea490005f250c7d29e`, and result commit `064f5fd5b2b52bd1874c205edaeb616f7eae0533`.
- Follow-on proof for the mutated commit exists: Source Check run `28245666829`, Monocle Benchmark run `28245666824`, GitHub Pages live proof run `28245666963`, and `delivery-proof/monocle-man/latest/deployment-proof.json` records `status: PASS`.
- This proves the narrow GitHub memory/executor loop and one bounded source mutation. It does not prove broad autonomous project ownership, arbitrary command execution, local-subagent delegation, or visual/design review closure.
- The intended operating model is now explicit: WebGPT controls the task, names required skills/contracts, creates or updates GitHub issues/PRs/tasks, the Codex cloud agent implements GitHub-native code changes, GitHub Actions/Pages produce proof, and PhatGPT-LAB records the iteration.
- WebGPT deliverables should be executable GitHub work packets, not advisory prose: exact objective, skills, files, validation command, deployment/evidence expectation, and fail-closed verdict rules.
- The next cloud-agent handoff artifact is `.github/workflows/assign-copilot-agent.yml`. It uses GitHub's public-preview Agent Tasks API to start a Copilot cloud-agent task for a bounded issue and records `agent-state/last-result.json`.
- The handoff workflow is not proven until `COPILOT_AGENT_TASK_TOKEN` is configured and a run against issue #5 either starts a Copilot task or records `BLOCKED_CLOUD_AGENT_AUTH` / `BLOCKED_CLOUD_AGENT_API`.
- The local-worker architecture should reject vague PRs/issues before doing work. `scripts/phatgpt_local_worker_cycle.py` now provides the first dry-run slice: inspect one GitHub PR/issue, require a `phatgpt-task:v1` JSON block, validate allowed commands/paths/evidence/stop condition, and write a local-subagent receipt.
- The preferred MVP trigger is GitHub event or `opencode serve` -> OpenCode primary dispatcher -> role subagent. Cron/local worker execution remains a fallback watchdog and deterministic smoke harness, not the primary architecture.
- The MVP event loop uses three shared agent contracts under `/home/graham/workspace/experiments/agent-skills/agents`: `phatgpt-coder` for the only mutating implementation role, `phatgpt-reviewer` for read-only pass/needs-changes/blocked review, and `phatgpt-researcher` for optional task-block preparation/refusal.
- The PhatGPT coder, reviewer, and researcher must follow `best-practices-github-ticket`: ticket type, target, route/agent metadata, required proof, lease-before-work, separate repair/review, proof-based comments/closure, and reviewer PR comments as the trace.
- The OpenCode GitHub event workflow is not yet proven live. A source-level workflow and `.opencode/agents` prompts exist, but the next gate is a real `/opencode` or `/phatgpt` PR comment event that leaves a PR trace comment.
- The OpenCode GitHub event workflow defaults to OpenCode OAuth model `gpt-5.5` with `medium` reasoning. The GitHub action rejected `opencode/gpt-5.5` and suggested `gpt-5.5`; local `opencode models` displays provider-qualified ids, but the action's OpenCode provider expects the unqualified model id. Manual dispatch may override the model for smoke tests, including `deepseek-v4-flash`.

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
| 2026-06-26 | Split MVP event loop into coder, reviewer, and optional researcher agents | The coder is the only mutating role; the reviewer is read-only and returns pass/needs-changes/blocked; the researcher prepares task blocks or refuses vague work. |
| 2026-06-26 | Make `best-practices-github-ticket` mandatory for PhatGPT event agents | PRs/issues are the queue contract; agents must lease one ticket, honor route metadata, preserve proof, comment verdicts in the PR, and keep repair and review separate. |
| 2026-06-26 | Use OpenCode OAuth `gpt-5.5` medium as the default event agent model | Live GitHub Action run `28257495934` rejected `opencode/gpt-5.5` and suggested `gpt-5.5`; the workflow keeps model/variant override inputs for smoke tests. |

## Open Questions

- [ ] Add code-review and design-review receipts for the migrated Monocle source, workflows, and live screenshots.
- [ ] Classify the three `youtube-nocookie.com` telemetry aborts as expected third-party noise or adjust the proof filter.
- [ ] Implement Slice 002 dry-run local-subagent refusal/receipt path.
- [ ] Implement a bounded loop controller so ChatGPT/WebGPT invokes deterministic rounds instead of relying on prose memory.
- [ ] Prove WebGPT can create the next bounded GitHub issue/PR/task for Codex cloud, Codex can implement it, and Actions/Pages can deploy and preserve evidence.
- [ ] Configure `COPILOT_AGENT_TASK_TOKEN` and run `Assign Copilot Agent` for issue #5.
- [ ] Trigger `.github/workflows/opencode-phatgpt.yml` from a real PR comment and preserve the OpenCode trace comment.
- [ ] Validate `opencode serve` locally as the Tailscale/broker control surface.
- [ ] Keep the local worker as fallback/smoke only after the OpenCode event path is tested.
- [ ] Add bounded execution mode only after the dry-run receipt path is accepted.

## Key Files

| File | Purpose |
|------|---------|
| PROJECT_KNOWLEDGE.md | Shared project knowledge |
| README.md | Human entry point and current project summary |
| agent-state/next-command.json | WebGPT-writable command envelope |
| agent-state/last-result.json | GitHub Actions result receipt |
| .github/workflows/webgpt-command-dispatcher.yml | Path-filtered proxy that turns WebGPT file writes into workflow dispatches |
| .github/workflows/agent-dispatch.yml | Bounded executor workflow |
| .github/workflows/assign-copilot-agent.yml | Manual Agent Tasks API handoff test for Copilot cloud |
| scripts/validate_agent_state.py | Validates agent-state command/result contracts |
| scripts/apply_text_patch.py | Applies one schema-validated exact text replacement for safe mutation tests |
| scripts/start_copilot_agent_task.py | Starts a bounded Copilot cloud-agent task and writes a fail-closed receipt |
| scripts/phatgpt_local_worker_cycle.py | Short-lived PR/issue worker that validates or refuses structured local task blocks |
| .github/workflows/opencode-phatgpt.yml | GitHub-event OpenCode dispatcher workflow for the PhatGPT MVP |
| .opencode/agents/phatgpt-dispatcher.md | Primary OpenCode event router |
| .opencode/agents/phatgpt-coder.md | Repo-local OpenCode coder subagent prompt |
| .opencode/agents/phatgpt-reviewer.md | Repo-local OpenCode reviewer subagent prompt |
| .opencode/agents/phatgpt-researcher.md | Repo-local OpenCode researcher subagent prompt |
| schemas/pr-local-task.schema.json | Machine-readable `phatgpt-task:v1` PR/issue task contract |
| ../agent-skills/agents/phatgpt-coder/ | Shared mutating coder subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-reviewer/ | Shared read-only reviewer subagent contract for the MVP loop |
| ../agent-skills/agents/phatgpt-researcher/ | Shared optional researcher/task-spec subagent contract for the MVP loop |
| docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md | Operating contract for the GitHub memory/executor loop |

## Infrastructure State

<!-- Auto-populated from /project-state --quick -->
