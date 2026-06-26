# PhatGPT-LAB — Verified Self-Improvement for Web Interfaces

<p align="center">
  <img
    src="assets/chatgpt-lab-header.webp"
    alt="Retro-futurist laboratory header showing a human brain beneath a glass bell jar on a dark walnut plinth with an etched brass PHATGPT-LAB plaque"
    width="100%"
  />
</p>

PhatGPT-LAB is a GitHub-backed control plane designed to prove that ChatGPT Web can build, verify, and improve software projects directly.

The repo stores everything ChatGPT needs to pick up where it left off: requirements, instructions, operating contracts, current state, schemas, scripts, evidence records, exported chats, and iteration history. ChatGPT Project Sources are read-only from the Web UI, so this repository acts as the writable external source of truth that ChatGPT can reload, change, review, and validate across sessions.

**The golden rule:** a model may propose an improvement; only current evidence may approve it.

## Why This Exists

ChatGPT can write code, but a reliable self-improvement loop needs more than conversation memory. It needs stable files, exact source references, deterministic checks, rendered screenshots, review artifacts, and evidence that survives across sessions.

This repo records:

1. what the project is trying to build;
2. which requirements and sources are canonical;
3. who controls the next implementation round;
4. which skills and repositories to load;
5. which prior chats explain intent and decisions;
6. what the current blockers are;
7. what evidence is required before accepting a result; and
8. how each iteration should be recorded.

## Project Mission

The mission is to prove a reusable, evidence-driven self-improvement system controlled from ChatGPT Web.

ChatGPT Web is the primary controller and default implementer. It selects the bounded objective, changes source through GitHub branches and pull requests, retrieves CI and deployment evidence, reviews rendered results, and decides whether to patch, merge, stop, or delegate. The project agent is a bounded local execution adapter for operations unavailable through current ChatGPT tools; it is not a co-equal planning authority.

The working model is simple:

![PhatGPT-LAB improvement cycle: observe, reason, verify, improve](artifacts/readme/chatgpt-lab-improvement-cycle.png)

1. **Observe** the repository, CI results, screenshots, and prior iteration artifacts.
2. **Reason** from current requirements, source state, and unresolved blockers.
3. **Verify** changes with GitHub Actions, deployment metadata, browser interactions, and rendered screenshots.
4. **Improve** the project by committing the smallest evidence-backed change and recording the iteration.

Bias: evidence over opinion. Chats, reviewers, and model judgments may guide the next action, but only concrete artifacts establish what happened.

## The Loop

```text
human objective or detected defect
    ↓
load current requirements + select the smallest useful skill chain
    ↓
baseline the exact Git commit and rendered site
    ↓
ChatGPT writes a bounded patch on an isolated branch
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

The **inner loop** improves the benchmark. The **outer loop** improves the skill selection, tests, evidence gates, reviewer quality, and stopping rules that produced the result.

## Try This First

```bash
git clone https://github.com/grahama1970/chatgpt-lab.git
cd chatgpt-lab

python3 scripts/validate_control_plane.py
sed -n '1,220p' sources/SOURCE_INDEX.md
sed -n '1,220p' docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md
sed -n '1,220p' docs/requirements/CONTROL_AUTHORITY.md
```

At the beginning of a new PhatGPT-LAB session, follow the bootstrap order in [`sources/SOURCE_INDEX.md`](sources/SOURCE_INDEX.md). Project agents should also read [`AGENTS.md`](AGENTS.md). Stable ChatGPT Project instructions live in [`sources/PROJECT_INSTRUCTIONS.md`](sources/PROJECT_INSTRUCTIONS.md).

## First Benchmark: Monocle Man

The Monocle Man single-page website is the first benchmark fixture. Improving it is not the whole project; it is the test case for proving the larger loop:

1. bootstrap current context from this repository;
2. select and load the smallest useful skill chain;
3. inspect the benchmark source at an exact commit;
4. establish a tested, screenshot-backed baseline;
5. implement one small ChatGPT-authored change;
6. run deterministic GitHub Actions checks;
7. retrieve logs and artifacts as structured evidence;
8. deploy the tested revision;
9. inspect desktop and mobile renders; and
10. write an iteration record that identifies the controller, any delegates, evidence, findings, and verdict.

Slice 001 is defined in [`docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`](docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md). Controller and delegation boundaries are normative in [`docs/requirements/CONTROL_AUTHORITY.md`](docs/requirements/CONTROL_AUTHORITY.md).

## Evidence Hierarchy

| Evidence | What it proves |
| --- | --- |
| GitHub source at an exact commit SHA | What code and configuration existed |
| GitHub Actions logs and artifacts | What executed and what passed or failed |
| Netlify deployment metadata | What revision is live |
| Fresh desktop/mobile screenshots | What the rendered interface looked like |
| Deterministic interaction results | What users could actually do |
| Independent code and design reviews | What should change next |
| Project-agent or `$ask` artifacts | What optional bounded collaboration produced |
| Exported chats and conversation memory | Context only — never execution proof |

A screenshot cannot prove keyboard behavior. A passing test cannot prove a layout is visually coherent. Source inspection cannot prove images loaded. Delegated summaries cannot replace raw command results.

## Project Shape

```text
README.md                              human entry point
PROJECT_KNOWLEDGE.md                   shared human/agent project snapshot
AGENTS.md                              agent bootstrap and role constraints
assets/                                repository identity and provenance
chats/                                 exported or summarized project context
sources/PROJECT_INSTRUCTIONS.md        persistent ChatGPT Project bootstrap
sources/SOURCE_INDEX.md                canonical source map and bootstrap order
sources/source-manifest.json           machine-readable sources and capabilities
sources/control-plane/                 operating contract, state, rubric, decisions
docs/requirements/                     Slice requirements and control authority
docs/research/                         non-canonical background notes
schemas/                               machine-readable evidence contracts
scripts/                               validation and maintenance tools
iterations/                            durable per-run evidence records
artifacts/                             CI receipts, screenshots, and reports
.github/workflows/source-check.yml     deterministic repository validation
.github/workflows/agent-dispatch.yml   bounded GitHub Actions executor proof
.github/workflows/webgpt-command-dispatcher.yml path-filtered WebGPT file-write bridge
agent-state/                           machine-readable controller memory
```

`chats/` explains intent and history, but it is not execution proof. Every accepted iteration must preserve durable revision identifiers, evidence references, findings, and a verdict.

## Operating Principles

- **Evidence before confidence.** Missing proof becomes `INSUFFICIENT_EVIDENCE`, not an optimistic pass.
- **ChatGPT controls the round.** The project agent executes only explicit local-only tasks and cannot self-approve.
- **Progressive skill loading.** Read the registry first; load only the smallest applicable skill chain and its declared dependencies.
- **Builder/reviewer separation.** ChatGPT may perform both roles, but the review phase remains read-only until findings are finalized.
- **Bounded retries.** The current default is three rounds and no more than five prioritized fixes per round.
- **Exact revision identity.** CI, deployment, screenshots, and review must all refer to the same candidate commit.
- **Durable learning.** Historical iteration and decision records are appended, not rewritten to make later results look cleaner.
- **Reconcile concurrent writes.** Refresh the branch before every write; never force stale work over newer project truth.

## Current Status

The control-plane repository, requirements, controller authority, source-check workflow, and WebGPT-to-GitHub-Actions bridge are established.

The proven bridge is narrow: WebGPT writes `agent-state/next-command.json`, GitHub runs `.github/workflows/webgpt-command-dispatcher.yml`, the proxy dispatches `.github/workflows/agent-dispatch.yml`, and the executor commits `agent-state/last-result.json`. The current proof is `push-proof-002`: dispatcher run `28238572045`, executor run `28238575766`, result commit `59e44c80d1acb864b6583bd17c1369d873692030`, and `agent-state/last-result.json` records `status: PASS`.

The next engineering milestone is to add one real but safe allowlisted command beyond `echo_hello` and prove it through the same bridge. A commit-linked live deployment and visual evidence remain required before Monocle live-site claims can pass.

Run the current validator with:

```bash
python3 scripts/validate_control_plane.py
python3 scripts/validate_agent_state.py
```

That check proves the control-plane structure is internally consistent. It does not, by itself, prove the benchmark website, deployment, or design review loop.

## Header Artwork

The photorealistic retro laboratory header was created specifically for PhatGPT-LAB. The brain represents reasoning; the glass makes it inspectable; the walnut plinth and etched brass plaque turn the system into a durable laboratory instrument rather than a generic cloud-AI metaphor. Artwork provenance and usage guidance live in [`assets/README.md`](assets/README.md).
