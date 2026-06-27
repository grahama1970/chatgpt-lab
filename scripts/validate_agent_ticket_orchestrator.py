#!/usr/bin/env python3
"""Validate no-mutation orchestrator dry-run examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ticket_orchestrator import ROOT, github_json_to_thread_fixture, load_json, route_thread


DEFAULT_EXAMPLE_DIR = ROOT / "examples/agent-harness/github-state"


def validate_examples(example_dir: Path, active_goal_path: Path) -> tuple[list[str], list[dict[str, object]]]:
    errors: list[str] = []
    decisions: list[dict[str, object]] = []
    active_goal = load_json(active_goal_path)
    specs = [
        ("pr", "pr-13-gh-view.json", "REFUSED"),
        ("issue", "issue-14-tau-comment-gh-view.json", "ROUTE"),
    ]
    for kind, filename, expected_status in specs:
        path = example_dir / filename
        try:
            data = load_json(path)
            fixture = github_json_to_thread_fixture(kind, data)
            decision = route_thread(fixture, active_goal, {"grahama1970"})
        except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
            errors.append(f"{path}: unable to route fixture: {exc}")
            continue
        if decision.get("status") != expected_status:
            errors.append(f"{path}: expected {expected_status}, got {decision.get('status')}")
        if decision.get("would_mutate") is not False:
            errors.append(f"{path}: decision must be non-mutating")
        orchestrator = decision.get("orchestrator")
        if not isinstance(orchestrator, dict) or orchestrator.get("would_mutate") is not False:
            errors.append(f"{path}: orchestrator marker must be non-mutating")
        decisions.append(
            {
                "path": str(path),
                "kind": kind,
                "status": decision.get("status"),
                "reason": decision.get("reason"),
                "selected_schema": decision.get("source", {}).get("selected_schema")
                if isinstance(decision.get("source"), dict)
                else None,
                "next": decision.get("next"),
            }
        )
    return errors, decisions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLE_DIR)
    parser.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    args = parser.parse_args()

    try:
        errors, decisions = validate_examples(args.examples, args.active_goal)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"unable to read orchestrator examples: {exc}"]
        decisions = []

    result = {
        "schema": "chatgpt_lab.agent_ticket_orchestrator_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "examples": str(args.examples),
        "decisions": decisions,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
