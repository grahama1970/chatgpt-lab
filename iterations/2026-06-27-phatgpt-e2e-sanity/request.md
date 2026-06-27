# PhatGPT E2E Sanity Task

This is a disposable live sanity task for the PhatGPT-LAB multi-agent loop.

The intended lane sequence is:

1. Coder applies exactly one allowlisted text patch.
2. Reviewer validates the live PR branch read-only.
3. Deployer evaluates release gates in dry-run mode.
4. Reviewer reviews the deployer receipt.

The PR must not be merged as part of the sanity check.

During the sanity run, the local artifact check exposed a receipt-collision bug:
coder and reviewer lanes wrote the same `local-subagent-receipt.json` path. The
bugfix preserves role-specific receipts and keeps the legacy latest receipt path
as a compatibility alias.
