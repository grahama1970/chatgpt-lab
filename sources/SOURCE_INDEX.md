---
project: ChatGPT-Lab
source_version: 0.3.0
updated: 2026-06-25
canonical_manifest: sources/source-manifest.json
---

# Source Index

This file is the entry point for every ChatGPT-Lab session.

## Bootstrap rule

Before changing code, reviewing design, delegating work, or claiming system status:

1. Read `sources/source-manifest.json`.
2. Read `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`.
3. Read `sources/control-plane/OPERATING_CONTRACT.md` and `sources/control-plane/CURRENT_STATE.md`.
4. Read `sources/control-plane/DECISIONS.md` for superseding architecture decisions.
5. Fetch the current `grahama1970/agent-skills` registry.
6. Select the smallest applicable skill chain.
7. Record the control-plane ref, registry ref/hash, selected skills, controller, and any delegates in the iteration artifact.
8. Inspect the benchmark repository at the exact recorded branch or commit.
9. Treat missing CI, deployment, screenshot, or interaction evidence as `INSUFFICIENT_EVIDENCE` rather than success.

## Control authority

ChatGPT Web is the primary controller and default implementer. It selects the next bounded objective, makes GitHub branch and pull-request changes, inspects evidence, reconciles reviews, and decides whether to merge, retry, stop, or delegate.

The ChatGPT-Lab project agent is a bounded local execution adapter for capabilities unavailable to ChatGPT Web. It does not independently broaden requirements, choose the next round, merge a candidate, or declare a pass.

## Canonical sources

| Source | Location | Purpose |
|---|---|---|
| Lab control plane | `grahama1970/chatgpt-lab`, branch `main`, `sources/`, `schemas/`, `scripts/`, `docs/requirements/`, and repository root `README.md` | Requirements, operating contract, state, decisions, schemas, and iteration records |
| Requirements | `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md` | Testable requirements and authority model for the ChatGPT self-improvement loop |
| Skill registry | `grahama1970/agent-skills`, branch `main`, `SOURCES.md` and `sources/agent-skills-registry.json` | Skill discovery and progressive loading |
| Benchmark source | `grahama1970/snippets`, branch `preview-monocle-man-netlify`, path `monocle-man-site/` | Monocle Man SPA source code |
| Execution evidence | GitHub Actions associated with the benchmark commit or pull request | Tests, logs, reports, and screenshot artifacts |
| Rendered evidence | Netlify project `monocle-man-review` | Live deployed website |
| Visual evidence | Fresh desktop/mobile screenshots from the same commit and deployment | Design and responsive verification |
| Original media | `https://youtu.be/NBxByrz5BRE` | Source film and dialogue context |

## Source precedence

When sources disagree, use this order:

1. approved requirements and append-only architecture decisions at the recorded control-plane commit;
2. exact GitHub benchmark file content at the recorded candidate commit;
3. GitHub Actions output for that commit;
4. Netlify deployment metadata and rendered page;
5. fresh screenshots and interaction artifacts;
6. current selected `SKILL.md` guidance;
7. exported chats and conversational recollection.

Requirements define what must be proven. Evidence determines whether it was proven. Neither model prose nor delegated worker output can override raw artifacts.

## Refresh rules

- Refresh the control-plane branch before every new run.
- Refresh the requirements file before expanding system capabilities.
- Refresh the skill registry before each new task family or when its recorded hash changes.
- Refresh benchmark source before every patch.
- Refresh CI and deployment evidence after every commit.
- Never reuse screenshots to judge a newer commit.
- Update `sources/control-plane/CURRENT_STATE.md` whenever a capability, blocker, repository location, or deployment state changes.
- Append rather than rewrite historical entries in `sources/control-plane/DECISIONS.md` and iteration records.

## Project-source strategy

ChatGPT Project Sources cannot currently be updated by the tools exposed in this session. This GitHub repository is therefore the writable, versioned external source. `sources/PROJECT_INSTRUCTIONS.md` is the stable pointer that tells future sessions how to load it.
