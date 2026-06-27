#!/usr/bin/env python3
"""Validate the active PhatGPT-LAB goal capsule."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from goal_contracts import ROOT, compute_goal_hash, load_json, validate_goal_capsule


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=ROOT / "goals/current.json",
        help="Goal capsule JSON path.",
    )
    parser.add_argument(
        "--print-hash",
        action="store_true",
        help="Print the computed hash instead of a validation receipt.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    try:
        goal = load_json(args.path)
        if args.print_hash:
            print(compute_goal_hash(goal))
            return 0
        errors.extend(validate_goal_capsule(goal))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to read goal capsule: {exc}")

    result = {
        "schema": "chatgpt_lab.goal_capsule_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "path": str(args.path),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
