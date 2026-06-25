# ChatGPT-Lab

ChatGPT-Lab is a GitHub-backed control plane for a ChatGPT Web project.

The practical goal is to keep the project instructions, operating contract, current state, schemas, scripts, evidence records, exported chats, and iteration history in a repository that ChatGPT Web can read during future sessions. ChatGPT Project Sources are not currently writable from this environment, so this repository becomes the external source of truth that can be updated, reviewed, validated, and reloaded.

The local project directory is `chatgpt-lab`. The intended GitHub repository target is `grahama1970/chatgpt-lab`.

## Why This Exists

ChatGPT can help improve websites, but a reliable improvement loop needs more than conversation memory. It needs stable files, exact source references, deterministic checks, and evidence artifacts that survive across sessions.

This repo gives future ChatGPT Web sessions a durable project source. It records:

1. what the project is trying to build;
2. which sources are canonical;
3. which skills and repositories should be loaded;
4. which prior chats explain intent and decisions;
5. what the current blockers are;
6. what evidence is required before a result can be accepted; and
7. how each iteration should be recorded.

## Project Mission

The mission is to build a reusable, evidence-driven website self-improvement system controlled from ChatGPT Web.

The first benchmark fixture is the Monocle Man single-page website. Improving that site is not the whole project; it is the test case for proving the larger loop:

1. bootstrap project context from this repository;
2. select and load the smallest useful skill chain;
3. inspect the target website source at an exact commit;
4. establish a tested and screenshot-backed baseline;
5. implement a small, coherent change;
6. run deterministic checks in GitHub Actions;
7. deploy the tested revision;
8. inspect the rendered site at desktop and mobile sizes;
9. separate builder, reviewer, and gate decisions; and
10. write an iteration artifact that records what happened.

## ChatGPT Project Shape

The repository mirrors the two main information areas in a ChatGPT Web project:

- `chats/`: exported or summarized project conversations. These explain intent, decisions, and historical context, but they are not execution proof.
- `sources/`: guidance for the canonical project sources ChatGPT should load. The root control-plane files remain at the repository root for discoverability and validation.

Supporting directories:

- `sources/control-plane/`: operating contract, current state, review rubric, decisions, and migration notes.
- `docs/research/`: non-canonical background material and research notes.
- `iterations/`: future per-run iteration records.
- `artifacts/`: validation receipts, screenshots, CI outputs, and other evidence artifacts.
- `schemas/`: machine-readable schemas.
- `scripts/`: local validation and maintenance scripts.

## Important Files

Start every new ChatGPT Web session by reading:

1. `SOURCE_INDEX.md`
2. `source-manifest.json`
3. `sources/control-plane/OPERATING_CONTRACT.md`
4. `sources/control-plane/CURRENT_STATE.md`
5. `sources/control-plane/REVIEW_RUBRIC.md`
6. `sources/control-plane/DECISIONS.md`
7. `sources/README.md`
8. relevant files under `chats/`

Other key paths:

- `PROJECT_INSTRUCTIONS.md`: stable instructions to load this repository as the project source.
- `sources/control-plane/`: detailed control-plane policy and state.
- `schemas/iteration.schema.json`: expected shape of iteration evidence records.
- `scripts/validate_control_plane.py`: local and CI validation for the control-plane files.
- `.github/workflows/source-check.yml`: GitHub Actions workflow for repository validation.
- `chats/monocle-man-website-creation.md`: initial exported project chat.

## Repository Role

This repository is the ChatGPT Web-accessible control plane. It is not just documentation and it is not the benchmark website source.

It owns:

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
5. Independent review findings for judgment and fix prioritization.
6. Exported chats and conversation memory as context only, never proof.

Missing CI, deployment, screenshot, or interaction evidence should be recorded as `INSUFFICIENT_EVIDENCE`, not treated as success.

## Current Status

The repository is in bootstrap state. The control-plane files and validation script are present locally, but the system is not yet a closed improvement loop.

Immediate milestones are:

1. create or expose `grahama1970/chatgpt-lab`, then push this repository there;
2. confirm the source-check GitHub Actions workflow passes;
3. establish benchmark CI for tests, accessibility, console checks, and screenshots;
4. connect a deployment path to Netlify;
5. prove deployments map to exact tested commits; and
6. write the first complete iteration record.

## Validation

Run the local control-plane check with:

```bash
python3 scripts/validate_control_plane.py
```

For packaged files, verify checksums with:

```bash
sha256sum -c SHA256SUMS.txt
```

These checks confirm repository structure and file integrity. They do not prove the benchmark website, CI loop, Netlify deployment, or visual review workflow.
