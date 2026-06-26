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

The mission is to prove a reusable, evidence-driven self-improvement system controlled from ChatGPT Web and grounded in GitHub evidence.

ChatGPT Web / WebGPT is the primary controller. It reads the repo state, selects the bounded objective, names the skills and contracts to use, creates or updates the GitHub issue/PR/task, retrieves CI and deployment evidence, reviews rendered results, and decides whether to continue, stop, or delegate. The Codex cloud agent is the preferred implementer for GitHub-native code changes. The local project agent is only a bounded execution adapter for operations unavailable through current ChatGPT/GitHub tools; it is not a co-equal planning authority.

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
WebGPT loads current requirements + selects the smallest useful skill chain
    ↓
WebGPT creates a bounded GitHub issue/PR/task
    ↓
Codex cloud agent implements on a branch or PR
    ↓
GitHub Actions: source check + benchmark + interactions + accessibility + screenshots
    ↓
GitHub Pages deploys the tested commit
    ↓
WebGPT/ChatGPT reviews fresh CI, deployment, and screenshot evidence
    ↓
PASS | NEEDS_CHANGES | BLOCKED | INSUFFICIENT_EVIDENCE
    ↓
retry within a fixed round limit, then preserve the lesson
```

The **inner loop** improves the benchmark through GitHub-native work. The **outer loop** improves the skill selection, task contracts, tests, evidence gates, reviewer quality, and stopping rules that produced the result.

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
.github/workflows/assign-copilot-agent.yml on-demand Copilot cloud-agent handoff test
.github/workflows/opencode-phatgpt.yml GitHub-event OpenCode dispatcher for PhatGPT agents
.opencode/agents/                      OpenCode primary dispatcher and subagent prompts
scripts/phatgpt_local_worker_cycle.py  short-lived PR/issue worker contract validator
agent-state/                           machine-readable controller memory
../agent-skills/agents/phatgpt-coder/  mutating event worker contract
../agent-skills/agents/phatgpt-reviewer/ read-only event reviewer contract
../agent-skills/agents/phatgpt-researcher/ optional task-spec researcher contract
```

`chats/` explains intent and history, but it is not execution proof. Every accepted iteration must preserve durable revision identifiers, evidence references, findings, and a verdict.

## Operating Principles

- **Evidence before confidence.** Missing proof becomes `INSUFFICIENT_EVIDENCE`, not an optimistic pass.
- **ChatGPT controls the round.** The project agent executes only explicit local-only tasks and cannot self-approve.
- **WebGPT gives Codex bounded work.** WebGPT names the objective, skills, files, validation commands, and proof requirements; Codex cloud implements the GitHub-native change.
- **Event workers are role-bounded.** The MVP loop uses GitHub events or `opencode serve` to start an OpenCode primary dispatcher, then delegates to a coder, reviewer, or optional researcher subagent. Each invocation handles at most one PR/issue and exits.
- **GitHub tickets are the queue contract.** The PhatGPT coder, reviewer, and researcher follow `best-practices-github-ticket`: lease one ticket, honor route/agent metadata, require deterministic proof, keep repair and review separate, and write PR comments for traceability.
- **Progressive skill loading.** Read the registry first; load only the smallest applicable skill chain and its declared dependencies.
- **Builder/reviewer separation.** ChatGPT may perform both roles, but the review phase remains read-only until findings are finalized.
- **Bounded retries.** The current default is three rounds and no more than five prioritized fixes per round.
- **Exact revision identity.** CI, deployment, screenshots, and review must all refer to the same candidate commit.
- **Durable learning.** Historical iteration and decision records are appended, not rewritten to make later results look cleaner.
- **Reconcile concurrent writes.** Refresh the branch before every write; never force stale work over newer project truth.

## Current Status

The control-plane repository, requirements, controller authority, source-check workflow, and WebGPT-to-GitHub-Actions bridge are established.

The proven bridge is narrow but no longer read-only: WebGPT writes `agent-state/next-command.json`, GitHub runs `.github/workflows/webgpt-command-dispatcher.yml`, the proxy dispatches `.github/workflows/agent-dispatch.yml`, and the executor commits `agent-state/last-result.json`. The first mutation proof is `apply-text-patch-proof-001`: WebGPT command commit `5450331fcf932ddcbf79cbea490005f250c7d29e`, dispatcher run `28245510581`, executor run `28245515891`, result commit `064f5fd5b2b52bd1874c205edaeb616f7eae0533`, and `agent-state/last-result.json` records `status: PASS`.

The safe mutation command is `apply_text_patch`. It accepts only a schema-validated payload with an allowlisted `monocle-man-site/**` path, exact old text, exact new text, and `expected_replacements: 1`. The first live command changed `monocle-man-site/src/main.jsx` from `One lens. One side. No compromise.` to `One lens. One side. Evidence over opinion.` and the follow-on checks for commit `064f5fd5b2b52bd1874c205edaeb616f7eae0533` passed: Source Check run `28245666829`, Monocle Benchmark run `28245666824`, and GitHub Pages proof run `28245666963`.

This is not yet a broad autonomous project-ownership claim. The remaining work is to reduce local project-agent involvement, add review receipts, classify third-party network noise, implement the dry-run local-subagent receipt path, and turn the current manual loop into a bounded controller.

The next handoff test is `.github/workflows/assign-copilot-agent.yml`. It is manually triggered with an issue number, calls GitHub's public-preview Agent Tasks API, and writes `agent-state/last-result.json` with either `PASS`, `BLOCKED_CLOUD_AGENT_AUTH`, or `BLOCKED_CLOUD_AGENT_API`. It requires a user-to-server token in the repository secret `COPILOT_AGENT_TASK_TOKEN`; the default `GITHUB_TOKEN` is not sufficient for starting Copilot cloud-agent tasks.

The preferred MVP trigger is event driven. `.github/workflows/opencode-phatgpt.yml` starts OpenCode on issue comments, PR comments, PR events, or manual dispatch. The GitHub Action model is selected from repository variables; the current smoke path uses `PHATGPT_OPENCODE_MODEL=opencode/deepseek-v4-flash-free` with `PHATGPT_OPENCODE_VARIANT=medium` because the earlier `opencode/gpt-5.5` OAuth run was blocked by account balance. The OpenCode primary agent is `.opencode/agents/phatgpt-dispatcher.md`; it routes to `@phatgpt-coder`, `@phatgpt-reviewer`, or `@phatgpt-researcher`. `opencode serve` is the local/Tailscale control surface when the loop needs to be driven from outside GitHub Actions. Cron is only a fallback watchdog.

The first bounded event-worker proof is PR #8. A valid `phatgpt-task:v1` block asked for a one-line Monocle caption change, the coder worker changed `monocle-man-site/src/main.jsx`, PR checks passed at head `146d51dc54b977dab01470a0ae288af38b9f7813`, and the reviewer commented a PR-scope `PASS`. This does not prove live deployment ownership because the Pages deploy job is skipped for PR branches.

The first WebGPT-created PR test is PR #9, and it failed closed for the right reason: the PR body had no `best-practices-github-ticket` metadata and no `phatgpt-task:v1` block, so the worker refused it and commented the missing contract. Future WebGPT PRs must use `.github/pull_request_template.md` and include the machine-readable task block before invoking `/phatgpt`.

The local-worker path remains a deterministic fallback and smoke harness. `scripts/phatgpt_local_worker_cycle.py` inspects one GitHub PR or issue, requires a structured `phatgpt-task:v1` block, validates allowed commands, paths, evidence, and stop conditions, then writes a receipt. It has role modes matching the OpenCode agents:

- `phatgpt-coder`: selects one `phatgpt-local-agent` PR, validates the task, and is the only role allowed to mutate code in the later execution slice.
- `phatgpt-reviewer`: selects one `phatgpt-ready-for-review` PR, runs read-only checks, and labels/comment-reports `pass`, `needs-changes`, or `blocked`.
- `phatgpt-researcher`: prepares or refuses implementation-ready task blocks when the PR is too vague for the coder.

The shared agent contracts live in `../agent-skills/agents/phatgpt-coder/`, `../agent-skills/agents/phatgpt-reviewer/`, and `../agent-skills/agents/phatgpt-researcher/`. The `.opencode/agents/` files are the repo-local OpenCode entrypoint prompts that call those roles. This slice proves pickup/validation/refusal receipts and adds the event-triggered OpenCode entrypoint; a live OpenCode run remains the next gate.

All three shared contracts compose `best-practices-github-ticket`. A ChatGPT/WebGPT PR is not actionable until it contains ticket type, target path, current state, requested outcome, route or agent metadata when known, required proof, non-goals, and a valid `phatgpt-task:v1` block. The coder must lease before mutation; the reviewer must stay read-only and comment every verdict on the GitHub PR; closure requires deterministic proof and reconciled review findings.

Run the current validator with:

```bash
python3 scripts/validate_control_plane.py
python3 scripts/validate_agent_state.py
```

That check proves the control-plane structure is internally consistent. It does not, by itself, prove the benchmark website, deployment, or design review loop.

## Header Artwork

The photorealistic retro laboratory header was created specifically for PhatGPT-LAB. The brain represents reasoning; the glass makes it inspectable; the walnut plinth and etched brass plaque turn the system into a durable laboratory instrument rather than a generic cloud-AI metaphor. Artwork provenance and usage guidance live in [`assets/README.md`](assets/README.md).
