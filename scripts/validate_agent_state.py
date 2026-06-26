#!/usr/bin/env python3
"""Validate ChatGPT-Lab agent-state files for the dispatcher proof."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENT_STATE_SCHEMA = "chatgpt_lab.agent_state.v1"
SKILL_ROUTER_SCHEMA = "chatgpt_lab.skill_router.v1"
NEXT_COMMAND_SCHEMA = "chatgpt_lab.next_command.v1"
WORKFLOW_RESULT_SCHEMA = "chatgpt_lab.workflow_result.v1"
TARGET_REPOSITORY = "grahama1970/chatgpt-lab"
DISPATCH_WORKFLOW = "agent-dispatch.yml"
NEXT_COMMAND_PATH = "agent-state/next-command.json"
LAST_RESULT_PATH = "agent-state/last-result.json"
ALLOWED_COMMANDS = {"echo_hello", "validate_control_plane"}
RESULT_STATUSES = {"NOT_RUN", "PASS", "FAILED", "REFUSED"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_object(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return {}
    return value


def validate_current(data: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "current", errors)
    if errors:
        return errors
    required = [
        "schema",
        "project",
        "repository",
        "branch",
        "phase",
        "controller",
        "executor",
        "next_command_path",
        "last_result_path",
        "skill_router_path",
        "updated_at",
    ]
    for key in required:
        if key not in root:
            errors.append(f"current missing required field: {key}")
    if root.get("schema") != AGENT_STATE_SCHEMA:
        errors.append(f"current.schema must be {AGENT_STATE_SCHEMA}")
    if root.get("repository") != TARGET_REPOSITORY:
        errors.append(f"current.repository must be {TARGET_REPOSITORY}")
    if root.get("next_command_path") != NEXT_COMMAND_PATH:
        errors.append(f"current.next_command_path must be {NEXT_COMMAND_PATH}")
    if root.get("last_result_path") != LAST_RESULT_PATH:
        errors.append(f"current.last_result_path must be {LAST_RESULT_PATH}")
    for key in ["project", "branch", "phase", "controller", "executor", "skill_router_path", "updated_at"]:
        if not is_nonempty_string(root.get(key)):
            errors.append(f"current.{key} must be a non-empty string")
    return errors


def validate_skill_router(data: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "skill_router", errors)
    if errors:
        return errors
    if root.get("schema") != SKILL_ROUTER_SCHEMA:
        errors.append(f"skill_router.schema must be {SKILL_ROUTER_SCHEMA}")
    if not isinstance(root.get("default_chain"), list) or not root.get("default_chain"):
        errors.append("skill_router.default_chain must be a non-empty array")
    routes = root.get("routes")
    if not isinstance(routes, list) or not routes:
        errors.append("skill_router.routes must be a non-empty array")
    else:
        for index, route in enumerate(routes):
            item = require_object(route, f"skill_router.routes[{index}]", errors)
            if not item:
                continue
            for key in ["intent", "authority"]:
                if not is_nonempty_string(item.get(key)):
                    errors.append(f"skill_router.routes[{index}].{key} must be a non-empty string")
            if not isinstance(item.get("skills"), list) or not item.get("skills"):
                errors.append(f"skill_router.routes[{index}].skills must be a non-empty array")
    if not is_nonempty_string(root.get("updated_at")):
        errors.append("skill_router.updated_at must be a non-empty string")
    return errors


def validate_next_command(data: Any, expected_command_id: str | None = None) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "next_command", errors)
    if errors:
        return errors
    required = [
        "schema",
        "command_id",
        "command",
        "target_repo",
        "target_ref",
        "workflow",
        "state_path",
        "objective",
        "allowed_outputs",
        "stop_condition",
    ]
    for key in required:
        if key not in root:
            errors.append(f"next_command missing required field: {key}")
    if root.get("schema") != NEXT_COMMAND_SCHEMA:
        errors.append(f"next_command.schema must be {NEXT_COMMAND_SCHEMA}")
    if not is_nonempty_string(root.get("command_id")):
        errors.append("next_command.command_id must be a non-empty string")
    elif expected_command_id and root.get("command_id") != expected_command_id:
        errors.append("next_command.command_id must match workflow input command_id")
    if root.get("command") not in ALLOWED_COMMANDS:
        errors.append(f"next_command.command must be one of {sorted(ALLOWED_COMMANDS)}")
    if root.get("target_repo") != TARGET_REPOSITORY:
        errors.append(f"next_command.target_repo must be {TARGET_REPOSITORY}")
    if not is_nonempty_string(root.get("target_ref")):
        errors.append("next_command.target_ref must be a non-empty string")
    if root.get("workflow") != DISPATCH_WORKFLOW:
        errors.append(f"next_command.workflow must be {DISPATCH_WORKFLOW}")
    if root.get("state_path") != NEXT_COMMAND_PATH:
        errors.append(f"next_command.state_path must be {NEXT_COMMAND_PATH}")
    if not is_nonempty_string(root.get("objective")):
        errors.append("next_command.objective must be a non-empty string")
    allowed_outputs = root.get("allowed_outputs")
    if not isinstance(allowed_outputs, list):
        errors.append("next_command.allowed_outputs must be an array")
    elif LAST_RESULT_PATH not in allowed_outputs:
        errors.append(f"next_command.allowed_outputs must include {LAST_RESULT_PATH}")
    if not is_nonempty_string(root.get("stop_condition")):
        errors.append("next_command.stop_condition must be a non-empty string")
    return errors


def validate_result(data: Any, expected_command_id: str | None = None) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "workflow_result", errors)
    if errors:
        return errors
    required = [
        "schema",
        "command_id",
        "status",
        "repository",
        "workflow",
        "run_id",
        "run_attempt",
        "head_sha",
        "output_path",
        "stdout",
        "stderr",
        "checked_at",
    ]
    for key in required:
        if key not in root:
            errors.append(f"workflow_result missing required field: {key}")
    if root.get("schema") != WORKFLOW_RESULT_SCHEMA:
        errors.append(f"workflow_result.schema must be {WORKFLOW_RESULT_SCHEMA}")
    if not is_nonempty_string(root.get("command_id")):
        errors.append("workflow_result.command_id must be a non-empty string")
    elif expected_command_id and root.get("command_id") != expected_command_id:
        errors.append("workflow_result.command_id must match next_command.command_id")
    if root.get("status") not in RESULT_STATUSES:
        errors.append(f"workflow_result.status must be one of {sorted(RESULT_STATUSES)}")
    if root.get("repository") != TARGET_REPOSITORY:
        errors.append(f"workflow_result.repository must be {TARGET_REPOSITORY}")
    if root.get("workflow") != DISPATCH_WORKFLOW:
        errors.append(f"workflow_result.workflow must be {DISPATCH_WORKFLOW}")
    if root.get("output_path") != LAST_RESULT_PATH:
        errors.append(f"workflow_result.output_path must be {LAST_RESULT_PATH}")
    if not isinstance(root.get("stdout"), str):
        errors.append("workflow_result.stdout must be a string")
    if not isinstance(root.get("stderr"), str):
        errors.append("workflow_result.stderr must be a string")
    if root.get("status") != "NOT_RUN":
        if not isinstance(root.get("run_id"), int):
            errors.append("workflow_result.run_id must be an integer after execution")
        if not isinstance(root.get("run_attempt"), int):
            errors.append("workflow_result.run_attempt must be an integer after execution")
        if not is_nonempty_string(root.get("head_sha")):
            errors.append("workflow_result.head_sha must be a non-empty string after execution")
        if not is_nonempty_string(root.get("checked_at")):
            errors.append("workflow_result.checked_at must be a non-empty string after execution")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--command-id")
    parser.add_argument("--skip-result", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    errors: list[str] = []
    try:
        current = load_json(root / "agent-state/current.json")
        skill_router = load_json(root / "agent-state/skill-router.json")
        next_command = load_json(root / NEXT_COMMAND_PATH)
        errors.extend(validate_current(current))
        errors.extend(validate_skill_router(skill_router))
        errors.extend(validate_next_command(next_command, args.command_id))
        if not args.skip_result:
            result = load_json(root / LAST_RESULT_PATH)
            errors.extend(validate_result(result, args.command_id))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to read agent-state JSON: {exc}")

    result_payload = {
        "schema": "chatgpt_lab.agent_state_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "root": str(root),
        "errors": errors,
    }
    print(json.dumps(result_payload, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
