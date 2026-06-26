# Summary

<!-- One sentence describing the bounded change requested by this PR. -->

## Ticket Contract

- Ticket type:
- Target path:
- Current state:
- Requested outcome:
- Route / agent metadata:
- Required proof:
- Non-goals:

## PhatGPT Task Contract

<!--
Required for WebGPT-created PRs. Keep this JSON valid.

The dispatcher refuses PRs without this block. Use "pr": null when this task
block is inside the PR being processed; use an integer only for an explicit
cross-reference.
-->

<!-- phatgpt-task:v1
{
  "schema": "chatgpt_lab.pr_local_task.v1",
  "task_id": "replace-with-short-stable-task-id",
  "command": "validate_only",
  "mode": "read_only",
  "target": {
    "repository": "grahama1970/chatgpt-lab",
    "pr": null,
    "branch": "replace-with-pr-branch",
    "commit": null
  },
  "objective": "State the exact bounded objective.",
  "allowed_commands": [
    "python3 scripts/validate_control_plane.py"
  ],
  "allowed_paths": [
    "README.md",
    "PROJECT_KNOWLEDGE.md",
    "docs/**",
    "iterations/**"
  ],
  "forbidden_paths": [
    ".env",
    "**/.env",
    "**/secrets/**",
    "~/.ssh/**"
  ],
  "validation_commands": [
    "python3 scripts/validate_control_plane.py"
  ],
  "expected_evidence": [
    "PR diff is limited to allowed_paths",
    "validation commands exit 0",
    "reviewer comments PASS, NEEDS_CHANGES, BLOCKED, or INSUFFICIENT_EVIDENCE"
  ],
  "required_outputs": [
    "local-subagent-receipt.json",
    "PR comment with coder/reviewer receipt"
  ],
  "stop_condition": "A reviewer comments a verdict with exact command results, changed files, and remaining blockers.",
  "refusal_conditions": [
    "missing_structured_task_block",
    "task_not_implementation_ready",
    "command_not_allowlisted",
    "path_outside_allowlist",
    "secrets_requested",
    "unsafe_git_operation",
    "unclear_acceptance_criteria",
    "missing_validation_command",
    "missing_expected_evidence",
    "timeout_exceeded",
    "concurrent_lease_exists"
  ]
}
-->
