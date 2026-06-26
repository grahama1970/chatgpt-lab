# ChatGPT-Lab Self-Improvement Requirements

**Status:** Draft v0.2
**Updated:** 2026-06-25
**Purpose:** Define the minimum requirements for proving that ChatGPT Web can build and improve software projects without requiring a separate code agent as the default implementer.

## Goal

ChatGPT-Lab must prove a repeatable loop where ChatGPT Web can:

1. load durable project context from GitHub;
2. make code and control-plane changes directly;
3. run GitHub CI against those changes;
4. receive machine-readable CI, deployment, screenshot, and review evidence;
5. inspect rendered behavior through screenshots and browser interaction;
6. use WebGPT and local subagents only as optional collaborators; and
7. record each iteration so the next ChatGPT session can continue from evidence rather than memory.

The benchmark target is the Monocle Man SPA. The larger product is the self-improvement loop, not that website.

## Slice 001 Scope

Do not ask WebGPT to design the whole autonomous loop first. The first
implementation request is **Slice 001: a narrow, implementation-ready
GitHub/CI/WebGPT evidence loop for the Monocle Man SPA**, plus schemas and stubs
that make future local-subagent delegation safe.

Slice 001 proves only this vertical path:

1. target repo: `grahama1970/chatgpt-lab`;
2. target branch: `main`;
3. target path: `monocle-man-site/`;
4. benchmark CI builds or statically serves the site;
5. Playwright smoke test runs;
6. desktop screenshot is captured;
7. mobile screenshot is captured;
8. console errors are captured;
9. accessibility report is captured;
10. interaction result JSON is captured;
11. final `verdict.json` is emitted;
12. one tiny visible ChatGPT-authored website change is tested;
13. GitHub Actions runs on the exact candidate commit;
14. evidence artifacts are uploaded and referenced from ChatGPT-Lab; and
15. one iteration record is written under `iterations/`.

Slice 001 must not implement a full live local-subagent bridge. It may add the
task-request schema, receipt schema, refusal rules, and one dry-run/read-only
example. Live WebGPT-to-local-subagent execution remains `NOT_ESTABLISHED` until
a later slice proves transport, identity, authorization, and receipts.

## Benchmark Evidence Bundle

The first benchmark workflow must upload an artifact with this minimum layout:

```text
benchmark-evidence/
  run-metadata.json
  source-metadata.json
  test-results.json
  console-errors.json
  network-errors.json
  accessibility.json
  interactions.json
  screenshots/
    desktop.png
    mobile.png
  deployment-metadata.json
  artifact-manifest.json
  verdict.json
```

`deployment-metadata.json` may be nullable until Netlify deployment proof exists.
Any live-site claim still requires deployment metadata that maps the live URL to
the exact tested commit.

`run-metadata.json` must include:

```json
{
  "schema": "chatgpt_lab.github_actions_run.v1",
  "repository": "grahama1970/chatgpt-lab",
  "workflow": "monocle-man-benchmark",
  "run_id": null,
  "run_attempt": null,
  "head_sha": null,
  "branch": "main",
  "artifact_name": "monocle-man-benchmark-evidence",
  "generated_at": null
}
```

The critical invariant is: workflow `head_sha` must equal the candidate commit.
A passing GitHub Actions status without that equality is `INSUFFICIENT_EVIDENCE`.

## Iteration File Layout

Slice 001 iteration records should use this layout:

```text
iterations/
  2026-06-25-slice-001-monocle-man/
    iteration.json
    status.json
    loaded-sources.json
    selected-skills.json
    candidate.json
    evidence/
      github-actions-run.json
      benchmark-artifact-manifest.json
      deployment-proof.json
      screenshot-index.json
    reviews/
      code-review.json
      visual-review.json
      webgpt-review.json
    webgpt/
      ask-run-reference.json
      request.md
      response.parsed.json
    subagents/
      requests/
      receipts/
```

`status.json` is the fast-readable state file:

```json
{
  "schema": "chatgpt_lab.iteration_status.v1",
  "iteration_id": "2026-06-25-slice-001-monocle-man",
  "state": "INSUFFICIENT_EVIDENCE",
  "phase": "benchmark-ci",
  "candidate_commit": null,
  "required_next_evidence": [
    "github_actions_run_matching_candidate_commit",
    "desktop_screenshot",
    "mobile_screenshot",
    "verdict_json"
  ],
  "blockers": [],
  "updated_at": "2026-06-25T00:00:00-04:00"
}
```

## Local Subagent Request Contract

WebGPT must never emit free-form instructions such as "run whatever is needed
locally." Local work requests must be structured JSON and validated before any
cron-launched local subagent acts.

Minimum request shape:

```json
{
  "schema": "chatgpt_lab.webgpt_local_task_request.v1",
  "task_id": "webgpt-local-20260625-001",
  "requested_by": "webgpt",
  "objective": "Run read-only validation for the benchmark evidence bundle.",
  "mode": "read_only",
  "target": {
    "repository": "grahama1970/chatgpt-lab",
    "branch": "main",
    "path": "monocle-man-site/",
    "commit": null
  },
  "allowed_commands": [
    "npm ci",
    "npm run build",
    "npx playwright test"
  ],
  "allowed_paths": [
    "monocle-man-site/**",
    "artifacts/**"
  ],
  "forbidden_paths": [
    "~/.ssh/**",
    ".env",
    "**/.env",
    "**/secrets/**"
  ],
  "timeout_seconds": 600,
  "network_policy": "default_ci_only",
  "write_policy": "artifacts_only",
  "required_outputs": [
    "subagent-receipt.json",
    "stdout.txt",
    "stderr.txt",
    "artifact-manifest.json"
  ],
  "refusal_conditions": [
    "target_commit_missing",
    "command_not_allowlisted",
    "path_outside_allowlist",
    "secrets_requested",
    "timeout_exceeded"
  ]
}
```

Invalid requests produce receipts, not silent skips. Minimum refusal receipt:

```json
{
  "schema": "chatgpt_lab.local_subagent_receipt.v1",
  "task_id": "webgpt-local-20260625-001",
  "status": "REFUSED",
  "reason": "target_commit_missing",
  "commands_run": [],
  "files_touched": [],
  "artifacts": [],
  "started_at": null,
  "completed_at": null
}
```

## Collaboration Control-Plane Surfaces

There are two primary collaboration surfaces:

1. **GitHub repository control plane:** durable source, requirements, state, decisions, schemas, CI workflows, evidence artifacts, and iteration records.
2. **`$ask webgpt` control plane:** browser-backed planning, review, oracle, and task-collaboration surface with preserved request/status/event/output artifacts.

The cron-launched local subagent is not a third planning authority. It is a bounded local execution surface for structured tasks that WebGPT requests through the `$ask webgpt` collaboration path and that the project agent can audit through artifacts.

## Actors

| Actor | Role | Requirement boundary |
|---|---|---|
| ChatGPT Web | Primary product-building agent | Must be able to understand requirements, propose changes, inspect evidence, and decide the next bounded iteration. |
| ChatGPT-Lab project agent | Local/control-plane operator | May edit repos, run local checks, operate the GitHub and `$ask webgpt` collaboration surfaces, and preserve evidence. |
| GitHub | Repository control-plane surface | Stores requirements, state, decisions, source, CI workflows, logs, artifacts, and iteration records. |
| Netlify | Deployment authority | Hosts reviewed builds and exposes deployment metadata tied to commits. |
| WebGPT via `$ask` | Browser-backed collaboration control-plane surface | May plan, review, ask clarifying questions, or request bounded local subagent work, but cannot replace deterministic proof. |
| Cron-launched local subagent | Bounded local execution surface | Watches or receives approved WebGPT task requests, performs bounded local work, and returns artifacts. |

## Capability Requirements

| ID | Requirement | Evidence artifact | Current state |
|---|---|---|---|
| REQ-CAP-001 | ChatGPT-Lab must keep project instructions, requirements, schemas, state, decisions, and iteration evidence in a GitHub repository ChatGPT can reload. | `sources/SOURCE_INDEX.md`, `sources/source-manifest.json`, GitHub repo metadata. | `READY` for control plane. |
| REQ-CAP-002 | ChatGPT or the project agent must be able to create and update the control-plane repository directly. | Git commit SHA, `git ls-remote`, GitHub repo view JSON. | `READY`; proven for `grahama1970/chatgpt-lab`. |
| REQ-CAP-003 | ChatGPT or the project agent must be able to change the benchmark source repository directly or through a branch/PR. | Target repo commit, PR metadata, branch ref. | `NOT_ESTABLISHED`. |
| REQ-CAP-004 | GitHub CI must run on every relevant control-plane push, including evidence-only changes when those changes affect project truth. | GitHub Actions run JSON with matching head SHA. | `READY` for control-plane source check. |
| REQ-CAP-005 | Benchmark CI must test ChatGPT-authored code changes with build, unit/smoke, browser, accessibility, console, and screenshot checks. | CI artifacts: build logs, test results, accessibility report, console report, desktop/mobile screenshots, verdict JSON. | `NOT_ESTABLISHED`. |
| REQ-CAP-006 | CI results must be retrievable by ChatGPT as structured evidence, not only as prose. | Downloaded run metadata, logs, artifacts, and normalized iteration evidence. | `PARTIAL`; control-plane runs are retrievable. |
| REQ-CAP-007 | ChatGPT must be able to inspect rendered output through fresh screenshots and browser interactions from the same tested commit. | Screenshot files, browser trace, interaction result JSON, commit/deploy mapping. | `NOT_ESTABLISHED` for benchmark. |
| REQ-CAP-008 | The project agent must be able to use `$ask webgpt` to perform bounded planning, review, oracle, and task-collaboration workflows. | `$ask` run directory containing request, status, events, raw response, parsed output, and any mode-specific artifacts. | `NEEDS_ATTENTION`; plan-collab preflight is currently blocked by duplicate ChatGPT tabs. |
| REQ-CAP-009 | WebGPT must be able to request bounded local work that is performed by a cron-launched local subagent, not by ad hoc manual interpretation. | WebGPT task request artifact, cron pickup receipt, subagent execution receipt, response artifact, identity/auth proof. | `NOT_ESTABLISHED`. |
| REQ-CAP-010 | The WebGPT-to-local-subagent bridge must be fail-closed and reachable through a controlled path such as Tailscale when remote transport is needed. | Tailscale identity, endpoint health proof, task transcript, auth decision, rollback/safety policy. | `NOT_ESTABLISHED`. |
| REQ-CAP-011 | The cron-launched subagent must have a narrow task contract and must not execute arbitrary WebGPT prose. | Task schema, allowlist, timeout, workspace boundary, command log, and refusal receipt for invalid tasks. | `NOT_ESTABLISHED`. |

## Evidence Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-EVD-001 | Every implementation claim must state whether it is based on mocked or live evidence. | Reports include `mocked: yes/no`, `live: yes/no`, exercised commands, and unverified scope. |
| REQ-EVD-002 | A passing GitHub Actions status is not enough by itself; the run must match the target commit. | `headSha` equals the candidate commit. |
| REQ-EVD-003 | Rendered UI claims require screenshot or browser evidence, not DOM existence alone. | Fresh desktop/mobile screenshots and interaction traces are stored or linked. |
| REQ-EVD-004 | WebGPT review is reviewer evidence, not closure proof. | Local deterministic checks still pass after reconciling WebGPT output. |
| REQ-EVD-005 | Each iteration must produce a machine-readable record. | A file under `iterations/` validates against `schemas/iteration.schema.json`. |
| REQ-EVD-006 | Each deployment claim must map a live URL to an exact tested commit. | Netlify deployment metadata includes commit/ref and matches CI evidence. |

## Workflow Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-WFL-001 | Each run starts by loading control-plane context from `sources/SOURCE_INDEX.md`. | Iteration record names the loaded control-plane ref. |
| REQ-WFL-002 | Collaboration state must flow through GitHub repo artifacts or `$ask webgpt` artifacts, not hidden chat memory. | Iteration record references GitHub commits/artifacts and ask run artifacts. |
| REQ-WFL-003 | Each run refreshes the skill registry before selecting skills. | Iteration record captures registry ref/hash and selected skills. |
| REQ-WFL-004 | Each implementation round is bounded. | Round has at most five prioritized fixes and an explicit stop condition. |
| REQ-WFL-005 | Builder, reviewer, and gate roles remain logically separate even when one model performs multiple roles. | Iteration record separates implementation notes, review findings, and verdict. |
| REQ-WFL-006 | Failed or insufficient evidence stops the loop before new complexity is added. | State changes to `INSUFFICIENT_EVIDENCE`, `NEEDS_ATTENTION`, or `BLOCKED`. |
| REQ-WFL-007 | Requirements changes must update this file before implementation changes broaden the system. | Requirements diff precedes implementation diff for new capabilities. |

## WebGPT And Local Subagent Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-WEB-001 | The project agent must use the executable `$ask` runtime for WebGPT work, not an informal browser prompt or hand-written substitute. | Ask artifacts are preserved outside Git and referenced in the iteration record. |
| REQ-WEB-002 | `$ask webgpt-plan-collab` may be used to improve plans, but its output is advisory. | Ask artifacts include request, status, events, raw response, and plan-collab output. |
| REQ-WEB-003 | `$ask webgpt-review` may review code, plans, or phase gates only from a concrete bundle. | Bundle includes objective, files, commands, evidence, questions, and acceptance gates. |
| REQ-WEB-004 | WebGPT cannot inspect bare local paths unless file contents or served URLs are supplied. | Bundle contains the relevant content or URL. |
| REQ-WEB-005 | If WebGPT wants local work, it must emit a structured task request for the cron-launched subagent. | Request includes task id, objective, allowed files, allowed commands, timeout, required artifacts, and refusal conditions. |
| REQ-WEB-006 | The cron-launched subagent must execute only validated tasks and must produce a response artifact for WebGPT and the project agent. | Response includes status, commands run, files touched, artifacts produced, errors, and remaining blockers. |
| REQ-WEB-007 | Local subagent output must not be treated as proof unless it includes raw command results or artifacts. | Subagent receipt includes commands, paths, hashes, screenshots, logs, or test output. |
| REQ-WEB-008 | PR/issue work handed to a local subagent must be implementation-ready before execution. | The target contains a `chatgpt_lab.pr_local_task.v1` block with allowed commands, paths, validation commands, expected evidence, required outputs, stop condition, and refusal conditions. |
| REQ-WEB-009 | Under-specified PR/issue work must be refused, not inferred. | The local worker writes a `chatgpt_lab.local_subagent_receipt.v1` receipt with `status: REFUSED`, `reason`, `missing`, and `next_required_action`. |
| REQ-WEB-010 | The MVP cron loop must separate coder, reviewer, and optional researcher roles. | `agent-skills/agents/phatgpt-coder`, `phatgpt-reviewer`, and `phatgpt-researcher` contracts exist; each invocation handles at most one PR/issue and writes a receipt. |
| REQ-WEB-011 | The coder role is the only local role allowed to mutate code. | Coder contract allows scoped mutation only after a valid task block; reviewer and researcher contracts deny code mutation, commit, push, and merge. |
| REQ-WEB-012 | The reviewer role must be read-only and must return `PASS`, `NEEDS_CHANGES`, or `BLOCKED` style output without patching. | Reviewer contract denies write access and emits review receipt/findings/next owner. |
| REQ-WEB-013 | Reviewer `NEEDS_CHANGES` output must become the next coder target instead of triggering reviewer mutation. | PR labels/comments route findings back to the coder queue; the coder may retry only within the bounded retry budget. |

## Trust Boundary Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-TRU-001 | Source truth comes from GitHub file content at a specific commit. | Candidate commit is recorded. |
| REQ-TRU-002 | Execution truth comes from GitHub Actions or explicit local command artifacts. | Run ID or local transcript is recorded. |
| REQ-TRU-003 | Deployment truth comes from Netlify metadata. | Deployment ID and commit mapping are recorded. |
| REQ-TRU-004 | Rendered truth comes from fresh screenshots and browser interaction evidence. | Screenshot/trace artifact names include commit or deployment ID. |
| REQ-TRU-005 | Model judgment is advisory unless backed by deterministic evidence. | Review verdict references raw proof artifacts. |

## First Acceptance Milestone

`USABLE_WITH_GAPS` requires:

1. control-plane source-check workflow passes on the current `main`;
2. benchmark CI exists and uploads required artifacts;
3. ChatGPT-authored benchmark change is committed and tested;
4. screenshots are captured from the tested revision;
5. Netlify deployment maps to the tested commit;
6. WebGPT review can be invoked through `$ask` with preserved artifacts;
7. one complete iteration record validates against schema; and
8. unsupported success claims are absent.

## Resolved Slice 001 Decisions

1. The first slice is Monocle Man CI plus screenshot evidence plus one tiny
   visible ChatGPT-authored benchmark change plus one iteration record.
2. ChatGPT-Lab owns contracts, schemas, iteration records, source references, and
   evidence references.
3. `grahama1970/chatgpt-lab@main:monocle-man-site/` owns
   the benchmark source, benchmark workflow, Playwright smoke, screenshot
   capture, and generated benchmark artifacts.
4. `$ask webgpt` owns WebGPT orchestration artifacts. `$surf` owns browser
   transport proof when the lower layer is used directly.
5. Local subagent work is allowed only through versioned JSON task requests with
   allowlisted commands, path bounds, timeouts, required outputs, and
   receipt-backed refusal.
6. Missing CI, screenshots, deployment metadata, WebGPT artifacts, or local
   receipts fail closed as `INSUFFICIENT_EVIDENCE`, `NEEDS_ATTENTION`, or
   `BLOCKED`; they never imply success.

## Remaining Open Questions

1. Which exact ChatGPT conversation URL or browser-oracle project binding should
   be canonical for `$ask webgpt` work on ChatGPT-Lab?
2. Should Slice 001 land directly on `main`, or through a
   branch plus pull request before merge?
3. What is the first tiny visible Monocle Man change ChatGPT should make once
   benchmark CI exists?

## Parking Lot

- Live Tailscale/WebGPT/cron-subagent bridge execution.
- Bounded loop controller implementation.
- Netlify deployment proof collector.
- Artifact ingestion back into ChatGPT Project context without manual upload.
