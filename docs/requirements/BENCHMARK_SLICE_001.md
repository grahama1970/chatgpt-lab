# Benchmark Slice 001 — Monocle Man Evidence Loop

## Objective

Prove a narrow end-to-end collaboration loop for the Monocle Man SPA without claiming the full autonomous self-improvement system is complete.

## In scope

- Benchmark GitHub Actions workflow in `grahama1970/snippets`.
- Playwright smoke and deterministic interaction checks.
- Console and same-origin network error capture.
- Accessibility checks with color contrast enabled.
- Required-image load and visibility checks.
- Desktop and mobile screenshots for first viewport, hero, focused states, content sections, and full page.
- Exact rendered HTML snapshot from the tested build.
- Artifact manifest with hashes and screenshot dimensions.
- Verdict JSON derived from the underlying evidence.
- ChatGPT-Lab validators for benchmark artifacts and iteration records.
- Local-subagent request/receipt schemas and refusal examples.
- One tiny visible website change checked by the benchmark.

## Out of scope

- Full loop controller.
- Live WebGPT-to-local-subagent bridge.
- Tailscale endpoint or identity protocol.
- Netlify deployment implementation.
- Broad Monocle Man redesign.
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
  image-status.json
  source/
    index.html
  screenshots/
    desktop.png
    mobile.png
    desktop-hero.png
    mobile-hero.png
    desktop-full.png
    mobile-full.png
    desktop-lines.png
    mobile-lines.png
    desktop-modal.png
    mobile-menu.png
  deployment-metadata.json
  artifact-manifest.json
  verdict.json
```

## Required metadata

`run-metadata.json` must use schema `chatgpt_lab.github_actions_run.v1`.

`source-metadata.json` must identify the repository, candidate branch, `monocle-man-site/` path, and tested commit.

When a pull-request merge commit is tested, preserve both the tested merge SHA and the pull-request head SHA. Do not silently treat them as the same identity.

## Visual evidence gate

Screenshot existence alone is not a visual pass. A benchmark-CI-only pass requires:

- every required image has non-zero intrinsic dimensions and visible pixels;
- no required image uses the missing-image fallback;
- desktop and mobile layouts have no unintended horizontal overflow;
- navigation, mobile menu, film modal, keyboard operation, and external-link checks pass;
- reduced-motion behavior is verified;
- no unexpected console error or same-origin network failure remains;
- no critical or serious accessibility violation remains;
- the artifact contains the rendered HTML and all required screenshots;
- the verdict is computed from these artifacts rather than workflow status alone.

## Success boundary

The workflow may report `PASS` with `scope = benchmark_ci_only` when all required CI evidence exists and blocking checks pass.

That is not a live-site closure claim. Live-site closure requires Netlify metadata mapping the deployed URL to the exact tested commit.

## Tiny visible change

The initial candidate includes the footer text:

```text
Slice 001 evidence build: CI · screenshots · WebGPT record.
```

The benchmark smoke test checks this text via `data-slice-note`.

## Regression proof

The first Slice 001 workflow reported `PASS` although the screenshots showed a missing hero image. The corrected gate must preserve:

1. a failing run that reports image and accessibility blockers;
2. a later passing run after image delivery and contrast are fixed;
3. current desktop and mobile screenshots showing the monocle subject;
4. rendered HTML without unresolved `/.netlify/images` transform URLs;
5. a new iteration record that supersedes, but does not rewrite, the historical record.

## Fail-closed requirements

- Missing CI for the candidate means insufficient evidence.
- Missing or stale screenshots leave rendered quality unproven.
- DOM existence does not prove an image rendered.
- Screenshot files without runtime assertions do not prove visual correctness.
- Missing deployment metadata prevents live-site claims.
- Missing WebGPT artifacts prevents treating WebGPT collaboration as evidence.
- Invalid local-subagent requests must be refused with a receipt.
