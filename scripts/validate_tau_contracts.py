#!/usr/bin/env python3
"""Validate compact Tau agent-facing contract examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from goal_contracts import ROOT, load_json, validate_goal_capsule
from tau_contracts import validate_tau_contract

DEFAULT_EXAMPLE_DIR = ROOT / "examples/agent-harness/tau"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLE_DIR)
    parser.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    args = parser.parse_args()

    errors: list[str] = []
    decisions: list[dict[str, object]] = []
    try:
        active_goal = load_json(args.active_goal)
        errors.extend(validate_goal_capsule(active_goal))
        paths = sorted(args.examples.glob("*.json"))
        if not paths:
            errors.append(f"no Tau examples found under {args.examples}")
        for path in paths:
            data = load_json(path)
            contract_errors, decision = validate_tau_contract(data, active_goal, trusted_human="grahama1970")
            for error in contract_errors:
                errors.append(f"{path}: {error}")
            decisions.append(
                {
                    "path": str(path),
                    "schema": data.get("schema") if isinstance(data, dict) else None,
                    "status": decision.get("status") if isinstance(decision, dict) else None,
                    "next": decision.get("next") if isinstance(decision, dict) else None,
                }
            )
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to validate Tau examples: {exc}")

    result = {
        "schema": "chatgpt_lab.tau_contract_examples_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "examples": str(args.examples),
        "decisions": decisions,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
