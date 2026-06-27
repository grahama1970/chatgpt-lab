#!/usr/bin/env python3
"""Validate dry-run route fixtures for the goal-locked harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ticket_route import ROOT, load_json, route_fixture

DEFAULT_FIXTURE_DIR = ROOT / "examples/agent-harness/fixtures"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURE_DIR)
    parser.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    parser.add_argument("--trusted-human", action="append", default=["grahama1970"])
    args = parser.parse_args()

    errors: list[str] = []
    decisions: list[dict[str, object]] = []
    try:
        active_goal = load_json(args.active_goal)
        fixture_paths = sorted(args.fixtures.glob("*.json"))
        if not fixture_paths:
            errors.append(f"no route fixtures found under {args.fixtures}")
        for path in fixture_paths:
            fixture = load_json(path)
            decision = route_fixture(fixture, active_goal, set(args.trusted_human))
            decisions.append(
                {
                    "fixture": str(path),
                    "status": decision.get("status"),
                    "reason": decision.get("reason"),
                    "selected_schema": decision.get("source", {}).get("selected_schema")
                    if isinstance(decision.get("source"), dict)
                    else None,
                }
            )
            expected_status = fixture.get("expected_decision", {}).get("status")
            expected_reason = fixture.get("expected_decision", {}).get("reason")
            expected_subagent = fixture.get("expected_decision", {}).get("next_subagent")
            if expected_status and decision.get("status") != expected_status:
                errors.append(f"{path}: expected status {expected_status}, got {decision.get('status')}")
            if expected_reason and decision.get("reason") != expected_reason:
                errors.append(f"{path}: expected reason {expected_reason}, got {decision.get('reason')}")
            next_block = decision.get("next")
            actual_subagent = next_block.get("subagent") if isinstance(next_block, dict) else None
            if expected_subagent and actual_subagent != expected_subagent:
                errors.append(f"{path}: expected next subagent {expected_subagent}, got {actual_subagent}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to validate route fixtures: {exc}")

    result = {
        "schema": "chatgpt_lab.agent_ticket_route_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "fixtures": str(args.fixtures),
        "decisions": decisions,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
