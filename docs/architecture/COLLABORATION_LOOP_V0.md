# Collaboration Loop V0

## Purpose

Define the first implementation-ready loop that lets ChatGPT-Lab use GitHub and `$ask webgpt` as durable control-plane surfaces while keeping deterministic proof in CI artifacts.

This is V0 for Slice 001 only.

## Control surfaces

| Surface | Role | Slice 001 behavior |
|---|---|---|
| GitHub / `grahama1970/chatgpt-lab` | Durable control plane | Stores requirements, schemas, validators, iteration templates, and evidence references. |
| GitHub / `grahama1970/chatgpt-lab` | Benchmark source and CI authority | Owns the Monocle Man source files, benchmark workflow, Playwright tests, and uploaded evidence artifact. |
| `$ask webgpt` | Browser-backed collaborator | Produces request/status/events/raw/parsed artifacts for creation, planning, review, or oracle work. |
| `$surf` | Browser transport proof layer | Lower-level transport proof used by `$ask`; not called directly by normal project-agent workflows. |
| Local subagent | Future bounded execution surface | Schema/stub only in Slice 001. No live execution bridge is implemented here. |

## Slice 001 state machine

```text
BOOTSTRAP
  -> BASELINE_REQUESTED
  -> CANDIDATE_PATCHED
  -> CI_RUNNING
  -> CI_ARTIFACT_AVAILABLE
  -> ARTIFACT_VALIDATED
  -> WEBGPT_REFERENCED_OR_SKIPPED
  -> ITERATION_RECORDED
  -> STOP
```

Failure transitions:

```text
missing candidate commit          -> INSUFFICIENT_EVIDENCE
CI absent for candidate commit    -> INSUFFICIENT_EVIDENCE
CI failed with fixable issue      -> NEEDS_CHANGES
workflow/permission unavailable   -> BLOCKED
artifact missing or malformed     -> INSUFFICIENT_EVIDENCE
deployment proof missing          -> no live-site claim
invalid local-subagent request    -> REFUSED receipt
```

## Evidence hierarchy

1. GitHub source at recorded commit.
2. GitHub Actions run for that same commit.
3. Uploaded benchmark evidence artifact.
4. Fresh screenshots from the benchmark run.
5. Deployment metadata only when available and commit-mapped.
6. `$ask webgpt` artifacts as advisory collaboration evidence.
7. Conversation memory as context only.

## Candidate invariant

For any iteration that evaluates code:

```text
iteration.candidate.commit == github_actions_run.head_sha
```

If this equality cannot be proven, the iteration cannot close successfully.

## Screenshot invariant

Rendered UI claims require both:

```text
benchmark-evidence/screenshots/desktop.png
benchmark-evidence/screenshots/mobile.png
```

Each screenshot must come from the same benchmark run and candidate commit referenced by the iteration.

## Deployment invariant

A live-site claim requires:

```text
deployment-metadata.status == "PROVEN"
deployment-metadata.commit == candidate.commit
deployment-metadata.url != null
```

If deployment metadata is `NOT_ESTABLISHED`, the benchmark CI can still be useful, but the iteration cannot claim the live Netlify site reflects the tested commit.

## WebGPT artifact invariant

If WebGPT was used in a round, the iteration must reference artifacts equivalent to:

```text
request
status
events
raw_response
parsed_response
```

A prose summary without those artifacts is not WebGPT evidence.

## Local subagent invariant

Slice 001 allows only schemas and examples. A later bridge must refuse any request that is not a valid `chatgpt_lab.webgpt_local_task_request.v1`.

The refusal itself must be a valid `chatgpt_lab.local_subagent_receipt.v1`.
