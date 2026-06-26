---
project: ChatGPT-Lab
source_version: 0.4.0
updated: 2026-06-26
canonical_manifest: sources/source-manifest.json
---

# Source Index

This file is the entry point for every ChatGPT-Lab session.

## Bootstrap rule

Before changing code, reviewing design, delegating work, or claiming system status:

1. Read `sources/source-manifest.json`.
2. Read `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`.
3. Read `docs/requirements/CONTROL_AUTHORITY.md`.
4. For Monocle Man work, read `docs/requirements/MONOCLE_MAN_REACT_CONTRACT.md` before touching product code.
5. Read `docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md`.
6. Read `agent-state/current.json`, `agent-state/skill-router.json`, `agent-state/next-command.json`, and `agent-state/last-result.json`.
7. Read `sources/control-plane/OPERATING_CONTRACT.md` and `sources/control-plane/CURRENT_STATE.md`.
8. Read `sources/control-plane/DECISIONS.md` for superseding architecture decisions.
9. Fetch the current `grahama1970/agent-skills` registry.
10. Select the smallest applicable skill chain.
11. Use web search for current external references when the task depends on browser, React, accessibility, deployment, API, or standards behavior.
12. Record the control-plane ref, registry ref/hash, selected skills, controller, and any delegates in the iteration artifact.
13. Inspect the benchmark repository at the exact recorded branch or commit.
14. Treat missing CI, deployment, screenshot, or interaction evidence as `INSUFFICIENT_EVIDENCE` rather than success.

## Plan-first rule

If the user does not provide a comprehensive implementation plan, ChatGPT must create one before editing product code. The plan must define the product goal, file boundaries, React components or files, selectors, action IDs, accessibility obligations, GitHub Actions checks, screenshots, deployment proof, and stop condition.

For the Monocle Man SPA, `docs/requirements/MONOCLE_MAN_REACT_CONTRACT.md` is the required deterministic plan unless a stricter replacement is committed first.

## Control authority

ChatGPT Web is the primary controller and default implementer. It selects the next bounded objective, makes GitHub branch and pull-request changes, inspects evidence, reconciles reviews, and decides whether to merge, retry, stop, or delegate.

The ChatGPT-Lab project agent is a bounded local execution adapter for capabilities unavailable to ChatGPT Web. It does not independently broaden requirements, choose the next round, merge a candidate, or declare a pass.

## Canonical sources

| Source | Location | Purpose |
|---|---|---|
| Lab control plane | `grahama1970/chatgpt-lab`, branch `main`, `sources/`, `schemas/`, `scripts/`, `docs/requirements/`, and repository root `README.md` | Requirements, operating contract, state, decisions, schemas, and iteration records |
| Core requirements | `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md` | Testable requirements and Slice 001 evidence contract |
| Control authority | `docs/requirements/CONTROL_AUTHORITY.md` | Normative controller, delegate, concurrency, and default write-path rules |
| Monocle Man React contract | `docs/requirements/MONOCLE_MAN_REACT_CONTRACT.md` | Required React components, selectors, action IDs, and deterministic CI checks for the SPA |
| WebGPT operating model | `docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md` | Slice 002 GitHub dispatcher and repo-state operating contract |
| Agent state | `agent-state/current.json`, `agent-state/skill-router.json`, `agent-state/next-command.json`, `agent-state/last-result.json` | Machine-readable state, routing, command, and workflow-result memory |
| Skill registry | `grahama1970/agent-skills`, branch `main`, `SOURCES.md` and `sources/agent-skills-registry.json` | Skill discovery and progressive loading |
| Benchmark source | `grahama1970/snippets`, branch `preview-monocle-man-netlify`, path `monocle-man-site/` | Monocle Man SPA source code |
| Execution evidence | GitHub Actions associated with the benchmark commit or pull request | Tests, logs, reports, and screenshot artifacts |
| Rendered evidence | Netlify project `monocle-man-review` | Live deployed website |
| Visual evidence | Fresh desktop/mobile screenshots from the same commit and deployment | Design and responsive verification |
| Original media | `https://youtu.be/NBxByrz5BRE` | Source film and dialogue context |

## Source precedence

When sources disagree, use this order:

1. approved requirements, control-authority rules, the Monocle Man React contract, and append-only architecture decisions at the recorded control-plane commit;
2. exact GitHub benchmark file content at the recorded candidate commit;
3. GitHub Actions output for that commit;
4. Netlify deployment metadata and rendered page;
5. fresh screenshots and interaction artifacts;
6. current selected `SKILL.md` guidance;
7. exported chats and conversational recollection.

Requirements define what must be proven. Evidence determines whether it was proven. Neither model prose nor delegated worker output can override raw artifacts.

## Refresh rules

- Refresh the control-plane branch before every new run.
- Refresh requirements and the Monocle Man React contract before expanding system capabilities.
- Refresh `agent-state/*.json` before issuing or evaluating a dispatcher command.
- Refresh the skill registry before each new task family or when its recorded hash changes.
- Refresh benchmark source before every patch.
- Refresh CI and deployment evidence after every commit.
- Never reuse screenshots to judge a newer commit.
- Update `sources/control-plane/CURRENT_STATE.md` whenever a capability, blocker, repository location, or deployment state changes.
- Append rather than rewrite historical entries in `sources/control-plane/DECISIONS.md` and iteration records.

## Project-source strategy

ChatGPT Project Sources cannot currently be updated by the tools exposed in this session. This GitHub repository is therefore the writable, versioned external source. `sources/PROJECT_INSTRUCTIONS.md` is the stable pointer that tells future sessions how to load it.
