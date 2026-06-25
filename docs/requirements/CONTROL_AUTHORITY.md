# ChatGPT-Lab Control Authority

**Status:** Normative clarification v1  
**Updated:** 2026-06-25  
**Applies to:** `SELF_IMPROVEMENT_REQUIREMENTS.md`, Slice 001, and all later implementation rounds

## Decision

ChatGPT Web is the **primary controller and default implementer** for ChatGPT-Lab.

It owns:

- interpretation and amendment of requirements;
- selection of the next bounded objective;
- skill selection and dependency loading;
- GitHub branches, commits, and pull requests created through its connected tools;
- retrieval and inspection of CI and deployment evidence;
- rendered design review;
- reconciliation of reviewer findings;
- the merge, retry, stop, or delegation decision; and
- the final gate verdict.

The ChatGPT-Lab project agent is a **delegated local execution adapter**, not a co-equal planning authority and not the default author of the next round.

## Default Write Path

```text
ChatGPT Web
  -> load current requirements and source state
  -> select one bounded objective
  -> create an isolated GitHub branch
  -> implement the change
  -> open a pull request
  -> retrieve matching CI logs and artifacts
  -> inspect screenshots and rendered behavior
  -> review, patch, merge, or stop
```

A project-agent-mediated commit is permitted only when the required action depends on local-only state or is unavailable through ChatGPT's connected tools.

## Project Agent Boundary

The project agent may:

- run local checks and authenticated local CLIs;
- operate `$ask webgpt`, browser-oracle, workstation, private-service, or cron surfaces;
- execute a structured task explicitly delegated by ChatGPT Web;
- preserve raw command output, screenshots, logs, hashes, and receipts; and
- return blockers or refusal evidence.

The project agent must not independently:

- broaden requirements or Slice 001 scope;
- select a new project objective;
- add architecture outside the approved round;
- overwrite concurrent ChatGPT work without reconciliation;
- merge or promote a candidate;
- declare the visual design or system complete; or
- treat its own summary as proof.

## Optional Collaborators

`$ask webgpt`, the project agent, CodeRabbit, and local subagents are advisory or execution workers beneath the ChatGPT-controlled builder/reviewer/gate loop.

They may produce findings or artifacts. They do not own the next round or final verdict.

## Interpretation Of Existing Requirements

This clarification resolves ambiguous language in `SELF_IMPROVEMENT_REQUIREMENTS.md` as follows:

1. **REQ-CAP-002 and REQ-CAP-003:** direct ChatGPT branch-and-PR writes are the default. Project-agent-mediated changes are fallback only.
2. **REQ-CAP-008:** `$ask webgpt` is an optional collaboration capability, not the default implementation path.
3. **First Acceptance Milestone item 6:** preserved `$ask` artifacts are required only for a run that actually selects the `$ask webgpt` path. The direct ChatGPT/GitHub/CI path is not blocked by duplicate browser tabs.
4. **Remaining Open Question 2:** Slice 001 should land through an isolated branch and pull request before merge.
5. **Remaining Open Question 3:** ChatGPT Web chooses the tiny visible benchmark change after the CI baseline exists; the project agent does not choose it independently.
6. **Local subagent contracts:** schemas and dry-run refusal tests may be prepared in Slice 001, but live delegation is not on the critical path.

## Delegation Receipt

When delegation is required, the iteration record must identify:

- controlling ChatGPT session or control-plane ref;
- delegate identity;
- task id and objective;
- allowed files and commands;
- timeout and refusal conditions;
- commands actually run;
- files touched;
- raw artifacts and hashes;
- unresolved blockers; and
- ChatGPT's final acceptance or rejection decision.

## Concurrency Rule

Before every write, ChatGPT refreshes the target file or branch. If another actor has changed the repository, ChatGPT reconciles the new evidence and creates a fresh branch when necessary. It must not force an outdated branch over current `main` merely to preserve prior work.

## Next Round

After this clarification is merged, ChatGPT Web should implement Slice 001's benchmark CI and evidence harness directly in the benchmark repository through a new branch and pull request.

The project agent should participate only if ChatGPT identifies a specific local-only capability gap and issues a bounded task contract.
