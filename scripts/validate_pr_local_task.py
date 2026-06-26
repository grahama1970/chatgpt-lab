#!/usr/bin/env python3
"""Validate a PhatGPT-LAB PR local task block and optional receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASK_SCHEMA = "chatgpt_lab.pr_local_task.v1"
RECEIPT_SCHEMA = "chatgpt_lab.local_subagent_receipt.v1"
TASK_MODES = {"read_only", "evidence_collection", "bounded_execution"}
RECEIPT_STATUSES = {"REFUSED", "COMPLETED", "FAILED"}
REQUIRED_REFUSALS = {
    "missing_structured_task_block",
    "task_not_implementation_ready",
    "command_not_allowlisted",
    "path_outside_allowlist",
    "secrets_requested",
    "unsafe_git_operation",
    "unclear_acceptance_criteria",
    "missing_validation_command",
    "missing_expected_evidence",
    "timeout_exceeded",
    "concurrent_lease_exists",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_task(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["task must be an object"]

    required = [
        "schema",
        "task_id",
        "mode",
        "target",
        "objective",
        "allowed_commands",
        "allowed_paths",
        "forbidden_paths",
        "validation_commands",
        "expected_evidence",
        "required_outputs",
        "stop_condition",
        "refusal_conditions",
    ]
    for key in required:
        if key not in data:
            errors.append(f"task missing required field: {key}")

    if data.get("schema") != TASK_SCHEMA:
        errors.append(f"task.schema must be {TASK_SCHEMA}")
    if data.get("mode") not in TASK_MODES:
        errors.append(f"task.mode must be one of {sorted(TASK_MODES)}")
    for key in ["task_id", "objective", "stop_condition"]:
        if not nonempty_string(data.get(key)):
            errors.append(f"task.{key} must be a non-empty string")

    for key in [
        "allowed_commands",
        "allowed_paths",
        "forbidden_paths",
        "validation_commands",
        "expected_evidence",
        "required_outputs",
        "refusal_conditions",
    ]:
        value = data.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"task.{key} must be a non-empty array")

    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("task.target must be an object")
    else:
        if target.get("repository") != "grahama1970/chatgpt-lab":
            errors.append("task.target.repository must be grahama1970/chatgpt-lab")
        if not isinstance(target.get("pr"), int) or target.get("pr") < 1:
            errors.append("task.target.pr must be a positive integer")
        if not nonempty_string(target.get("branch")):
            errors.append("task.target.branch must be a non-empty string")
        commit = target.get("commit")
        if commit is not None and not nonempty_string(commit):
            errors.append("task.target.commit must be a non-empty string or null")

    forbidden = set(data.get("forbidden_paths") or [])
    if ".env" not in forbidden or "**/.env" not in forbidden:
        errors.append("task.forbidden_paths must include .env and **/.env")

    refusals = set(data.get("refusal_conditions") or [])
    missing_refusals = sorted(REQUIRED_REFUSALS.difference(refusals))
    if missing_refusals:
        errors.append(
            "task.refusal_conditions missing required values: "
            + ", ".join(missing_refusals)
        )

    if not any(str(command).startswith("python3 scripts/validate_control_plane.py") for command in data.get("validation_commands") or []):
        errors.append("task.validation_commands must include python3 scripts/validate_control_plane.py")
    if "local-subagent-receipt.json" not in (data.get("required_outputs") or []):
        errors.append("task.required_outputs must include local-subagent-receipt.json")

    return errors


def validate_receipt(data: Any, task_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["receipt must be an object"]
    required = [
        "schema",
        "task_id",
        "status",
        "commands_run",
        "files_touched",
        "artifacts",
        "started_at",
        "completed_at",
    ]
    for key in required:
        if key not in data:
            errors.append(f"receipt missing required field: {key}")
    if data.get("schema") != RECEIPT_SCHEMA:
        errors.append(f"receipt.schema must be {RECEIPT_SCHEMA}")
    if "role" in data and data.get("role") not in {"coder", "reviewer", "researcher"}:
        errors.append("receipt.role must be coder, reviewer, or researcher when present")
    if data.get("status") not in RECEIPT_STATUSES:
        errors.append(f"receipt.status must be one of {sorted(RECEIPT_STATUSES)}")
    if task_id is not None and data.get("task_id") != task_id:
        errors.append("receipt.task_id must match task.task_id")
    for key in ["commands_run", "files_touched", "artifacts"]:
        if not isinstance(data.get(key), list):
            errors.append(f"receipt.{key} must be an array")
    if data.get("status") == "REFUSED":
        if not nonempty_string(data.get("reason")):
            errors.append("REFUSED receipt requires reason")
        if not isinstance(data.get("missing", []), list):
            errors.append("REFUSED receipt missing must be an array when present")
        if not nonempty_string(data.get("next_required_action")):
            errors.append("REFUSED receipt requires next_required_action")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_json", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        task = load_json(args.task_json)
        errors.extend(validate_task(task))
        if args.receipt:
            receipt = load_json(args.receipt)
            task_id = task.get("task_id") if isinstance(task, dict) else None
            errors.extend(validate_receipt(receipt, task_id))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to read JSON: {exc}")

    result = {
        "schema": "chatgpt_lab.pr_local_task_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
