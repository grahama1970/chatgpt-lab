# Project Knowledge: chatgpt-lab

**Last updated:** 2026-06-26 11:21 EDT by agent
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

## Recent Decisions

| Date | Decision | Why |
|------|----------|-----|
| 2026-06-26 | Initialize project knowledge | Enable shared human/agent context |
| 2026-06-26 | Use path-filtered push as the WebGPT dispatch bridge | WebGPT can write repo files but cannot directly call GitHub `workflow_dispatch`; GitHub Actions can bridge that gap from a trusted workflow. |
| 2026-06-26 | Keep `agent-dispatch.yml` as the bounded executor | The proxy only translates a repo-state write into a workflow dispatch; command execution stays allowlisted and validated. |
| 2026-06-26 | Treat `apply_text_patch` as the first safe mutation command | It gives WebGPT a narrow way to edit source without arbitrary shell access or broad file rewrites. |
| 2026-06-26 | Use WebGPT as controller and Codex cloud as GitHub-native implementer | The experiment should prove a deployed GitHub/Actions/Pages loop without relying on the local project agent as the implementer. |

## Open Questions

- [ ] Add code-review and design-review receipts for the migrated Monocle source, workflows, and live screenshots.
- [ ] Classify the three `youtube-nocookie.com` telemetry aborts as expected third-party noise or adjust the proof filter.
- [ ] Implement Slice 002 dry-run local-subagent refusal/receipt path.
- [ ] Implement a bounded loop controller so ChatGPT/WebGPT invokes deterministic rounds instead of relying on prose memory.
- [ ] Prove WebGPT can create the next bounded GitHub issue/PR/task for Codex cloud, Codex can implement it, and Actions/Pages can deploy and preserve evidence.

## Key Files

| File | Purpose |
|------|---------|
| PROJECT_KNOWLEDGE.md | Shared project knowledge |
| README.md | Human entry point and current project summary |
| agent-state/next-command.json | WebGPT-writable command envelope |
| agent-state/last-result.json | GitHub Actions result receipt |
| .github/workflows/webgpt-command-dispatcher.yml | Path-filtered proxy that turns WebGPT file writes into workflow dispatches |
| .github/workflows/agent-dispatch.yml | Bounded executor workflow |
| scripts/validate_agent_state.py | Validates agent-state command/result contracts |
| scripts/apply_text_patch.py | Applies one schema-validated exact text replacement for safe mutation tests |
| docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md | Operating contract for the GitHub memory/executor loop |

## Infrastructure State

<!-- Auto-populated from /project-state --quick -->
