#!/usr/bin/env python3
"""Validate PhatGPT-LAB goal-locked ticket contract examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from goal_contracts import (
    ROOT,
    load_json,
    validate_agent_handoff,
    validate_generated_ticket,
    validate_goal_capsule,
    validate_human_interjection,
)


DEFAULT_EXAMPLE_DIR = ROOT / "examples/agent-harness"


def validate_examples(example_dir: Path, active_goal_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        active_goal = load_json(active_goal_path)
        errors.extend(validate_goal_capsule(active_goal))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unable to read active goal: {exc}"]

    example_specs = [
        ("agent-handoff.valid.json", validate_agent_handoff),
        ("human-interjection.pause.valid.json", validate_human_interjection),
        ("generated-ticket.valid.json", validate_generated_ticket),
    ]
    for filename, validator in example_specs:
        path = example_dir / filename
        try:
            data = load_json(path)
            for error in validator(data, active_goal):
                errors.append(f"{path}: {error}")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: unable to read JSON: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLE_DIR)
    parser.add_argument("--goal", type=Path, default=ROOT / "goals/current.json")
    args = parser.parse_args()

    errors = validate_examples(args.examples, args.goal)
    result = {
        "schema": "chatgpt_lab.agent_ticket_contract_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "examples": str(args.examples),
        "goal": str(args.goal),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
