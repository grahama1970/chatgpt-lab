#!/usr/bin/env python3
"""Validate Slice 001 WebGPT local-subagent request and receipt examples.

This is a schema/stub validator only. It does not implement a live bridge and
does not execute requested commands.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUEST_SCHEMA = "chatgpt_lab.webgpt_local_task_request.v1"
RECEIPT_SCHEMA = "chatgpt_lab.local_subagent_receipt.v1"
REQUEST_MODES = {"read_only", "artifacts_only"}
RECEIPT_STATUSES = {"REFUSED", "COMPLETED", "FAILED"}


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_request(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["request must be an object"]
    required = [
        "schema",
        "task_id",
        "requested_by",
        "objective",
        "mode",
        "target",
        "allowed_commands",
        "allowed_paths",
        "forbidden_paths",
        "timeout_seconds",
        "network_policy",
        "write_policy",
        "required_outputs",
        "refusal_conditions",
    ]
    for key in required:
        if key not in data:
            errors.append(f"request missing required field: {key}")
    if data.get("schema") != REQUEST_SCHEMA:
        errors.append(f"request.schema must be {REQUEST_SCHEMA}")
    if data.get("requested_by") != "webgpt":
        errors.append("request.requested_by must be webgpt")
    if data.get("mode") not in REQUEST_MODES:
        errors.append(f"request.mode must be one of {sorted(REQUEST_MODES)}")
    if not isinstance(data.get("timeout_seconds"), int) or data.get("timeout_seconds") <= 0:
        errors.append("request.timeout_seconds must be a positive integer")
    for array_key in ["allowed_commands", "allowed_paths", "forbidden_paths", "required_outputs", "refusal_conditions"]:
        if not isinstance(data.get(array_key), list):
            errors.append(f"request.{array_key} must be an array")
    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("request.target must be an object")
    else:
        for key in ["repository", "branch", "path", "commit"]:
            if key not in target:
                errors.append(f"request.target missing required field: {key}")
        if target.get("repository") != "grahama1970/snippets":
            errors.append("request.target.repository must be grahama1970/snippets for Slice 001")
        if target.get("path") != "monocle-man-site/":
            errors.append("request.target.path must be monocle-man-site/")
    forbidden = data.get("forbidden_paths") if isinstance(data.get("forbidden_paths"), list) else []
    if ".env" not in forbidden or "**/.env" not in forbidden:
        errors.append("request.forbidden_paths must include .env and **/.env")
    if "target_commit_missing" not in (data.get("refusal_conditions") or []):
        errors.append("request.refusal_conditions must include target_commit_missing")
    return errors


def validate_receipt(data: Any, request_task_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["receipt must be an object"]
    required = ["schema", "task_id", "status", "commands_run", "files_touched", "artifacts", "started_at", "completed_at"]
    for key in required:
        if key not in data:
            errors.append(f"receipt missing required field: {key}")
    if data.get("schema") != RECEIPT_SCHEMA:
        errors.append(f"receipt.schema must be {RECEIPT_SCHEMA}")
    if data.get("status") not in RECEIPT_STATUSES:
        errors.append(f"receipt.status must be one of {sorted(RECEIPT_STATUSES)}")
    for array_key in ["commands_run", "files_touched", "artifacts"]:
        if not isinstance(data.get(array_key), list):
            errors.append(f"receipt.{array_key} must be an array")
    if request_task_id is not None and data.get("task_id") != request_task_id:
        errors.append("receipt.task_id must match request.task_id")
    if data.get("status") == "REFUSED" and not nonempty_string(data.get("reason")):
        errors.append("REFUSED receipt requires a non-empty reason")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_json", type=Path)
    parser.add_argument("receipt_json", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        request = load(args.request_json)
        receipt = load(args.receipt_json)
        errors.extend(validate_request(request))
        task_id = request.get("task_id") if isinstance(request, dict) else None
        errors.extend(validate_receipt(receipt, task_id))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to read JSON: {exc}")

    result = {
        "schema": "chatgpt_lab.local_subagent_contract_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
