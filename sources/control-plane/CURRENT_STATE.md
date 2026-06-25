# Current State

**As of:** 2026-06-25  
**Profile:** Monocle Man React contract benchmark  
**Overall readiness:** `NOT_READY`  
**Benchmark:** Monocle Man SPA

The control plane is active in `grahama1970/chatgpt-lab`. Slice 001 benchmark CI was previously hardened, and the next bounded Monocle Man experiment has now converted the benchmark fixture into a React/Vite SPA through a ChatGPT-authored branch and pull request in `grahama1970/snippets`.

## Readiness

| Capability | State | Evidence / caveat |
|---|---|---|
| Persistent ChatGPT Project | `READY` | Project `ChatGPT-Lab` was created by the user and this conversation was moved into it. |
| Dedicated control-plane repository | `READY` | `grahama1970/chatgpt-lab`, branch `main`. |
| Control-plane source check | `PASS` | Workflow is active and runs on pushes to `main`; latest control-plane evidence updates still need the current push run inspected before broader readiness promotion. |
| Self-improvement requirements | `DRAFT_V0.2` | Slice 001 scope, benchmark evidence layout, local-subagent request contract, and schema stubs are recorded. |
| GitHub source read/write | `READY` | ChatGPT Web has written to `grahama1970/chatgpt-lab` and `grahama1970/snippets`. |
| Skill discovery | `READY` | `grahama1970/agent-skills` registry is accessible; latest observed content hash: `2cb9ea5b36cef21e7c2d69e52cfd36da7b2e4f54895b03cbc878b37a64a83025`. |
| Monocle Man benchmark CI | `READY_REACT_CONTRACT` | `grahama1970/snippets` PR #3 merged as `043f1a7c807a30b221ddd56cd3ea744b34c1dfd8`. Candidate CI run `28198930713` passed on head SHA `911052a2973a005021cdd9a41c4eefda72cc3b34` and uploaded artifact `7890258305`. |
| Monocle Man evidence record | `READY` | Superseding iteration record: `iterations/2026-06-25-monocle-man-react-contract/`. |
| Netlify project | `READY` | Project `monocle-man-review`, site ID `df347395-47e5-4ed6-a1c7-57360a5735de`. |
| Verified Netlify deployment | `NOT_ESTABLISHED` | No deployment metadata yet maps the live URL to the merged React benchmark commit. The React benchmark pass is CI/artifact truth only; no live-site claim is made. |
| `$ask webgpt` collaboration | `NEEDS_ATTENTION` | Prior plan-collab attempts were blocked by ambiguous ChatGPT tab identity. |
| Local subagent bridge | `NOT_ESTABLISHED` | Only schema/refusal examples exist. |
| Bounded loop controller | `NOT_ESTABLISHED` | Manual ChatGPT-driven loop is proven for Slice 001 and the React contract round; deterministic controller script still needs implementation. |

## Current source locations

- Control plane: `grahama1970/chatgpt-lab`, branch `main`
- Requirements: `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`
- Benchmark source: `grahama1970/snippets`, branch `preview-monocle-man-netlify`, path `monocle-man-site/`
- Hardened benchmark PR: `https://github.com/grahama1970/snippets/pull/2`
- React contract benchmark PR: `https://github.com/grahama1970/snippets/pull/3`
- React contract benchmark merge commit: `043f1a7c807a30b221ddd56cd3ea744b34c1dfd8`
- React contract candidate CI run: `https://github.com/grahama1970/snippets/actions/runs/28198930713`
- React contract benchmark artifact: `monocle-man-benchmark-evidence`, ID `7890258305`, digest `sha256:005c8b06d93a71e8fab77642cd68f7cd68ee3be87ff3a7f38edb3651b197bc27`
- Netlify: `https://monocle-man-review.netlify.app`

## Immediate blockers to a closed loop

1. Establish Netlify deployment metadata that maps the live URL to the merged React benchmark commit.
2. Invoke `$ask webgpt` through a stable ChatGPT-Lab project binding and preserve artifacts.
3. Implement the dry-run local-subagent refusal/receipt path for Slice 002.
4. Implement a bounded loop controller script so ChatGPT invokes a deterministic loop rather than acting as the loop in prose.
5. Add machine-readable skill selection and dependency expansion beyond per-iteration recording.

## Next admissible milestone

`USABLE_WITH_GAPS` requires:

- current control-plane source-check workflow passes after the latest control-plane evidence updates;
- benchmark CI evidence remains available or is copied into durable iteration evidence;
- Netlify deployment metadata maps the live URL to the tested commit;
- one `$ask webgpt` review or planning round has preserved artifacts;
- no live-site claim is made without deployment proof.
