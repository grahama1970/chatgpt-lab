# Monocle Man React + GitHub Pages Plan

## Original vague request

The round began from a vague human request: a Monocle Man video link plus the instruction to create a designed landing page, with slides mentioned as a possible later extension.

The bounded deliverable for this round is a polished React landing page backed by deterministic evidence. Slides remain out of scope until separately selected.

## Mandatory preflight

Before implementation, the controller must record selected skills and tools. For this frontend deliverable, the required skills are:

1. `skills/best-practices-react/SKILL.md`
2. `skills/test-interactions/SKILL.md`
3. `skills/review-design/SKILL.md`
4. `skills/review-code/SKILL.md`
5. `skills/best-practices-report/SKILL.md`

Required tools are GitHub connector, web reference checks, GitHub Actions, and GitHub Pages.

For any frontend, `test-interactions`, `review-design`, `review-code`, and `best-practices-report` must be selected unless the committed plan explicitly scopes one away. For any API backend, the plan must select API contract tests and `review-code` before coding.

## Plan

1. Bootstrap source truth from `chatgpt-lab` and `agent-skills`.
2. Check current React, WAI-ARIA, Vite, and GitHub Pages references.
3. Convert the Monocle Man benchmark to a React/Vite SPA.
4. Implement qids, actions, titles, and action registry.
5. Implement modal, keyboard, focus, navigation, image, and animation behavior.
6. Prove behavior through GitHub Actions benchmark evidence.
7. Add GitHub Pages delivery for the static Vite build.
8. Inspect PR build and benchmark evidence before merge.
9. Inspect post-merge Pages deployment and live desktop/mobile rendering when exposed.
10. Write `REPORT.md` using `best-practices-report` before final response.

## Acceptance checks

- React source merged to the delivery branch.
- Benchmark CI passes with artifact evidence.
- GitHub Pages build/deploy workflow exists.
- Live page URL and deployment commit/ref are recorded.
- Desktop and mobile live visual inspection is recorded.
- Missing review or live-delivery evidence is explicitly marked `INSUFFICIENT_EVIDENCE`.

## Current status

React implementation and GitHub Pages workflow have been merged. Benchmark and PR Pages build evidence passed. Post-merge Pages deployment URL and live visual inspection remain unproven from the currently exposed connector surface.
