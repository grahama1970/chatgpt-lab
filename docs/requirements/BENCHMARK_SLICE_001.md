# Benchmark Slice 001 — Monocle Man Evidence Loop

## Objective

Prove a narrow end-to-end collaboration loop for the Monocle Man SPA without claiming the full autonomous self-improvement system is complete.

## In scope

- Benchmark GitHub Actions workflow in `grahama1970/snippets`.
- Playwright smoke and interaction checks.
- Console error capture.
- Network error capture.
- Accessibility report capture.
- Desktop and mobile screenshots.
- Machine-readable benchmark artifact manifest.
- Benchmark verdict JSON.
- ChatGPT-Lab validators for benchmark artifacts and iteration records.
- Local-subagent request/receipt schemas and refusal examples.
- One tiny visible website change checked by the benchmark.

## Out of scope

- Full loop controller.
- Live WebGPT-to-local-subagent bridge.
- Tailscale endpoint or identity protocol.
- Netlify deployment implementation.
- Monocle Man redesign.
- Secret-dependent checks.
- Conversation-memory proof.

## Required benchmark artifact layout

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

## Required metadata

`run-metadata.json` must use schema `chatgpt_lab.github_actions_run.v1`.

`source-metadata.json` must identify:

```text
repository = grahama1970/snippets
branch = preview-monocle-man-netlify
path = monocle-man-site/
commit = candidate commit
```

## Success boundary

The benchmark workflow may report a benchmark-CI-only pass if the site builds, smoke checks pass, screenshots exist, and required JSON artifacts exist.

That is not a live-site closure claim. Live-site closure requires Netlify metadata mapping the deployed URL to the tested commit.

## Tiny visible change

The initial candidate includes the footer text:

```text
Slice 001 evidence build: CI · screenshots · WebGPT record.
```

The benchmark smoke test checks this text via `data-slice-note`.

## Fail-closed requirements

- Missing CI run for the candidate commit means the iteration has insufficient evidence.
- Missing screenshots means rendered quality is unproven.
- Missing deployment metadata prevents live-site claims.
- Missing WebGPT artifacts prevents treating WebGPT collaboration as evidence.
- Invalid local-subagent requests must be refused with a receipt.
