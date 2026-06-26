#!/usr/bin/env python3
"""Write agent-state/last-result.json for the dispatcher workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "agent-state/last-result.json"
NEXT_COMMAND_PATH = ROOT / "agent-state/next-command.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--status", choices=["PASS", "FAILED", "REFUSED"], required=True)
    parser.add_argument("--stdout", default="")
    parser.add_argument("--stderr", default="")
    args = parser.parse_args()

    try:
        command = load_json(NEXT_COMMAND_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"unable to read {NEXT_COMMAND_PATH}: {exc}", file=sys.stderr)
        return 2

    expected_command_id = command.get("command_id") if isinstance(command, dict) else None
    if args.command_id != expected_command_id:
        print("command id does not match next-command.json", file=sys.stderr)
        return 2

    payload = {
        "schema": "chatgpt_lab.workflow_result.v1",
        "command_id": args.command_id,
        "status": args.status,
        "repository": os.environ.get("GITHUB_REPOSITORY", "grahama1970/chatgpt-lab"),
        "workflow": "agent-dispatch.yml",
        "run_id": int(os.environ["GITHUB_RUN_ID"]) if os.environ.get("GITHUB_RUN_ID") else None,
        "run_attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]) if os.environ.get("GITHUB_RUN_ATTEMPT") else None,
        "head_sha": os.environ.get("GITHUB_SHA"),
        "output_path": "agent-state/last-result.json",
        "stdout": args.stdout,
        "stderr": args.stderr,
        "checked_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
