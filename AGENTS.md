# AGENTS.md

This repository is the versioned control plane for ChatGPT-Lab. It is not the
Monocle Man website itself.

## Mandatory bootstrap

Before planning, implementing, reviewing, or claiming status:

1. Read `sources/SOURCE_INDEX.md`.
2. Read `sources/source-manifest.json`,
   `sources/control-plane/OPERATING_CONTRACT.md`, and
   `sources/control-plane/CURRENT_STATE.md`.
3. Refresh the live registry in `grahama1970/agent-skills`.
4. Select the smallest relevant skill chain and record it in the iteration
   receipt.
5. Inspect the benchmark at the exact branch and commit recorded in the source
   manifest.
6. Treat missing or stale CI, deployment, screenshot, or interaction evidence as
   `INSUFFICIENT_EVIDENCE`.

## Role discipline

- Builder phase may edit code, tests, workflows, and iteration artifacts.
- Reviewer phase is read-only until findings are finalized.
- Gate phase distinguishes deterministic facts, visual judgment, and human
  preference.
- Never use the builder's rationale as proof that the implementation works.

## Required evidence for website claims

- Git commit SHA
- GitHub Actions run and job results
- deployment URL and revision identity
- current desktop and mobile screenshots
- deterministic interaction results
- code-review findings
- design-review findings
- verdict and stop reason

## Allowed verdicts

`PASS`, `NEEDS_CHANGES`, `BLOCKED`, `INSUFFICIENT_EVIDENCE`

## Default limits

- maximum improvement rounds: 3
- maximum prioritized fixes per round: 5
- required viewport classes: desktop and mobile
- quantitative performance thresholds: not established until measured and
  explicitly accepted

Do not invent test results, deployment state, metrics, screenshots, transcript
content, or completed background work.
