# Decision Ledger

Append new decisions. Do not rewrite old entries merely because later work changes direction.

## 2026-06-25 — D-001: GitHub is the external project source

**Decision:** Use a versioned GitHub control plane because this ChatGPT session cannot add or update Project Sources directly.

**Consequence:** Every session must bootstrap from `sources/SOURCE_INDEX.md`; conversational memory is not the source of truth.

## 2026-06-25 — D-002: Use a dedicated control-plane repository

**Decision:** Target `grahama1970/webgpt-lab`, branch `main`, as the canonical control plane.

**Migration rule:** The earlier `grahama1970/snippets@chatgpt-lab:chatgpt-lab/` branch remains historical bootstrap evidence after this repository is populated and validated.

## 2026-06-25 — D-003: Evidence has explicit precedence

**Decision:** Git source proves code, GitHub Actions proves execution, Netlify proves deployment, and fresh screenshots plus interaction results prove rendered behavior. Model prose cannot override those artifacts.

## 2026-06-25 — D-004: No separate coding agent is required

**Decision:** ChatGPT may implement and review the website directly.

**Guardrail:** Builder and reviewer phases remain logically separate; the reviewer judges current source and rendered evidence rather than the builder's rationale.

## 2026-06-25 — D-005: The improvement loop must be bounded and recorded

**Decision:** Use a maximum of three rounds per run and at most five prioritized fixes per round. Each round writes an audit artifact before continuing.

## 2026-06-25 — D-006: Do not invent performance gates

**Decision:** Quantitative performance thresholds remain `NOT_ESTABLISHED` until a measured baseline and explicit acceptance decision are recorded.

## 2026-06-25 — D-007: Repository bundle is migration input, not execution proof

**Decision:** A successful local package validation proves file integrity only. The repository becomes active evidence only after GitHub Actions validates the pushed commit.

## 2026-06-25 — D-008: Dedicated repository identity is ChatGPT-Lab

**Decision:** Use `grahama1970/chatgpt-lab`, branch `main`, as the canonical control-plane repository identity.

**Evidence:** The local project and ChatGPT Project are named ChatGPT-Lab, and the exported bootstrap chat requested a `chatgpt-lab` repository when direct Project Source updates were unavailable.

**Update:** The repository was created with the authenticated `gh` CLI, pushed to `main`, and validated by GitHub Actions run `28180430889`.

**Local preparation:** The package has been initialized as a local git repository on branch `main` with `origin` set to `git@github.com:grahama1970/chatgpt-lab.git`.

## 2026-06-25 — D-009: Keep root minimal

**Decision:** Keep root limited to `README.md`, repository infrastructure, and top-level directories. Move ChatGPT source-loading files into `sources/` and package receipts into `artifacts/package/`.

**Consequence:** Future sessions bootstrap from `sources/SOURCE_INDEX.md` and `sources/source-manifest.json`. Local package checksums are verified with `sha256sum -c artifacts/package/SHA256SUMS.txt`.

## 2026-06-25 — D-010: Requirements lead implementation

**Decision:** Capture the ChatGPT self-improvement loop as explicit requirements before building benchmark CI, WebGPT delegation, local subagent bridges, or iteration automation.

**Consequence:** `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md` is now part of the canonical bootstrap path. New loop capabilities should update that requirements artifact before implementation broadens the system.

## 2026-06-25 — D-011: ChatGPT Web owns the loop

**Decision:** ChatGPT Web is the primary controller and default implementer. It owns requirements, the next bounded objective, GitHub branches and pull requests, evidence inspection, reviewer reconciliation, merge decisions, and final gate verdicts.

**Project-agent boundary:** The ChatGPT-Lab project agent is a delegated local execution adapter for capabilities unavailable to ChatGPT Web. It may perform explicitly bounded local work and return raw artifacts, but it is not a co-equal planning authority, may not broaden scope, and may not self-approve or choose the next round.

**Consequence:** The default benchmark write path is a ChatGPT-authored branch and pull request. Project-agent-mediated changes are fallback only and require a structured task contract plus raw execution receipts.

## 2026-06-25 — D-012: ChatGPT Web takeover gates

**Decision:** ChatGPT Web owns both `grahama1970/chatgpt-lab` and the bounded Monocle Man benchmark surface in `grahama1970/snippets`, with different authority. `chatgpt-lab` is the durable control plane. `snippets` authority is limited to branch `preview-monocle-man-netlify` and path `monocle-man-site/` unless a later decision expands scope.

**Next milestone:** The immediate milestone is the first bounded self-improvement iteration using benchmark CI evidence. Netlify deployment proof is the next gate for live-site or project-ownership claims after CI evidence is normalized into an iteration record.

**Write path:** ChatGPT Web should use branch and pull-request flow by default. Direct pushes to `main` are reserved for emergency control-plane metadata only and should be avoided once the branch/PR flow works.

**WebGPT binding:** Use a fresh dedicated WebGPT controller/reviewer tab named `ChatGPT-Lab WebGPT Controller` for durable takeover work. Do not rely long-term on `phatgpt` tab `837355496` unless the binding is explicitly recorded and proven healthy for the current session.

**Evidence retention:** Keep canonical GitHub references: run id, job id where available, artifact name/id where available, head SHA, branch, and workflow URL. Also copy normalized durable evidence into `chatgpt-lab/iterations/.../evidence/`, including JSON reports, artifact manifest, verdict, screenshot index or screenshots, and important excerpts, because GitHub Actions artifacts can expire.

**Local subagent scope:** Slice 002 should implement the dry-run local task receipt path. It must validate request schema, refuse unsafe tasks, produce `local-subagent-receipt.json`, and prove fail-closed behavior. It must not perform mutating local work yet.

**Ownership bar:** A scoped milestone may say ChatGPT owns the benchmark CI loop when exact-commit CI, artifacts, screenshots, `$ask webgpt` artifacts, and a valid iteration record exist. Project-level ownership requires all of: exact-commit benchmark CI, live Netlify deployment mapped to that commit, preserved `$ask webgpt` artifacts, and one valid iteration record.

**Verdict rule:** Netlify proof is not required before every scoped benchmark `PASS` when the iteration explicitly avoids a live-site claim. Netlify proof is required before `USABLE_WITH_GAPS`, live-site improvement claims, or project-ownership `PASS`.

## 2026-06-25 — D-013: Commit attribution follows the controller

**Decision:** Do not author project commits under third-party model names, vendor names, or bot-like identities that imply a controller other than ChatGPT Web or the lab identity made the change.

**Consequence:** Local project-agent commits must set repo-local Git identity before committing. The source-check workflow validates the latest commit author and core authority docs so accidental global Git identity leakage is treated as a control-plane error.

## 2026-06-25 — D-014: Local project agents are last-resort low-capacity execution bridges

**Decision:** Local project agents are not default collaborators or semantic authorities. They are cost-constrained, low-capacity execution bridges for local-only proof collection, local command execution, and tiny bounded bug fixes when ChatGPT Web cannot produce the required evidence through direct connectors, GitHub, hosted CI, selected skills, deployment tooling, or `$ask` collaboration.

**Consequence:** ChatGPT Web must not delegate architecture, broad implementation, planning, review verdicts, evidence reconciliation, or next-step selection to a local project agent. Any local-agent use requires a bounded task contract and raw receipts. The canonical policy is `sources/control-plane/LOCAL_AGENT_POLICY.md`.

**Monocle implication:** For the current live-delivery blocker, a local agent would only be allowed to run a narrow command set such as `gh` workflow/deployment inspection and live screenshot capture, then return receipts. It must not make a PASS claim.
