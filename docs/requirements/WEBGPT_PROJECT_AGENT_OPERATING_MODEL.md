# WebGPT Project Agent Operating Model

**Status:** Slice 002 implementation contract  
**Updated:** 2026-06-26  
**Scope:** `grahama1970/chatgpt-lab` default-branch dispatcher proof

## Purpose

Prove that ChatGPT Web or WebGPT can use GitHub as durable memory and GitHub Actions as a bounded executor without relying on a local project agent for ordinary control-plane tasks.

## Control Flow

1. ChatGPT reads `agent-state/current.json`.
2. ChatGPT reads or writes `agent-state/next-command.json`.
3. If ChatGPT has direct Actions write access, it dispatches `.github/workflows/agent-dispatch.yml` on `main` through an authenticated GitHub REST action.
4. If direct workflow dispatch is unavailable, ChatGPT writes `agent-state/next-command.json`; `.github/workflows/webgpt-command-dispatcher.yml` wakes on that path-filtered push and dispatches `.github/workflows/agent-dispatch.yml`.
5. GitHub Actions validates the command against `schemas/next-command.schema.json` and `scripts/validate_agent_state.py`.
6. GitHub Actions executes only an allowlisted command.
7. GitHub Actions writes `agent-state/last-result.json`.
8. ChatGPT reads `agent-state/last-result.json` and decides the next bounded command.

## Slice 002 Command Set

The first proof allowed only one command:

```text
echo_hello
```

It proves dispatch, command validation, workflow execution, result writing, artifact upload, and commit-back to the control-plane repository. It does not prove arbitrary local execution, Monocle deployment, screenshot review, or broad project ownership.

The next allowed command is intentionally narrow:

```text
apply_text_patch
```

`apply_text_patch` may only mutate allowlisted text files under `monocle-man-site/`. The command payload must validate against `schemas/commands/apply-text-patch.schema.json`, include `exact_old`, `exact_new`, and `expected_replacements: 1`, and produce a touched-file manifest so the executor commits only the intended file plus `agent-state/last-result.json`.

## Required GitHub REST Surface

A GPT Action or broker needs only these authenticated operations for the direct path:

- read repository file content;
- write repository file content;
- dispatch `.github/workflows/agent-dispatch.yml`;
- list workflow runs for the dispatched workflow;
- read workflow run and job metadata;
- read or download workflow artifacts.

If this surface is unavailable, a local project agent may perform the same GitHub API calls as a fallback execution adapter. That fallback does not become a planning authority.

For WebGPT surfaces that can write repository files but cannot call workflow dispatch, the supported bridge is `.github/workflows/webgpt-command-dispatcher.yml`. It requires only a push to `agent-state/next-command.json`; GitHub Actions then performs the workflow-dispatch call with `actions: write`.

## Stop Condition

The slice can claim capability only when a GitHub Actions run on `main` writes or uploads `agent-state/last-result.json` with:

- `command_id`;
- `status`;
- `run_id`;
- `run_attempt`;
- `head_sha`;
- `checked_at`.

The `command_id` must match `agent-state/next-command.json`, and `head_sha` must be the workflow checkout SHA for the dispatch run.
