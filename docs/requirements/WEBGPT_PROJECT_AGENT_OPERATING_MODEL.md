# WebGPT Project Agent Operating Model

**Status:** Slice 002 implementation contract  
**Updated:** 2026-06-26  
**Scope:** `grahama1970/chatgpt-lab` default-branch dispatcher proof

## Purpose

Prove that ChatGPT Web or WebGPT can use GitHub as durable memory and GitHub Actions as a bounded executor without relying on a local project agent for ordinary control-plane tasks.

## Control Flow

1. ChatGPT reads `agent-state/current.json`.
2. ChatGPT reads or writes `agent-state/next-command.json`.
3. ChatGPT dispatches `.github/workflows/agent-dispatch.yml` on `main` through an authenticated GitHub REST action.
4. GitHub Actions validates the command against `schemas/next-command.schema.json` and `scripts/validate_agent_state.py`.
5. GitHub Actions executes only an allowlisted command.
6. GitHub Actions writes `agent-state/last-result.json`.
7. ChatGPT reads `agent-state/last-result.json` and decides the next bounded command.

## Slice 002 Command Set

Only one command is allowed in the first proof:

```text
echo_hello
```

It proves dispatch, command validation, workflow execution, result writing, artifact upload, and commit-back to the control-plane repository. It does not prove arbitrary local execution, Monocle deployment, screenshot review, or broad project ownership.

## Required GitHub REST Surface

A GPT Action or broker needs only these authenticated operations:

- read repository file content;
- write repository file content;
- dispatch `.github/workflows/agent-dispatch.yml`;
- list workflow runs for the dispatched workflow;
- read workflow run and job metadata;
- read or download workflow artifacts.

If this surface is unavailable, a local project agent may perform the same GitHub API calls as a fallback execution adapter. That fallback does not become a planning authority.

## Stop Condition

The slice can claim capability only when a GitHub Actions run on `main` writes or uploads `agent-state/last-result.json` with:

- `command_id`;
- `status`;
- `run_id`;
- `run_attempt`;
- `head_sha`;
- `checked_at`.

The `command_id` must match `agent-state/next-command.json`, and `head_sha` must be the workflow checkout SHA for the dispatch run.
