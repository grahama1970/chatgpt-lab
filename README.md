# ChatGPT-Lab — Verified Self-Improvement for Web Interfaces

<p align="center">
  <img
    src="assets/chatgpt-lab-header.webp"
    alt="Retro-futurist laboratory header showing a human brain beneath a glass bell jar on a dark walnut plinth with an etched brass CHATGPT-LAB plaque"
    width="100%"
  />
</p>

ChatGPT-Lab is a GitHub-backed control plane for running **bounded,
evidence-driven software improvement loops** from ChatGPT Web. It keeps project
instructions, operating rules, source references, schemas, exported chats,
iteration receipts, and verification evidence in a place that can be read,
updated, reviewed, and validated across sessions.

The Monocle Man SPA is the first benchmark fixture. Improving that site is not
the whole project; it is the test case for proving a reusable loop that selects
skills, writes code, runs CI, deploys the tested revision, inspects real renders,
reviews code and design independently, applies validated fixes, and records what
the process learned.

**The golden rule:** a model may propose an improvement; only current evidence
may approve it.

## The Loop

```text
human objective or detected defect
    ↓
load current project sources + select the smallest useful skill chain
    ↓
baseline the exact Git commit and rendered site
    ↓
write a coherent patch on an isolated branch
    ↓
GitHub Actions: build + interactions + accessibility + screenshots
    ↓
Netlify: deploy the tested commit
    ↓
independent code review + visual review of fresh evidence
    ↓
PASS | NEEDS_CHANGES | BLOCKED | INSUFFICIENT_EVIDENCE
    ↓
retry within a fixed round limit, then preserve the lesson
```

The **inner loop** improves the website. The **outer loop** improves the skill
selection, tests, evidence gates, reviewer quality, and stopping rules that
produced the result.

## Try This First

You do not need to memorize the entire control plane. Start by validating it and
reading the canonical source map:

```bash
git clone https://github.com/grahama1970/chatgpt-lab.git
cd chatgpt-lab

python3 scripts/validate_control_plane.py
sed -n '1,220p' sources/SOURCE_INDEX.md
sed -n '1,220p' sources/control-plane/CURRENT_STATE.md
```

At the beginning of a new ChatGPT-Lab session, read these files in order:

1. [`sources/SOURCE_INDEX.md`](sources/SOURCE_INDEX.md)
2. [`sources/source-manifest.json`](sources/source-manifest.json)
3. [`sources/control-plane/OPERATING_CONTRACT.md`](sources/control-plane/OPERATING_CONTRACT.md)
4. [`sources/control-plane/CURRENT_STATE.md`](sources/control-plane/CURRENT_STATE.md)
5. [`sources/control-plane/REVIEW_RUBRIC.md`](sources/control-plane/REVIEW_RUBRIC.md)
6. [`sources/control-plane/DECISIONS.md`](sources/control-plane/DECISIONS.md)
7. [`sources/README.md`](sources/README.md)
8. relevant context under [`chats/`](chats/)

Project agents should also read [`AGENTS.md`](AGENTS.md). Stable instructions for
the ChatGPT Project live in
[`sources/PROJECT_INSTRUCTIONS.md`](sources/PROJECT_INSTRUCTIONS.md).

## Evidence Hierarchy

| Evidence | What it proves |
| --- | --- |
| GitHub source at an exact commit SHA | What code and configuration existed |
| GitHub Actions logs and artifacts | What executed and what passed or failed |
| Netlify deployment metadata | What revision is live |
| Fresh desktop/mobile screenshots | What the rendered interface looked like |
| Deterministic interaction results | What users could actually do |
| Independent code and design reviews | What should change next |
| Exported chats and conversation memory | Context only — never execution proof |

A screenshot cannot prove keyboard behavior. A passing test cannot prove a layout
is visually coherent. Source inspection cannot prove that images loaded. The
loop requires the right evidence for each claim.

## Current Benchmark

The Monocle Man SPA is intentionally small enough for fast iteration while still
exercising typography, imagery, responsive composition, embedded video,
keyboard interaction, accessibility, deployment, and subjective visual review.

- Benchmark source: `grahama1970/snippets`, branch
  `preview-monocle-man-netlify`, path `monocle-man-site/`
- Render target: Netlify project `monocle-man-review`
- Skills source: `grahama1970/agent-skills`
- Current readiness and blockers:
  [`sources/control-plane/CURRENT_STATE.md`](sources/control-plane/CURRENT_STATE.md)

## Repository Shape

The repository mirrors the durable information a ChatGPT Project needs:

```text
README.md                              human entry point
AGENTS.md                              agent bootstrap and role constraints
assets/                                repository identity and provenance
chats/                                 exported or summarized project context
sources/PROJECT_INSTRUCTIONS.md        persistent ChatGPT Project bootstrap
sources/SOURCE_INDEX.md                source map and bootstrap order
sources/source-manifest.json           machine-readable sources and capabilities
sources/control-plane/                 operating contract, state, rubric, decisions
schemas/iteration.schema.json          iteration evidence contract
scripts/validate_control_plane.py      local and CI source validation
iterations/                            durable per-run evidence records
artifacts/                             CI receipts, screenshots, and reports
.github/workflows/source-check.yml     deterministic repository validation
```

`chats/` explains intent and history, but it is not execution proof. Generated
artifacts may be retained elsewhere, but every accepted iteration must preserve
durable identifiers, revision identity, findings, and verdict.

## Operating Principles

- **Evidence before confidence.** Missing proof becomes
  `INSUFFICIENT_EVIDENCE`, not an optimistic pass.
- **Progressive skill loading.** Read the registry first; load only the smallest
  applicable skill chain and its declared dependencies.
- **Builder/reviewer separation.** ChatGPT may perform both roles, but the review
  phase remains read-only until findings are finalized.
- **Bounded retries.** The current default is three rounds and no more than five
  prioritized fixes per round.
- **Exact revision identity.** CI, deployment, screenshots, and review must all
  refer to the same candidate commit.
- **Durable learning.** Historical iteration and decision records are appended,
  not rewritten to make later results look cleaner.

## Current Status

The control-plane repository and source-check workflow are established. The full
system is not yet a closed loop: benchmark Playwright/accessibility/screenshot CI,
a commit-linked Netlify deployment, a coded loop controller, and automated skill
routing remain the principal engineering milestones.

Run the current validator with:

```bash
python3 scripts/validate_control_plane.py
```

That check proves the control-plane structure is internally consistent. It does
not, by itself, prove the benchmark website, deployment, or design review loop.

## Header Artwork

The photorealistic retro laboratory header was created specifically for
ChatGPT-Lab. The brain represents reasoning; the glass makes it inspectable; the
walnut plinth and etched brass plaque turn the system into a durable laboratory
instrument rather than a generic cloud-AI metaphor. Artwork provenance and
usage guidance live in [`assets/README.md`](assets/README.md).
