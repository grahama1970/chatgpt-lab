# Active queue policy

`queue-state/current.json` is the controller-facing snapshot of open GitHub work.

It does not close issues or pull requests. It classifies them for review so WebGPT does not confuse historical or superseded work with the next active task.

## Rules

1. The queue state must preserve the active goal id, version, and hash.
2. Active items are candidates for the next WebGPT task.
3. Stale or superseded items require reviewer or human approval before destructive cleanup.
4. A PR or issue classified as superseded must include a reason and a recommended action.
5. WebGPT must treat stale queue entries as `INSUFFICIENT_EVIDENCE` for new work until a reviewer or human confirms the classification.

## Validation

Run:

```bash
python3 scripts/validate_queue_state.py
python3 scripts/validate_control_plane.py
```
