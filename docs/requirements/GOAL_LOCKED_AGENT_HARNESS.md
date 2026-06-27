# Goal-Locked Agent Harness

**Status:** PR 1 contract slice  
**Scope:** contracts, examples, validators, and documentation only  
**Runtime behavior:** unchanged

## Purpose

PhatGPT-LAB needs a durable protocol for greenfield work where the problem and
solution are not known in advance. The protocol must let humans, WebGPT,
GitHub Actions, local cron, and bounded subagents cooperate through GitHub
Issues, Pull Requests, comments, labels, schemas, receipts, and artifacts
without losing the active human goal.

The first slice freezes the protocol. It does not implement ticket scanning,
leases, cron, orchestration, WebGPT browser calls, or GitHub mutation.

## Invariants

1. GitHub-visible state is the durable control surface.
2. Every actionable handoff preserves the active human-approved goal.
3. Only the human may create a new immutable goal version or alter success
   criteria.
4. Agents may propose amendments but may not apply them.
5. Every human, WebGPT, and subagent handoff must include exactly one
   `next.subagent`.
6. Missing goal hash, authority, route, stop condition, or proof fails closed.
7. ChatGPT/WebGPT output is a proposal until it is captured in GitHub or repo
   state and passes validation.
8. Runtime automation comes later, after the contracts validate in CI.

## Initial Role Allowlist

The first slice recognizes only these roles:

```text
human
goal-guardian
webgpt-ticket-author
coder
reviewer
releaser
```

Broader specialist roles such as researcher, experiment-designer,
data-scientist, modeler, mathematician, and visualizer are intentionally
deferred until the core protocol is proven.

## Durable Human Authority

A human instruction changes the harness only after it becomes GitHub-visible or
repo-visible. Accepted durable forms are:

```text
GitHub issue comment containing human_interjection.v1
GitHub PR comment containing human_interjection.v1
repo file update to goals/current.json through a human-approved PR
repo artifact recording a human-approved goal decision
```

A private ChatGPT conversation instruction is not durable by itself. It may be
converted into a GitHub/repo artifact, but the harness must validate that
artifact before acting on it.

## Required Contract Files

```text
goals/current.json
schemas/goal-capsule.schema.json
schemas/agent-handoff.schema.json
schemas/human-interjection.schema.json
schemas/generated-ticket.schema.json
examples/agent-harness/
scripts/validate_goal_capsule.py
scripts/validate_agent_ticket_contracts.py
```

## Goal Capsule

`goals/current.json` stores the active human-approved goal. Its `goal_hash` is
computed from canonical JSON containing:

```text
immutable_goal
success_criteria
constraints
non_goals
human_change_required_for
```

Validators reject the capsule when the hash does not match the goal material.
Agents must not edit the active capsule except to propose a separate amendment.

## Handoff Contract

Every actionable handoff must carry:

```text
original_goal
fresh_context
results or requested_work
rationale
evidence
required_evidence
stop_condition
next.subagent
```

`next.subagent` is always explicit, including pause, stop, and reject flows. For
those flows the route is:

```json
{
  "next": {
    "subagent": "human",
    "executor": "human"
  }
}
```

## WebGPT Ticket Contract

WebGPT may draft a `generated-ticket.v1`, but it may not directly mutate
GitHub, change the immutable goal, bypass validation, or declare final success.
The future orchestrator is responsible for posting or rejecting the generated
ticket.

## PR 1 Acceptance

The PR 1 slice is acceptable when:

```text
python3 scripts/validate_goal_capsule.py
python3 scripts/validate_agent_ticket_contracts.py
python3 -m unittest discover -s tests
python3 scripts/validate_control_plane.py
```

all exit 0, and the source-check workflow runs those validators in CI.
