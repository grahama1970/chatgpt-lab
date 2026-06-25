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
