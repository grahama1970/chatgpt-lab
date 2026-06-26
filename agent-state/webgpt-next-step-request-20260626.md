# WebGPT next-step assessment request

## Binding

- desktop: 2
- tab id: 837356639
- url: https://chatgpt.com/g/g-p-6a3d31b5776881919971d047e485b54a/c/6a3d8913-3eec-83ea-92cb-34e4c5a0dfc2

## Repository

- repo: grahama1970/chatgpt-lab
- branch: main
- latest control-plane report commit: d5b99899a760a2d481704dcb6a66518de86946fc

## Current state

- WebGPT file-write bridge is proven narrow.
- apply-text-patch-proof-001 is recorded.
- Result commit: 064f5fd5b2b52bd1874c205edaeb616f7eae0533
- Source Check: 28245666829
- Benchmark: 28245666824
- Pages proof: 28245666963
- Latest reporting/status commit: d5b99899a760a2d481704dcb6a66518de86946fc
- Post-report Source Check: 28247017860

## Read these files first

- README.md
- PROJECT_KNOWLEDGE.md
- sources/control-plane/CURRENT_STATE.md
- docs/reports/PROJECT_GOALS_STATUS_2026-06-26.md
- iterations/2026-06-26-apply-text-patch-proof/iteration.json
- agent-state/current.json
- agent-state/next-command.json
- agent-state/last-result.json

## Task

Assess the next smallest bounded step toward ChatGPT/WebGPT project ownership.

Do not design the whole system. Do not claim the project is ready. Do not make broad architecture prose.

Return one of these:

1. a concrete next WebGPT GitHub file-write command for `agent-state/next-command.json`, or
2. a short blocker report explaining why no command should be written yet.

## Preferred next candidates

- classify the three third-party `youtube-nocookie.com` telemetry aborts in the proof contract;
- create a bounded code-review/design-review receipt request;
- implement Slice 002 dry-run local-subagent refusal/receipt path;
- formalize post-executor follow-on dispatch so Source Check/Benchmark/Pages proof are not manually triggered.

## Acceptance bar

- identify exact files you would change;
- identify exact validation command expected afterward;
- preserve fail-closed language;
- do not request arbitrary shell execution;
- do not edit unrelated files.

## Local binding command for the execution environment

```bash
python /home/graham/workspace/experiments/agent-skills/skills/webgpt/scripts/webgpt_cli.py config --tab-id 837356639 --url "https://chatgpt.com/g/g-p-6a3d31b5776881919971d047e485b54a/c/6a3d8913-3eec-83ea-92cb-34e4c5a0dfc2" --kde-desktop 2
```
