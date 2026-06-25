# ChatGPT-Lab

ChatGPT-Lab is a GitHub-backed control plane for proving that ChatGPT Web can build and improve software projects directly.

The practical goal is to keep project requirements, instructions, operating contracts, current state, schemas, scripts, evidence records, exported chats, and iteration history in a repository that ChatGPT Web can read during future sessions. ChatGPT Project Sources are not currently writable from this environment, so this repository becomes the external source of truth that can be updated, reviewed, validated, and reloaded.

The local project directory is `chatgpt-lab`. The intended GitHub repository target is `grahama1970/chatgpt-lab`.

## Why This Exists

ChatGPT can write and improve projects, but a reliable self-improvement loop needs more than conversation memory. It needs stable files, exact source references, deterministic checks, rendered screenshots, review artifacts, and evidence that survives across sessions.

This repo gives future ChatGPT Web sessions a durable project source. It records:

1. what the project is trying to build;
2. which sources are canonical;
3. which requirements must be satisfied;
4. which skills and repositories should be loaded;
5. which prior chats explain intent and decisions;
6. what the current blockers are;
7. what evidence is required before a result can be accepted; and
8. how each iteration should be recorded.

## Project Mission

The mission is to prove a reusable, evidence-driven project self-improvement system controlled from ChatGPT Web.

The ultimate target is a loop where ChatGPT Web does not need a separate code agent as the default implementer. ChatGPT should be able to propose code changes, commit them through the available GitHub path, have GitHub CI test them, inspect CI artifacts and screenshots, collaborate through `$ask webgpt`, and continue the next iteration from recorded evidence.

The two primary collaboration control-plane surfaces are:

1. the GitHub repository, which holds durable requirements, state, source references, workflows, and evidence; and
2. `$ask webgpt`, which provides browser-backed planning, review, oracle, and task-collaboration workflows with preserved artifacts.

A cron-launched local subagent may perform bounded local work that WebGPT requests, but it is an execution surface behind the `$ask webgpt` collaboration path, not a replacement planning authority.

The first benchmark fixture is the Monocle Man single-page website. Improving that site is not the whole project; it is the test case for proving the larger loop:

1. bootstrap project context from this repository;
2. select and load the smallest useful skill chain;
3. inspect the target website source at an exact commit;
4. establish a tested and screenshot-backed baseline;
5. implement a small, coherent ChatGPT-authored change;
6. run deterministic checks in GitHub Actions;
7. return CI logs and artifacts to ChatGPT as evidence;
8. deploy the tested revision;
9. inspect the rendered site at desktop and mobile sizes;
10. use `$ask webgpt` and any cron-launched local subagent only through explicit artifact-backed delegation; and
11. write an iteration artifact that records what happened.

## ChatGPT Project Shape

The repository mirrors the two main information areas in a ChatGPT Web project:

- `chats/`: exported or summarized project conversations. These explain intent, decisions, and historical context, but they are not execution proof.
- `sources/`: guidance for the canonical project sources ChatGPT should load.

Supporting directories:

- `sources/PROJECT_INSTRUCTIONS.md`: stable instructions to load this repository as the project source.
- `sources/SOURCE_INDEX.md`: source index and bootstrap order.
- `sources/source-manifest.json`: machine-readable source and capability manifest.
- `sources/control-plane/`: operating contract, current state, review rubric, decisions, and migration notes.
- `docs/requirements/`: requirements for the self-improvement loop.
- `docs/research/`: non-canonical background material and research notes.
- `iterations/`: future per-run iteration records.
- `artifacts/`: validation receipts, screenshots, CI outputs, and other evidence artifacts.
- `artifacts/package/`: local package manifest, checksum file, and local validation receipt.
- `schemas/`: machine-readable schemas.
- `scripts/`: local validation and maintenance scripts.

## Important Files

Start every new ChatGPT Web session by reading:

1. `sources/SOURCE_INDEX.md`
2. `sources/source-manifest.json`
3. `sources/control-plane/OPERATING_CONTRACT.md`
4. `sources/control-plane/CURRENT_STATE.md`
5. `sources/control-plane/REVIEW_RUBRIC.md`
6. `sources/control-plane/DECISIONS.md`
7. `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`
8. `sources/README.md`
9. relevant files under `chats/`

Other key paths:

- `sources/PROJECT_INSTRUCTIONS.md`: stable instructions to load this repository as the project source.
- `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`: requirements for proving the ChatGPT self-improvement loop.
- `sources/control-plane/`: detailed control-plane policy and state.
- `schemas/iteration.schema.json`: expected shape of iteration evidence records.
- `scripts/validate_control_plane.py`: local and CI validation for the control-plane files.
- `artifacts/package/`: package integrity and local validation evidence.
- `.github/workflows/source-check.yml`: GitHub Actions workflow for repository validation.
- `chats/monocle-man-website-creation.md`: initial exported project chat.

## Repository Role

This repository is the ChatGPT Web-accessible control plane. It is not just documentation and it is not the benchmark website source.

It owns:

- requirements for the self-improvement loop;
- project instructions for future ChatGPT sessions;
- the operating contract for the improvement loop;
- the current readiness and blocker state;
- source precedence rules;
- review and gate criteria;
- schemas for iteration records;
- validation scripts;
- local and CI validation receipts;
- exported chat context;
- historical decisions and migration notes.

The benchmark website source currently lives separately in `grahama1970/snippets`, branch `preview-monocle-man-netlify`, under `monocle-man-site/`.

## Evidence Standard

This project treats claims as unproven until backed by concrete artifacts.

The evidence hierarchy is:

1. GitHub source and commit SHA for what code exists.
2. GitHub Actions logs and artifacts for what executed.
3. Netlify deployment metadata for what is live.
4. Fresh screenshots and interaction results for what users can see and do.
5. `$ask` / WebGPT / local-subagent artifacts for bounded advisory collaboration.
6. Independent review findings for judgment and fix prioritization.
7. Exported chats and conversation memory as context only, never proof.

Missing CI, deployment, screenshot, or interaction evidence should be recorded as `INSUFFICIENT_EVIDENCE`, not treated as success.

## Current Status

The repository is active as a control plane, but the full self-improvement loop is not yet established.

Immediate milestones are:

1. refine and accept `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`;
2. establish benchmark CI for tests, accessibility, console checks, and screenshots;
3. prove ChatGPT-authored benchmark changes can be committed and tested;
4. connect a deployment path to Netlify;
5. prove deployments map to exact tested commits;
6. prove `$ask` / WebGPT plan or review collaboration with preserved artifacts;
7. define any WebGPT-to-local-subagent bridge requirements before implementation; and
8. write the first complete iteration record.

## Validation

Run the local control-plane check with:

```bash
python3 scripts/validate_control_plane.py
```

For packaged files, verify checksums with:

```bash
sha256sum -c artifacts/package/SHA256SUMS.txt
```

These checks confirm repository structure and file integrity. They do not prove the benchmark website, CI loop, Netlify deployment, or visual review workflow.
