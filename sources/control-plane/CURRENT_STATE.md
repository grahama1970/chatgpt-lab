# Current State

**As of:** 2026-06-26  
**Profile:** Monocle Man React + GitHub Pages delivery  
**Overall readiness:** `NOT_READY`  
**Benchmark:** Monocle Man SPA

The control plane is active in `grahama1970/chatgpt-lab`. The Monocle Man benchmark fixture has been converted into a React/Vite SPA, CI-proven with deterministic evidence, and updated with a GitHub Pages delivery workflow. A fresh non-code delivery-proof PR was also merged. Live Pages deployment URL/visual inspection is still blocked by the currently exposed tool surfaces.

## Readiness

| Capability | State | Evidence / caveat |
|---|---|---|
| Persistent ChatGPT Project | `READY` | Project `ChatGPT-Lab` was created by the user and this conversation was moved into it. |
| Dedicated control-plane repository | `READY` | `grahama1970/chatgpt-lab`, branch `main`. |
| Control-plane source check | `PASS` | Workflow is active and runs on pushes to `main`; latest control-plane evidence updates still need the current push run inspected before broader readiness promotion. |
| Self-improvement requirements | `DRAFT_V0.2` | Slice 001 scope, benchmark evidence layout, local-subagent request contract, and schema stubs are recorded. |
| GitHub source read/write | `READY` | ChatGPT Web has written to `grahama1970/chatgpt-lab` and `grahama1970/snippets`. |
| Skill discovery | `READY` | `grahama1970/agent-skills` registry is accessible; latest observed content hash: `2cb9ea5b36cef21e7c2d69e52cfd36da7b2e4f54895b03cbc878b37a64a83025`. |
| Monocle Man benchmark CI | `READY_REACT_CONTRACT` | PR #3 merged as `043f1a7c807a30b221ddd56cd3ea744b34c1dfd8`. Candidate CI run `28198930713` passed and uploaded artifact `7890258305`. PR #4 benchmark run `28200837231` passed after adding normal-motion animation proof and uploaded artifact `7891035281`. PR #5 benchmark run `28203526868` also passed and uploaded artifact `7892100656`. |
| Monocle Man GitHub Pages workflow | `MERGED_DELIVERY_PROOF_BLOCKED` | PR #4 merged the Pages workflow as `aa30c43cbbb61d40ae7b22625e8dee24bb35c511`. PR #5 merged a fresh delivery-proof trigger as `e3fb0c09950c9cd11bbbbd8da7651326cccb5d8e`. PR Pages build runs `28200836938` and `28203526971` passed build steps. Post-merge Pages deployment run/URL is not visible through the currently exposed connector helper. |
| Monocle Man evidence record | `READY_WITH_BLOCKER` | Superseding iteration record: `iterations/2026-06-25-monocle-man-react-contract/`, including `PLAN.md`, `REPORT.md`, and `evidence/live-delivery-proof-attempt-pr5.json`. |
| Netlify project | `SECONDARY_STALE_OR_HISTORICAL` | Project `monocle-man-review`, site ID `df347395-47e5-4ed6-a1c7-57360a5735de`. Current GitHub-first path is GitHub Pages; Netlify no longer blocks this experiment unless later source reselects it. |
| Verified live deployment | `BLOCKED_TOOL_ACCESS` | GitHub Pages workflow and fresh trigger are merged, but no live Pages URL/deploy metadata and no live desktop/mobile visual inspection have been proven. Connector does not expose push-triggered Pages run/deployment metadata, and runtime DNS failed for likely Pages URLs. |
| GitHub dispatcher agent-state | `BOOTSTRAPPED` | `agent-state/*.json`, dispatcher schemas, validators, and `.github/workflows/agent-dispatch.yml` exist; first external WebGPT/API dispatch remains to be proven. |
| `$ask webgpt` collaboration | `NEEDS_ATTENTION` | Prior plan-collab attempts were blocked by ambiguous ChatGPT tab identity. |
| Local subagent bridge | `NOT_ESTABLISHED` | Only schema/refusal examples exist. |
| Bounded loop controller | `NOT_ESTABLISHED` | Manual ChatGPT-driven loop is proven for Slice 001 and the React/Pages rounds; deterministic controller script still needs implementation. |

## Current source locations

- Control plane: `grahama1970/chatgpt-lab`, branch `main`
- Requirements: `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`
- Benchmark source: `grahama1970/snippets`, branch `preview-monocle-man-netlify`, path `monocle-man-site/`
- React contract benchmark PR: `https://github.com/grahama1970/snippets/pull/3`
- React contract benchmark merge commit: `043f1a7c807a30b221ddd56cd3ea744b34c1dfd8`
- React contract candidate CI run: `https://github.com/grahama1970/snippets/actions/runs/28198930713`
- GitHub Pages delivery PR: `https://github.com/grahama1970/snippets/pull/4`
- GitHub Pages delivery merge commit: `aa30c43cbbb61d40ae7b22625e8dee24bb35c511`
- PR #4 Pages build run: `https://github.com/grahama1970/snippets/actions/runs/28200836938`
- PR #4 benchmark run: `https://github.com/grahama1970/snippets/actions/runs/28200837231`
- PR #4 benchmark artifact: `monocle-man-benchmark-evidence`, ID `7891035281`, digest `sha256:dc470f692016d680cb991faf6d20d08b8da3ad66fb6448283f3af8f53b32ed96`
- Live delivery proof PR: `https://github.com/grahama1970/snippets/pull/5`
- Live delivery proof merge commit: `e3fb0c09950c9cd11bbbbd8da7651326cccb5d8e`
- PR #5 Pages build run: `https://github.com/grahama1970/snippets/actions/runs/28203526971`
- PR #5 benchmark run: `https://github.com/grahama1970/snippets/actions/runs/28203526868`
- PR #5 benchmark artifact: `monocle-man-benchmark-evidence`, ID `7892100656`, digest `sha256:66793ccf37659226e5bbdbfbe813d7aface53260bc8d1a55f69e49860263d8f9`

## Immediate blockers to a closed live-delivery loop

1. Use GitHub UI, `gh` CLI, or a connector/API surface that can list push-triggered workflow runs and GitHub Pages deployments for merge commit `e3fb0c09950c9cd11bbbbd8da7651326cccb5d8e`.
2. Record the `deploy-pages` `page_url`, deployment status, and commit/ref mapping.
3. Visually inspect the live GitHub Pages URL at desktop and mobile widths, including normal animation behavior and reduced-motion behavior.
4. Run persona-bound `review-design` over live screenshots.
5. Run scoped `review-code` over PR #3, PR #4, and PR #5.
6. Invoke `$ask webgpt` through a stable ChatGPT-Lab project binding and preserve artifacts.
7. Implement the dry-run local-subagent refusal/receipt path for Slice 002.
8. Implement a bounded loop controller script so ChatGPT invokes a deterministic loop rather than acting as the loop in prose.
9. Prove WebGPT or a GPT Action can dispatch `.github/workflows/agent-dispatch.yml` and read the resulting `agent-state/last-result.json`.

## Next admissible milestone

`USABLE_WITH_GAPS` requires:

- current control-plane source-check workflow passes after the latest control-plane evidence updates;
- benchmark CI evidence remains available or is copied into durable iteration evidence;
- GitHub Pages deployment metadata maps the live URL to the tested commit;
- fresh desktop/mobile live visual evidence from GitHub Pages exists;
- one `$ask webgpt` review or planning round has preserved artifacts;
- no live-site claim is made without deployment proof.
