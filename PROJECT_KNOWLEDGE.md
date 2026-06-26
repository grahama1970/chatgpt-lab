# Project Knowledge: chatgpt-lab

**Last updated:** 2026-06-26 08:46 EDT by agent
**Status:** Active development

## Current Understanding

- PhatGPT-LAB is a GitHub-backed control plane for proving ChatGPT/WebGPT can drive bounded software improvement through durable repo state, CI evidence, and iteration records.
- The project now has a proven WebGPT-to-GitHub-Actions bridge: WebGPT writes `agent-state/next-command.json`; `.github/workflows/webgpt-command-dispatcher.yml` wakes on that path-filtered push; it dispatches `.github/workflows/agent-dispatch.yml`; the executor writes `agent-state/last-result.json`.
- Direct WebGPT `workflow_dispatch` is unavailable in the current connector, but the file-write bridge works for the bounded `echo_hello` command.
- The next safe mutation command is `apply_text_patch`: it requires a schema-validated payload, only allows selected `monocle-man-site/**` text files, and refuses unless the old text appears exactly once.
- The current proof command is `push-proof-002`; `agent-state/last-result.json` records `status: PASS`, run `28238575766`, and result commit `59e44c80d1acb864b6583bd17c1369d873692030`.
- This proves the narrow GitHub memory/executor loop. It does not prove broad autonomous project ownership, Monocle live deployment, arbitrary command execution, or visual review closure.

## Recent Decisions

| Date | Decision | Why |
|------|----------|-----|
| 2026-06-26 | Initialize project knowledge | Enable shared human/agent context |
| 2026-06-26 | Use path-filtered push as the WebGPT dispatch bridge | WebGPT can write repo files but cannot directly call GitHub `workflow_dispatch`; GitHub Actions can bridge that gap from a trusted workflow. |
| 2026-06-26 | Keep `agent-dispatch.yml` as the bounded executor | The proxy only translates a repo-state write into a workflow dispatch; command execution stays allowlisted and validated. |

## Open Questions

- [ ] Prove `apply_text_patch` through the WebGPT file-write bridge.
- [ ] How should iteration records reference WebGPT prompt/response artifacts that live under `artifacts/webgpt/`?
- [ ] When should Monocle live deployment proof resume after the control-plane bridge is documented?

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
