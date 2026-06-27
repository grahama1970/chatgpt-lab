#!/usr/bin/env python3
"""Select and run one PhatGPT-LAB local worker lane.

This is the cron/watchdog entrypoint for the ChatGPT Pro control-surface model.
It does not interpret model prose. It looks for GitHub-visible labels, selects
one bounded lane, delegates to the existing role-specific worker, records a
watchdog receipt, and exits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from phatgpt_subagent_selector import DEFAULT_AGENT_ROOT, build_lanes

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "watchdog"
DEFAULT_REPO = "grahama1970/chatgpt-lab"
QUEUE_STATE_PATH = ROOT / "queue-state" / "current.json"
ACTIVE_LABELS = {"maintainer-active", "agent-active", "phatgpt-deploying"}

def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout, result.stderr


def command_record(args: list[str], exit_code: int, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    record: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": exit_code,
    }
    if stdout.strip():
        record["stdout"] = stdout.strip()
    if stderr.strip():
        record["stderr"] = stderr.strip()
    return record


def load_stale_targets(path: Path = QUEUE_STATE_PATH) -> set[tuple[str, int]]:
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    stale: set[tuple[str, int]] = set()
    for item in data.get("stale_or_superseded_items") or []:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        number = item.get("number")
        if kind == "pull_request":
            kind = "pr"
        if kind in {"pr", "issue"} and isinstance(number, int):
            stale.add((kind, number))
    return stale


def labels_from_item(item: dict[str, Any]) -> set[str]:
    labels = item.get("labels") or []
    return {
        label["name"]
        for label in labels
        if isinstance(label, dict) and isinstance(label.get("name"), str)
    }


def has_assignee(item: dict[str, Any]) -> bool:
    assignees = item.get("assignees") or []
    return bool(assignees)


def target_is_available(kind: str, number: int, item: dict[str, Any], excluded: set[tuple[str, int]]) -> bool:
    if (kind, number) in excluded:
        return False
    if ACTIVE_LABELS.intersection(labels_from_item(item)):
        return False
    if has_assignee(item):
        return False
    return True


def discover(repo: str, kind: str, label: str, excluded: set[tuple[str, int]]) -> tuple[int | None, dict[str, Any]]:
    base = ["gh", "pr" if kind == "pr" else "issue", "list"]
    args = [
        *base,
        "--repo",
        repo,
        "--state",
        "open",
        "--label",
        label,
        "--limit",
        "20",
        "--json",
        "number,title,url,labels,assignees",
    ]
    exit_code, stdout, stderr = run_command(args)
    record = command_record(args, exit_code, stdout, stderr)
    if exit_code != 0:
        return None, record
    try:
        items = json.loads(stdout)
    except json.JSONDecodeError as exc:
        record["stderr"] = f"invalid gh JSON: {exc}"
        return None, record
    if not isinstance(items, list) or not items:
        return None, record
    for item in items:
        number = item.get("number") if isinstance(item, dict) else None
        if isinstance(number, int) and target_is_available(kind, number, item, excluded):
            return number, record
    record["stdout"] = json.dumps(
        {
            "eligible_count": len(items),
            "active_labels": sorted(ACTIVE_LABELS),
            "excluded": sorted(f"{target_kind}#{number}" for target_kind, number in excluded),
            "result": "all_matching_targets_excluded_by_queue_state_or_active_assignment",
        },
        sort_keys=True,
    )
    return None, record


def format_command(template: list[str], repo: str, label: str) -> list[str]:
    return [part.format(repo=repo, label=label) for part in template]


def write_receipt(
    *,
    status: str,
    selected_lane: dict[str, Any] | None,
    target_number: int | None,
    commands_run: list[dict[str, Any]],
    reason: str,
    dry_run: bool,
) -> Path:
    completed_at = now()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    latest_path = ARTIFACT_ROOT / "latest.json"
    stamped_path = ARTIFACT_ROOT / f"watchdog-{completed_at.replace(':', '').replace('-', '')}.json"
    receipt = {
        "schema": "chatgpt_lab.phatgpt_watchdog_receipt.v1",
        "status": status,
        "reason": reason,
        "dry_run": dry_run,
        "selected_lane": selected_lane,
        "target_number": target_number,
        "commands_run": commands_run,
        "started_at": completed_at,
        "completed_at": completed_at,
    }
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    latest_path.write_text(payload, encoding="utf-8")
    stamped_path.write_text(payload, encoding="utf-8")
    return latest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--agent-root", type=Path, default=Path(os.environ.get("PHATGPT_AGENT_ROOT", DEFAULT_AGENT_ROOT)))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-targets", type=int, default=1)
    args = parser.parse_args()

    if args.max_targets != 1:
        print("watchdog supports exactly --max-targets 1", file=sys.stderr)
        return 2

    commands_run: list[dict[str, Any]] = []
    excluded = load_stale_targets()
    lanes = build_lanes(args.agent_root)
    if not lanes:
        receipt = write_receipt(
            status="REFUSED",
            selected_lane=None,
            target_number=None,
            commands_run=[],
            reason="no_subagent_contracts_found",
            dry_run=args.dry_run,
        )
        print(json.dumps({"status": "REFUSED", "reason": "no_subagent_contracts_found", "receipt": str(receipt)}, indent=2))
        return 1

    for lane in lanes:
        number, record = discover(args.repo, lane["kind"], lane["label"], excluded)
        commands_run.append(record)
        if number is None:
            continue

        selected = {
            "name": lane["name"],
            "role": lane.get("role", lane["name"]),
            "kind": lane["kind"],
            "label": lane["label"],
        }
        command = format_command(lane["command"], args.repo, lane["label"])
        if args.dry_run:
            commands_run.append(command_record(command, 0, stdout="dry-run: command not executed"))
            receipt = write_receipt(
                status="WOULD_RUN",
                selected_lane=selected,
                target_number=number,
                commands_run=commands_run,
                reason="eligible_target_found",
                dry_run=True,
            )
            print(json.dumps({"status": "WOULD_RUN", "lane": selected, "target_number": number, "receipt": str(receipt)}, indent=2))
            return 0

        exit_code, stdout, stderr = run_command(command)
        commands_run.append(command_record(command, exit_code, stdout, stderr))
        status = "COMPLETED" if exit_code == 0 else "FAILED"
        receipt = write_receipt(
            status=status,
            selected_lane=selected,
            target_number=number,
            commands_run=commands_run,
            reason="worker_exit_zero" if exit_code == 0 else "worker_exit_nonzero",
            dry_run=False,
        )
        print(json.dumps({"status": status, "lane": selected, "target_number": number, "receipt": str(receipt)}, indent=2))
        return exit_code

    receipt = write_receipt(
        status="NOOP",
        selected_lane=None,
        target_number=None,
        commands_run=commands_run,
        reason="no_eligible_targets",
        dry_run=args.dry_run,
    )
    print(json.dumps({"status": "NOOP", "reason": "no_eligible_targets", "receipt": str(receipt)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
