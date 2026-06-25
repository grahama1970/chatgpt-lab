# ChatGPT-Lab Self-Improvement Requirements

**Status:** Draft v0.2  
**Updated:** 2026-06-25  
**Purpose:** Define the minimum requirements for proving that ChatGPT Web can control, build, verify, and improve software projects without requiring a separate code agent as the default implementer.

## Goal

ChatGPT-Lab must prove a repeatable loop where ChatGPT Web can:

1. load durable project context from GitHub;
2. make requirements, code, workflow, and control-plane changes directly;
3. create isolated branches and pull requests in the target repository;
4. run GitHub CI against those changes;
5. retrieve machine-readable CI, deployment, screenshot, and review evidence;
6. inspect rendered behavior through screenshots and browser interaction;
7. decide the next bounded iteration from evidence;
8. use the project agent, WebGPT collaboration, and local subagents only as optional bounded execution or review surfaces; and
9. record each iteration so the next ChatGPT session can continue from evidence rather than memory.

The benchmark target is the Monocle Man SPA. The larger product is the self-improvement loop, not that website.

## Authority Model

ChatGPT Web is the **primary controller and default implementer** for ChatGPT-Lab.

ChatGPT Web owns:

- interpretation and amendment of requirements;
- selection of the next bounded objective;
- skill selection and dependency loading;
- source changes made through GitHub branches and pull requests;
- retrieval and inspection of CI and deployment evidence;
- rendered design review;
- reconciliation of reviewer findings;
- the final gate verdict; and
- the decision to merge, retry, stop, or delegate a bounded task.

The ChatGPT-Lab project agent is a **delegated local execution adapter**, not a co-equal planning authority and not the default author of the next round. It may operate local-only capabilities that ChatGPT Web cannot access directly, including local CLIs, authenticated browser transport, `$ask webgpt`, private services, cron, or workstation files. Its work must be requested through a bounded contract and returned as artifacts.

The project agent must not independently:

- broaden requirements;
- select a new project objective;
- add architecture outside the approved round;
- merge or promote a candidate;
- declare the design or system complete; or
- treat its own prose as proof.

A separate coding agent or local subagent is optional. When used, it is a worker beneath the ChatGPT-controlled builder/reviewer/gate loop.

## Default Repository Write Path

The default implementation path is:

```text
ChatGPT Web
  -> create or update an isolated GitHub branch
  -> open a pull request
  -> run GitHub Actions for the exact head SHA
  -> retrieve logs and artifacts
  -> inspect rendered evidence
  -> patch, merge, or stop
```

A project-agent-mediated commit is permitted only when the required operation is unavailable through the ChatGPT GitHub connection or depends on local-only state. The iteration record must identify the delegate, task contract, files touched, commands run, and returned artifacts.

## Collaboration Control-Plane Surfaces

There are two collaboration surfaces, but only one primary authority:

1. **GitHub repository control plane:** canonical durable source, requirements, state, decisions, schemas, CI workflows, evidence artifacts, and iteration records.
2. **`$ask webgpt` collaboration surface:** optional browser-backed planning, review, oracle, and task-collaboration transport with preserved request/status/event/output artifacts.

`$ask webgpt` is not required when the active ChatGPT Web session already has the necessary repository, CI, browser, and deployment access. It is advisory when used and cannot replace deterministic proof or the ChatGPT gate decision.

The cron-launched local subagent is not a planning authority. It is a bounded local execution surface for validated structured tasks explicitly delegated by ChatGPT Web or carried through the approved `$ask webgpt` path.

## Actors

| Actor | Role | Requirement boundary |
|---|---|---|
| ChatGPT Web | Primary controller and default implementer | Owns requirements, bounded objectives, GitHub changes, evidence review, gate verdicts, and next-round decisions. |
| ChatGPT-Lab project agent | Delegated local/control-plane operator | Performs explicitly bounded local-only work, preserves raw evidence, and returns results without broadening scope or self-approving. |
| GitHub | Source and execution control-plane surface | Stores requirements, state, decisions, source, CI workflows, logs, artifacts, branches, pull requests, and iteration records. |
| Netlify | Deployment authority | Hosts reviewed builds and exposes deployment metadata tied to commits. |
| WebGPT via `$ask` | Optional browser-backed collaborator | May plan, review, or request bounded local work, but is advisory and cannot replace deterministic proof or the controlling ChatGPT decision. |
| Cron-launched local subagent | Optional bounded execution worker | Executes only validated structured tasks within an allowlisted workspace and returns command/artifact receipts. |

## Capability Requirements

| ID | Requirement | Evidence artifact | Current state |
|---|---|---|---|
| REQ-CAP-001 | ChatGPT-Lab must keep project instructions, requirements, schemas, state, decisions, and iteration evidence in a GitHub repository ChatGPT can reload. | `sources/SOURCE_INDEX.md`, `sources/source-manifest.json`, GitHub repo metadata. | `READY` for control plane. |
| REQ-CAP-002 | ChatGPT Web must be able to create and update the control-plane repository directly. | Git commit SHA, branch ref, pull request metadata, GitHub repository view. | `READY`; proven for `grahama1970/chatgpt-lab`. |
| REQ-CAP-003 | ChatGPT Web must be able to change the benchmark source through an isolated branch and pull request as the default path. Project-agent-mediated changes are fallback only. | Target repo commit, PR metadata, head ref, author/delegate record. | `NOT_ESTABLISHED`. |
| REQ-CAP-004 | GitHub CI must run on every relevant control-plane push or pull request, including evidence-only changes when they affect project truth. | GitHub Actions run JSON with matching head SHA. | `READY` for control-plane source check. |
| REQ-CAP-005 | Benchmark CI must test ChatGPT-authored code changes with build, unit/smoke, browser, accessibility, console, and screenshot checks. | CI artifacts: build logs, test results, accessibility report, console report, desktop/mobile screenshots, verdict JSON. | `NOT_ESTABLISHED`. |
| REQ-CAP-006 | CI results must be retrievable by ChatGPT as structured evidence, not only as prose. | Downloaded run metadata, logs, artifacts, and normalized iteration evidence. | `PARTIAL`; control-plane runs are retrievable. |
| REQ-CAP-007 | ChatGPT must be able to inspect rendered output through fresh screenshots and browser interactions from the same tested commit. | Screenshot files, browser trace, interaction result JSON, commit/deploy mapping. | `NOT_ESTABLISHED` for benchmark. |
| REQ-CAP-008 | The project agent may use `$ask webgpt` for bounded planning, review, oracle, and collaboration when ChatGPT selects that path. | `$ask` run directory containing request, status, events, raw response, parsed output, and mode-specific artifacts. | `NEEDS_ATTENTION`; optional path currently affected by duplicate ChatGPT tabs. |
| REQ-CAP-009 | ChatGPT or approved WebGPT collaboration may request bounded local work through a structured task artifact consumed by a local subagent. | Task request, pickup receipt, execution receipt, response artifact, identity/auth proof. | `NOT_ESTABLISHED`; optional future capability. |
| REQ-CAP-010 | Any remote WebGPT-to-local-subagent bridge must be fail-closed and reachable only through a controlled authenticated path such as Tailscale. | Identity, endpoint health proof, task transcript, auth decision, rollback/safety policy. | `NOT_ESTABLISHED`; optional future capability. |
| REQ-CAP-011 | A local subagent must have a narrow task contract and must not execute arbitrary prose. | Task schema, allowlist, timeout, workspace boundary, command log, and refusal receipt for invalid tasks. | `NOT_ESTABLISHED`; required before any local subagent is enabled. |
| REQ-CAP-012 | ChatGPT Web retains authority for the next-round objective, acceptance gate, merge decision, and final verdict even when work is delegated. | Iteration record identifies controller, delegates, findings, evidence, and gate decision. | `READY` as policy; benchmark proof pending. |

## Evidence Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-EVD-001 | Every implementation claim must state whether it is based on mocked or live evidence. | Reports include `mocked: yes/no`, `live: yes/no`, exercised commands, and unverified scope. |
| REQ-EVD-002 | A passing GitHub Actions status is not enough by itself; the run must match the target commit. | `headSha` equals the candidate commit. |
| REQ-EVD-003 | Rendered UI claims require screenshot or browser evidence, not DOM existence alone. | Fresh desktop/mobile screenshots and interaction traces are stored or linked. |
| REQ-EVD-004 | Model or WebGPT review is reviewer evidence, not closure proof. | Deterministic checks still pass after reconciling review output. |
| REQ-EVD-005 | Each iteration must produce a machine-readable record. | A file under `iterations/` validates against `schemas/iteration.schema.json`. |
| REQ-EVD-006 | Each deployment claim must map a live URL to an exact tested commit. | Netlify deployment metadata includes commit/ref and matches CI evidence. |
| REQ-EVD-007 | Delegated work must preserve raw execution evidence and controller identity. | Iteration record links the task contract, command transcript, artifacts, delegate, and ChatGPT gate decision. |

## Workflow Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-WFL-001 | Each run starts by loading control-plane context from `sources/SOURCE_INDEX.md`. | Iteration record names the loaded control-plane ref. |
| REQ-WFL-002 | Collaboration state must flow through GitHub artifacts or approved `$ask webgpt` artifacts, not hidden chat memory. | Iteration record references commits, CI artifacts, and any ask-run artifacts used. |
| REQ-WFL-003 | Each run refreshes the skill registry before selecting skills. | Iteration record captures registry ref/hash and selected skills. |
| REQ-WFL-004 | Each implementation round is bounded. | Round has at most five prioritized fixes and an explicit stop condition. |
| REQ-WFL-005 | Builder, reviewer, and gate roles remain logically separate even when one model performs multiple roles. | Iteration record separates implementation notes, review findings, and verdict. |
| REQ-WFL-006 | Failed or insufficient evidence stops the loop before new complexity is added. | State changes to `INSUFFICIENT_EVIDENCE`, `NEEDS_ATTENTION`, or `BLOCKED`. |
| REQ-WFL-007 | Requirements changes must update this file before implementation changes broaden the system. | Requirements diff precedes implementation diff for new capabilities. |
| REQ-WFL-008 | ChatGPT Web uses a direct branch-and-PR write path by default. | Candidate PR and commit are created through the ChatGPT-controlled GitHub path, or the iteration record explains why a delegate was required. |
| REQ-WFL-009 | Delegation is explicit, bounded, and reversible. | Task contract defines objective, allowed files, allowed commands, timeout, required artifacts, refusal conditions, and rollback. |
| REQ-WFL-010 | The controlling ChatGPT decides whether reviewer findings are valid and whether another round is warranted. | Gate record distinguishes accepted findings, rejected findings, human decisions, and next action. |

## WebGPT And Local Subagent Requirements

These requirements apply only when ChatGPT selects an optional collaboration or local-execution path.

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-WEB-001 | The project agent uses the executable `$ask` runtime for selected WebGPT work, not an informal browser prompt or hand-written substitute. | Ask artifacts are preserved outside Git and referenced in the iteration record. |
| REQ-WEB-002 | `$ask webgpt-plan-collab` may improve plans, but its output is advisory. | Ask artifacts include request, status, events, raw response, and plan-collab output. |
| REQ-WEB-003 | `$ask webgpt-review` may review code, plans, or phase gates only from a concrete bundle. | Bundle includes objective, files, commands, evidence, questions, and acceptance gates. |
| REQ-WEB-004 | WebGPT cannot inspect bare local paths unless file contents or served URLs are supplied. | Bundle contains the relevant content or URL. |
| REQ-WEB-005 | If ChatGPT or WebGPT requests local work, it emits a structured task request for the local subagent. | Request includes task id, objective, allowed files, allowed commands, timeout, required artifacts, and refusal conditions. |
| REQ-WEB-006 | The local subagent executes only validated tasks and produces a response artifact for ChatGPT and the project agent. | Response includes status, commands run, files touched, artifacts produced, errors, and remaining blockers. |
| REQ-WEB-007 | Local subagent output is not proof unless it includes raw command results or artifacts. | Receipt includes commands, paths, hashes, screenshots, logs, or test output. |
| REQ-WEB-008 | Optional collaboration cannot take ownership of the next round or final gate. | The iteration record names ChatGPT Web as controller and records the delegate as advisory or execution-only. |

## Trust Boundary Requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| REQ-TRU-001 | Source truth comes from GitHub file content at a specific commit. | Candidate commit is recorded. |
| REQ-TRU-002 | Execution truth comes from GitHub Actions or explicit local command artifacts. | Run ID or local transcript is recorded. |
| REQ-TRU-003 | Deployment truth comes from Netlify metadata. | Deployment ID and commit mapping are recorded. |
| REQ-TRU-004 | Rendered truth comes from fresh screenshots and browser interaction evidence. | Screenshot/trace artifact names include commit or deployment ID. |
| REQ-TRU-005 | Model judgment is advisory unless backed by deterministic evidence. | Review verdict references raw proof artifacts. |
| REQ-TRU-006 | Control authority comes from the ChatGPT-owned iteration and gate records. | Controller identity and final action are recorded independently of delegated worker output. |

## First Acceptance Milestone

`USABLE_WITH_GAPS` requires:

1. the control-plane source-check workflow passes on the current `main`;
2. ChatGPT Web creates a benchmark branch or pull request containing the CI harness or a bounded benchmark change;
3. benchmark CI uploads the required build, browser, accessibility, console, screenshot, and verdict artifacts;
4. screenshots are captured from the tested revision;
5. Netlify deployment maps to the tested commit;
6. ChatGPT retrieves and reviews CI and deployment evidence;
7. one complete iteration record validates against schema;
8. any optional `$ask webgpt` or local-subagent work used in the run has preserved task and response artifacts; and
9. unsupported success claims are absent.

The milestone does not require `$ask webgpt` or a local subagent when ChatGPT Web can complete the direct path itself.

## Resolved Decisions

1. **Repository write path:** ChatGPT Web branch plus pull request is the default. Project-agent-mediated commits are fallback only for local-only or unavailable connector operations.
2. **Canonical screenshot path:** GitHub Actions screenshot artifacts are the deterministic baseline. Local Playwright and Netlify captures are supplementary and must identify the same commit/deployment.
3. **CI evidence ingestion:** ChatGPT retrieves GitHub run metadata, logs, and artifacts through the GitHub connection, then records normalized identifiers in the iteration receipt.
4. **First benchmark engineering change:** establish the benchmark CI and screenshot harness before approving additional visual iterations.
5. **Next-round authority:** ChatGPT Web chooses and implements the next bounded round; project agents and subagents execute only explicit delegated tasks.

## Open Questions

1. What bridge protocol should be used if a future WebGPT/local-subagent path is enabled?
2. What exact schema should package screenshot, browser trace, accessibility, console, and deployment evidence into one review bundle?
3. Which ChatGPT tab should be the canonical optional `$ask webgpt` project binding once that collaboration path is repaired?
4. What is the minimum human-only product decision that should remain outside the automated gate for the Monocle Man benchmark?

## Parking Lot

- Tailscale/WebGPT/cron-subagent bridge protocol.
- Benchmark CI implementation.
- Screenshot artifact schema.
- Iteration record generator.
- Netlify deployment proof collector.
