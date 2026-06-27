#!/usr/bin/env python3
"""Compact Tau authoring contract validators and normalizers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from goal_contracts import ALLOWED_EXECUTORS, ALLOWED_SUBAGENTS, ROOT, load_json, nonempty_string, validate_goal_capsule

TAU_AGENT_HANDOFF_SCHEMA = "tau.agent_handoff.v1"
TAU_GENERATED_TICKET_SCHEMA = "tau.generated_ticket.v1"
TAU_HUMAN_GOAL_CHANGE_SCHEMA = "tau.human_goal_change.v1"
DEFAULT_EXECUTOR = "either"
TRUSTED_HUMANS = {"grahama1970", "human"}


def _require(data: dict[str, Any], required: list[str], prefix: str) -> list[str]:
    return [f"{prefix} missing required field: {key}" for key in required if key not in data]


def _validate_goal_ref(data: Any, active_goal: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    errors.extend(_require(data, ["goal_id", "goal_version", "goal_hash"], prefix))
    if data.get("goal_id") != active_goal.get("goal_id"):
        errors.append(f"{prefix}.goal_id must match active goal")
    if data.get("goal_version") != active_goal.get("version"):
        errors.append(f"{prefix}.goal_version must match active goal version")
    if data.get("goal_hash") != active_goal.get("goal_hash"):
        errors.append(f"{prefix}.goal_hash must match active goal hash")
    return errors


def _validate_next_agent(data: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    errors.extend(_require(data, ["name", "reason"], prefix))
    if data.get("name") not in ALLOWED_SUBAGENTS:
        errors.append(f"{prefix}.name must be a recognized agent")
    executor = data.get("executor", DEFAULT_EXECUTOR)
    if executor not in ALLOWED_EXECUTORS:
        errors.append(f"{prefix}.executor must be recognized when present")
    if not nonempty_string(data.get("reason")):
        errors.append(f"{prefix}.reason must be a non-empty string")
    return errors


def _validate_string_array(data: Any, prefix: str, *, min_items: int = 0) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, list):
        return [f"{prefix} must be an array"]
    if len(data) < min_items:
        errors.append(f"{prefix} must contain at least {min_items} item(s)")
    for index, item in enumerate(data):
        if not isinstance(item, str):
            errors.append(f"{prefix}[{index}] must be a string")
    return errors


def _validate_common(data: Any, active_goal: dict[str, Any], schema: str, prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    required = [
        "schema",
        "github",
        "goal",
        "previous_subagent",
        "context",
        "rationale",
        "next_agent",
        "required_evidence",
        "stop_condition",
    ]
    errors.extend(_require(data, required, prefix))
    if data.get("schema") != schema:
        errors.append(f"{prefix}.schema must be {schema}")
    github = data.get("github")
    if not isinstance(github, dict):
        errors.append(f"{prefix}.github must be an object")
    elif github.get("repo") != "grahama1970/chatgpt-lab":
        errors.append(f"{prefix}.github.repo must be grahama1970/chatgpt-lab")
    errors.extend(_validate_goal_ref(data.get("goal"), active_goal, f"{prefix}.goal"))
    if data.get("previous_subagent") not in ALLOWED_SUBAGENTS and data.get("previous_subagent") not in {"chatgpt-pro"}:
        errors.append(f"{prefix}.previous_subagent must be recognized")
    context = data.get("context")
    if not isinstance(context, dict):
        errors.append(f"{prefix}.context must be an object")
    elif not nonempty_string(context.get("summary")):
        errors.append(f"{prefix}.context.summary must be a non-empty string")
    elif "artifacts" in context:
        errors.extend(_validate_string_array(context["artifacts"], f"{prefix}.context.artifacts"))
    if not nonempty_string(data.get("rationale")):
        errors.append(f"{prefix}.rationale must be a non-empty string")
    errors.extend(_validate_next_agent(data.get("next_agent"), f"{prefix}.next_agent"))
    errors.extend(_validate_string_array(data.get("required_evidence"), f"{prefix}.required_evidence"))
    if not nonempty_string(data.get("stop_condition")):
        errors.append(f"{prefix}.stop_condition must be a non-empty string")
    return errors


def _target_kind_and_number(target: str) -> tuple[str, int] | None:
    if target.startswith("issue#"):
        value = target.removeprefix("issue#")
        if value.isdigit():
            return "issue", int(value)
    if target.startswith("pr#"):
        value = target.removeprefix("pr#")
        if value.isdigit():
            return "pr", int(value)
    return None


def _next(data: dict[str, Any]) -> dict[str, Any]:
    next_agent = data["next_agent"]
    executor = next_agent.get("executor", DEFAULT_EXECUTOR)
    return {
        "subagent": next_agent["name"],
        "executor": executor,
        "labels": [f"next:{next_agent['name']}", f"executor:{executor}"],
    }


def normalize_tau_handoff(data: dict[str, Any], active_goal: dict[str, Any]) -> dict[str, Any]:
    target = data["github"]["target"]
    parsed = _target_kind_and_number(target)
    return {
        "schema": "chatgpt_lab.route_decision.v1",
        "status": "ROUTE",
        "mode": "dry_run",
        "would_mutate": False,
        "source": {
            "kind": parsed[0] if parsed else None,
            "number": parsed[1] if parsed else None,
            "selected_comment_id": None,
            "selected_schema": data["schema"],
        },
        "goal": {
            "goal_id": active_goal["goal_id"],
            "goal_version": active_goal["version"],
            "goal_hash": active_goal["goal_hash"],
            "matched_active_goal": True,
        },
        "next": _next(data),
        "reasons": ["normalized compact Tau handoff"],
        "missing": [],
        "errors": [],
    }


def normalize_tau_generated_ticket(data: dict[str, Any], active_goal: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "chatgpt_lab.route_decision.v1",
        "status": "ROUTE",
        "mode": "dry_run",
        "would_mutate": False,
        "source": {
            "kind": data["ticket"].get("kind"),
            "number": None,
            "selected_comment_id": None,
            "selected_schema": data["schema"],
        },
        "goal": {
            "goal_id": active_goal["goal_id"],
            "goal_version": active_goal["version"],
            "goal_hash": active_goal["goal_hash"],
            "matched_active_goal": True,
        },
        "next": _next(data),
        "reasons": ["normalized compact Tau generated ticket"],
        "missing": [],
        "errors": [],
    }


def normalize_tau_goal_change(data: dict[str, Any], active_goal: dict[str, Any]) -> dict[str, Any]:
    target = data["github"]["target"]
    parsed = _target_kind_and_number(target)
    return {
        "schema": "chatgpt_lab.route_decision.v1",
        "status": "ROUTE",
        "mode": "dry_run",
        "would_mutate": False,
        "source": {
            "kind": parsed[0] if parsed else None,
            "number": parsed[1] if parsed else None,
            "selected_comment_id": None,
            "selected_schema": data["schema"],
        },
        "goal": {
            "goal_id": active_goal["goal_id"],
            "goal_version": active_goal["version"],
            "goal_hash": active_goal["goal_hash"],
            "matched_active_goal": True,
        },
        "next": _next(data),
        "reasons": ["normalized compact Tau human goal change"],
        "missing": [],
        "errors": [],
    }


def validate_tau_contract(data: Any, active_goal: dict[str, Any], *, trusted_human: str | None = None) -> tuple[list[str], dict[str, Any] | None]:
    if not isinstance(data, dict):
        return ["tau contract must be an object"], None
    schema = data.get("schema")
    if schema == TAU_AGENT_HANDOFF_SCHEMA:
        errors = _validate_common(data, active_goal, TAU_AGENT_HANDOFF_SCHEMA, "tau_handoff")
        if "result" not in data:
            errors.append("tau_handoff missing required field: result")
        elif not isinstance(data.get("result"), dict):
            errors.append("tau_handoff.result must be an object")
        else:
            result = data["result"]
            errors.extend(_require(result, ["status", "summary", "evidence"], "tau_handoff.result"))
            if not nonempty_string(result.get("status")):
                errors.append("tau_handoff.result.status must be a non-empty string")
            if not nonempty_string(result.get("summary")):
                errors.append("tau_handoff.result.summary must be a non-empty string")
            errors.extend(_validate_string_array(result.get("evidence"), "tau_handoff.result.evidence"))
        if errors:
            return errors, None
        return [], normalize_tau_handoff(data, active_goal)
    if schema == TAU_GENERATED_TICKET_SCHEMA:
        errors = _validate_common(data, active_goal, TAU_GENERATED_TICKET_SCHEMA, "tau_generated_ticket")
        for key in ["ticket", "requested_work", "goal_amendment_proposal"]:
            if key not in data:
                errors.append(f"tau_generated_ticket missing required field: {key}")
        ticket = data.get("ticket")
        if not isinstance(ticket, dict):
            errors.append("tau_generated_ticket.ticket must be an object")
        else:
            errors.extend(_require(ticket, ["kind", "title", "body"], "tau_generated_ticket.ticket"))
            for key in ["kind", "title", "body"]:
                if not nonempty_string(ticket.get(key)):
                    errors.append(f"tau_generated_ticket.ticket.{key} must be a non-empty string")
        if not nonempty_string(data.get("requested_work")):
            errors.append("tau_generated_ticket.requested_work must be a non-empty string")
        if data.get("goal_amendment_proposal") is not None and data.get("next_agent", {}).get("name") not in {"human", "goal-guardian"}:
            errors.append("tau_generated_ticket with goal_amendment_proposal must route to human or goal-guardian")
        if errors:
            return errors, None
        return [], normalize_tau_generated_ticket(data, active_goal)
    if schema == TAU_HUMAN_GOAL_CHANGE_SCHEMA:
        errors = _validate_common(data, active_goal, TAU_HUMAN_GOAL_CHANGE_SCHEMA, "tau_human_goal_change")
        if data.get("previous_subagent") != "human":
            errors.append("tau_human_goal_change.previous_subagent must be human")
        if trusted_human is not None and trusted_human not in TRUSTED_HUMANS:
            errors.append("tau_human_goal_change author must be trusted human")
        if data.get("next_agent", {}).get("name") != "goal-guardian":
            errors.append("tau_human_goal_change.next_agent.name must be goal-guardian")
        if "new_goal" not in data:
            errors.append("tau_human_goal_change missing required field: new_goal")
        elif not isinstance(data.get("new_goal"), dict):
            errors.append("tau_human_goal_change.new_goal must be an object")
        else:
            new_goal = data["new_goal"]
            errors.extend(
                _require(
                    new_goal,
                    ["text", "success_criteria", "constraints", "non_goals"],
                    "tau_human_goal_change.new_goal",
                )
            )
            if not nonempty_string(new_goal.get("text")):
                errors.append("tau_human_goal_change.new_goal.text must be a non-empty string")
            errors.extend(_validate_string_array(new_goal.get("success_criteria"), "tau_human_goal_change.new_goal.success_criteria", min_items=1))
            errors.extend(_validate_string_array(new_goal.get("constraints"), "tau_human_goal_change.new_goal.constraints"))
            errors.extend(_validate_string_array(new_goal.get("non_goals"), "tau_human_goal_change.new_goal.non_goals"))
        if errors:
            return errors, None
        return [], normalize_tau_goal_change(data, active_goal)
    return ["unknown Tau schema"], None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    parser.add_argument("--trusted-human")
    args = parser.parse_args()

    errors: list[str] = []
    decision = None
    try:
        active_goal = load_json(args.active_goal)
        errors.extend(validate_goal_capsule(active_goal))
        data = load_json(args.path)
        contract_errors, decision = validate_tau_contract(data, active_goal, trusted_human=args.trusted_human)
        errors.extend(contract_errors)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"unable to read Tau contract: {exc}")

    result = {
        "schema": "chatgpt_lab.tau_contract_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "path": str(args.path),
        "errors": errors,
        "route_decision": decision,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
