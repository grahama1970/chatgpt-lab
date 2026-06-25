# ChatGPT-Lab

![ChatGPT-Lab improvement cycle: observe, reason, verify, improve](artifacts/readme/chatgpt-lab-improvement-cycle.png)

ChatGPT-Lab is a GitHub-backed control plane designed to prove that ChatGPT Web can build and improve software projects directly.

The repo stores everything ChatGPT needs to pick up where it left off: requirements, instructions, operating contracts, current state, schemas, scripts, evidence records, exported chats, and iteration history. ChatGPT Project Sources are read-only from the Web UI, so this repository acts as the external source of truth: something ChatGPT can read, and you can update, review, validate, and reload.

Local directory: `chatgpt-lab`.

GitHub target: `grahama1970/chatgpt-lab`.

## Why This Exists

ChatGPT can write code, but a reliable self-improvement loop needs more than conversation memory. It needs stable files, exact source references, deterministic checks, rendered screenshots, review artifacts, and evidence that survives across sessions.

This repo gives future ChatGPT Web sessions a durable project source. It records:

1. What the project is trying to build.
2. Which sources are canonical.
3. Which requirements must be satisfied.
4. Which skills and repositories to load.
5. Which prior chats explain intent and decisions.
6. What the current blockers are.
7. What evidence is required before accepting a result.
8. How each iteration should be recorded.

## Project Mission

The mission is to prove a reusable, evidence-driven self-improvement system controlled from ChatGPT Web.

The end goal is a loop where ChatGPT Web does not need a separate code agent by default. ChatGPT should propose changes, commit them through GitHub, let CI test them, inspect artifacts and screenshots, collaborate via `$ask webgpt`, and continue the next iteration from recorded evidence.

The working model is simple:

1. **Observe** the repository, CI results, screenshots, and prior iteration artifacts.
2. **Reason** from current requirements, source state, and unresolved blockers.
3. **Verify** changes with deterministic local checks, GitHub Actions, deployment metadata, and rendered screenshots.
4. **Improve** the project by committing the smallest evidence-backed change and recording the next iteration.

Bias: evidence over opinion. Chats, reviews, and model judgments can guide the next action, but only concrete artifacts establish what actually happened.

Two primary collaboration surfaces:

1. **The GitHub repository**: durable requirements, state, source references, workflows, and evidence.
2. **`$ask webgpt`**: browser-backed planning, review, oracle, and task-collaboration workflows with preserved artifacts.

A cron-launched local subagent may handle bounded local work that WebGPT requests, but it is an execution surface behind the `$ask webgpt` path, not a replacement planning authority.

### First Benchmark: Monocle Man

The Monocle Man single-page website is the first benchmark fixture. Improving that site is not the whole project; it is the test case for proving the larger loop:

1. Bootstrap project context from this repository.
2. Select and load the smallest useful skill chain.
3. Inspect the target website source at an exact commit.
4. Establish a tested, screenshot-backed baseline.
5. Implement a small, coherent ChatGPT-authored change.
6. Run deterministic checks in GitHub Actions.
7. Return CI logs and artifacts to ChatGPT as evidence.
8. Deploy the tested revision.
9. Inspect the rendered site at desktop and mobile sizes.
10. Use `$ask webgpt` and any cron-launched local subagent only through explicit, artifact-backed delegation.
11. Write an iteration artifact that records what happened.

## Project Shape

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
9. Relevant files under `chats/`

Other key paths:

- `sources/PROJECT_INSTRUCTIONS.md`: stable instructions to load this repository as the project source.
- `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`: requirements for proving the ChatGPT self-improvement loop.
- `sources/control-plane/`: detailed control-plane policy and state.
- `schemas/iteration.schema.json`: expected shape of iteration evidence records.
- `scripts/validate_control_plane.py`: local and CI validation for the control-plane files.
- `artifacts/package/`: package integrity and local validation evidence.
- `.github/workflows/source-check.yml`: GitHub Actions workflow for repository validation.
- `chats/monocle-man-website-creation.md`: initial exported project chat.

## What This Repository Owns

This is the ChatGPT Web-accessible control plane. It is not just documentation, and it is not the benchmark website source.

It owns:

- Requirements for the self-improvement loop.
- Project instructions for future ChatGPT sessions.
- The operating contract for the improvement loop.
- Current readiness and blocker state.
- Source precedence rules.
- Review and gate criteria.
- Schemas for iteration records.
- Validation scripts.
- Local and CI validation receipts.
- Exported chat context.
- Historical decisions and migration notes.

The benchmark website source lives separately in `grahama1970/snippets`, branch `preview-monocle-man-netlify`, under `monocle-man-site/`.

## Evidence Standard

Claims are unproven until backed by concrete artifacts.

The evidence hierarchy:

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

Immediate milestones:

1. Refine and accept `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`.
2. Establish benchmark CI for tests, accessibility, console checks, and screenshots.
3. Prove ChatGPT-authored benchmark changes can be committed and tested.
4. Connect a deployment path to Netlify.
5. Prove deployments map to exact tested commits.
6. Prove `$ask` / WebGPT plan or review collaboration with preserved artifacts.
7. Define any WebGPT-to-local-subagent bridge requirements before implementation.
8. Write the first complete iteration record.

## Validation

Run the local control-plane check:

```bash
python3 scripts/validate_control_plane.py
```

For packaged files, verify checksums:

```bash
sha256sum -c artifacts/package/SHA256SUMS.txt
```

These checks confirm repository structure and file integrity. They do not prove the benchmark website, CI loop, Netlify deployment, or visual review workflow.
