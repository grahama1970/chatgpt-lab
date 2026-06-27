# PhatGPT Local Watchdog

The local watchdog is the pickup mechanism that lets ChatGPT Pro/WebGPT remain
the control surface while local subagents perform bounded local work.

The control split is:

- GitHub issues, PRs, comments, labels, receipts, and artifacts are the durable
  queue and audit log.
- ChatGPT Pro/WebGPT creates bounded GitHub-visible work packets.
- The watchdog runs locally, selects one eligible lane, delegates to the
  matching subagent worker, writes a receipt, and exits.
- `/home/graham/workspace/experiments/agent-skills/agents` is the authoritative
  subagent registry.
- `$memory` recall is advisory. It may answer "for task X, which subagent should
  we choose?", but the selector must validate that suggestion against the live
  agent registry before executing anything.

## Selector

Inspect available lanes:

```bash
python3 scripts/phatgpt_subagent_selector.py --json
```

Ask memory for an advisory task-to-subagent suggestion while still validating
against the live registry:

```bash
python3 scripts/phatgpt_subagent_selector.py \
  --with-memory \
  --task "Review a PR that claims queue-state cleanup is ready" \
  --json
```

The selector also has a deterministic task-text recommender. It returns:

- `phatgpt-coder` for bounded code/file mutation language.
- `phatgpt-reviewer` for read-only validation/review language.
- `phatgpt-deployer` for release, merge, or deploy-gate language.
- `phatgpt-researcher` when the task is vague or mixes multiple roles.

Mixed-role examples such as "implement and review" or "validate deployment
proof" intentionally route to `phatgpt-researcher` so the task can be split or
refused instead of guessing.

The selector maps live contracts to executable lanes. The watchdog does not
blindly process the newest GitHub item. It scans the `grahama1970/chatgpt-lab`
queue for lane labels, skips targets listed as stale or superseded in
`queue-state/current.json`, skips targets carrying active/lease labels, skips
targets with assignees, and then runs the highest-priority eligible lane.

| Agent contract | Label | Target | Worker |
| --- | --- | --- | --- |
| `phatgpt-deployer` | `phatgpt-ready-to-deploy` | PR | `scripts/phatgpt_deployer_cycle.py` |
| `phatgpt-reviewer` | `phatgpt-ready-for-review` | PR | `scripts/phatgpt_local_worker_cycle.py --role reviewer` |
| `phatgpt-coder` | `phatgpt-local-agent` | PR | `scripts/phatgpt_local_worker_cycle.py --role coder` |
| `phatgpt-researcher` | `phatgpt-needs-task` | issue, then PR | `scripts/phatgpt_local_worker_cycle.py --role researcher` |

## Watchdog

Dry-run one selection:

```bash
python3 scripts/phatgpt_watchdog_cycle.py --dry-run
```

Run one real bounded cycle:

```bash
./scripts/run_phatgpt_watchdog.sh
```

Install the cron entry:

```bash
./scripts/install_phatgpt_watchdog_cron.sh
```

The installed job runs every five minutes and appends to:

```text
artifacts/watchdog/cron.log
```

Each watchdog run writes:

```text
artifacts/watchdog/latest.json
artifacts/watchdog/watchdog-<timestamp>.json
```

## Fail-Closed Rules

- If no live subagent contracts are found, the watchdog refuses.
- If no eligible GitHub label is found, the watchdog writes `NOOP`.
- If a target is already assigned or marked active, the watchdog skips it.
- If a target is listed in `queue-state/current.json` as stale or superseded,
  the watchdog skips it.
- If `$memory` is unavailable, selector output remains valid with
  `memory.status: UNAVAILABLE`.
- If `$memory` suggests a subagent not present in the live registry, the
  suggestion is advisory only and must not be executed.
- If task language maps to more than one non-research role, the selector routes
  to `phatgpt-researcher` for task splitting or refusal.
- The watchdog processes at most one target per run.
