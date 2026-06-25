# Local Agent Policy

## Decision

Local project agents are last-resort, cost-constrained execution bridges. They are not the default implementation path and are not semantic authorities for ChatGPT-Lab.

## Rationale

The experiment is designed to test whether ChatGPT Web, its connectors, GitHub, hosted CI, selected skills, and `$ask` collaboration can handle vague or specific requests without depending on a local coding agent as the project brain.

Local project agents are useful mainly for narrow local execution tasks that ChatGPT Web cannot perform directly, such as running a local CLI command, collecting a filesystem receipt, checking a local service, or making a very small bounded bug fix.

They are not reliable enough or cost-effective enough to own architecture, broad implementation, planning, review verdicts, evidence reconciliation, scope decisions, or next-step selection.

## Allowed uses

A local project agent may be used only when one of these is true:

1. ChatGPT Web lacks the connector or runtime access required to collect a necessary proof artifact.
2. A local-only command must be run, such as `gh`, a browser/CDP tool, a repo-local test runner, or a local service probe.
3. A very small, bounded bug fix is needed and the exact file/scope/acceptance check is already defined by ChatGPT Web.
4. A selected skill explicitly requires local execution and ChatGPT Web cannot run it directly.

## Forbidden uses

A local project agent must not:

- decide scope;
- pick the next phase;
- broaden the task;
- invent architecture;
- claim PASS or closure;
- replace a required skill;
- replace `$ask` artifacts with informal prose;
- perform broad implementation without a committed plan;
- mutate unrelated files;
- treat its own summary as evidence.

## Required task contract

Every local-agent task must include:

- objective;
- repo/path scope;
- allowed commands;
- forbidden actions;
- exact files that may be changed, if any;
- expected artifacts or receipts;
- timeout or stop condition;
- acceptance check;
- non-claims.

## Default escalation order

Before using a local project agent, try:

1. ChatGPT Web direct connectors/tools;
2. GitHub source, PR, and Actions flows;
3. hosted CI artifacts;
4. selected repo skills and their documented contracts;
5. `$ask` / WebGPT collaboration with preserved artifacts;
6. local project agent only for the smallest remaining local execution gap.

## Current Monocle Man implication

For the current Monocle Man live-delivery blocker, the only valid local-agent use would be a tiny bounded task such as:

- use `gh` to list the post-merge GitHub Pages workflow run;
- record the deploy-pages `page_url`;
- capture desktop/mobile screenshots from that live URL;
- return raw receipts without making a PASS claim.
