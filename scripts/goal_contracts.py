#!/usr/bin/env python3
"""Shared validators for the goal-locked PhatGPT-LAB contract slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOAL_SCHEMA = "chatgpt_lab.goal_capsule.v1"
HANDOFF_SCHEMA = "chatgpt_lab.agent_handoff.v1"
HUMAN_INTERJECTION_SCHEMA = "chatgpt_lab.human_interjection.v1"
GENERATED_TICKET_SCHEMA = "chatgpt_lab.generated_ticket.v1"
ALLOWED_SUBAGENTS = {
    "human",
    "goal-guardian",
    "webgpt-ticket-author",
    "coder",
    "reviewer",
    "releaser",
}
ALLOWED_EXECUTORS = {"github-actions", "local", "either", "human"}
GOAL_HASH_FIELDS = (
    "immutable_goal",
    "success_criteria",
    "constraints",
    "non_goals",
    "human_change_required_for",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def canonical_goal_material(goal: dict[str, Any]) -> dict[str, Any]:
    return {field: goal.get(field) for field in GOAL_HASH_FIELDS}


def compute_goal_hash(goal: dict[str, Any]) -> str:
    payload = json.dumps(
        canonical_goal_material(goal),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _require_keys(data: dict[str, Any], required: list[str], prefix: str) -> list[str]:
    return [f"{prefix} missing required field: {key}" for key in required if key not in data]


def _validate_string_list(data: dict[str, Any], key: str, prefix: str, *, min_items: int = 0) -> list[str]:
    errors: list[str] = []
    value = data.get(key)
    if not isinstance(value, list) or len(value) < min_items:
        errors.append(f"{prefix}.{key} must be an array with at least {min_items} item(s)")
        return errors
    for index, item in enumerate(value):
        if not nonempty_string(item):
            errors.append(f"{prefix}.{key}[{index}] must be a non-empty string")
    return errors


def validate_goal_capsule(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["goal capsule must be an object"]

    required = [
        "schema",
        "goal_id",
        "version",
        "status",
        "owner",
        "immutable_goal",
        "success_criteria",
        "constraints",
        "non_goals",
        "human_change_required_for",
        "created_by",
        "created_at",
        "goal_hash",
    ]
    errors.extend(_require_keys(data, required, "goal"))
    if data.get("schema") != GOAL_SCHEMA:
        errors.append(f"goal.schema must be {GOAL_SCHEMA}")
    if not nonempty_string(data.get("goal_id")):
        errors.append("goal.goal_id must be a non-empty string")
    if not isinstance(data.get("version"), int) or data.get("version", 0) < 1:
        errors.append("goal.version must be a positive integer")
    if data.get("status") not in {"active", "superseded", "paused"}:
        errors.append("goal.status must be active, superseded, or paused")
    if data.get("owner") != "human":
        errors.append("goal.owner must be human")
    if data.get("created_by") != "human":
        errors.append("goal.created_by must be human")
    if not nonempty_string(data.get("immutable_goal")):
        errors.append("goal.immutable_goal must be a non-empty string")
    if not nonempty_string(data.get("created_at")):
        errors.append("goal.created_at must be a non-empty string")
    errors.extend(_validate_string_list(data, "success_criteria", "goal", min_items=1))
    errors.extend(_validate_string_list(data, "constraints", "goal"))
    errors.extend(_validate_string_list(data, "non_goals", "goal"))
    errors.extend(_validate_string_list(data, "human_change_required_for", "goal", min_items=1))

    expected_hash = compute_goal_hash(data)
    if data.get("goal_hash") != expected_hash:
        errors.append(f"goal.goal_hash must equal {expected_hash}")
    return errors


def validate_goal_ref(data: Any, active_goal: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    required = ["goal_id", "goal_version", "goal_hash", "immutable_goal_preserved"]
    errors.extend(_require_keys(data, required, prefix))
    if data.get("goal_id") != active_goal.get("goal_id"):
        errors.append(f"{prefix}.goal_id must match active goal")
    if data.get("goal_version") != active_goal.get("version"):
        errors.append(f"{prefix}.goal_version must match active goal version")
    if data.get("goal_hash") != active_goal.get("goal_hash"):
        errors.append(f"{prefix}.goal_hash must match active goal hash")
    if data.get("immutable_goal_preserved") is not True:
        errors.append(f"{prefix}.immutable_goal_preserved must be true")
    return errors


def validate_next(data: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    required = ["subagent", "executor", "reason"]
    errors.extend(_require_keys(data, required, prefix))
    if data.get("subagent") not in ALLOWED_SUBAGENTS:
        errors.append(f"{prefix}.subagent must be one of {sorted(ALLOWED_SUBAGENTS)}")
    if data.get("executor") not in ALLOWED_EXECUTORS:
        errors.append(f"{prefix}.executor must be one of {sorted(ALLOWED_EXECUTORS)}")
    if not nonempty_string(data.get("reason")):
        errors.append(f"{prefix}.reason must be a non-empty string")
    labels = data.get("labels", [])
    if labels is not None and not isinstance(labels, list):
        errors.append(f"{prefix}.labels must be an array when present")
    return errors


def validate_github_projection(data: Any, prefix: str, expected_next: dict[str, Any] | None, ticket: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{prefix} must be an object"]
    required = ["target", "create", "comment", "labels"]
    errors.extend(_require_keys(data, required, prefix))
    labels = data.get("labels")
    if not isinstance(labels, dict):
        errors.append(f"{prefix}.labels must be an object")
        label_add: list[Any] = []
    else:
        label_add = labels.get("add", [])
        if not isinstance(label_add, list):
            errors.append(f"{prefix}.labels.add must be an array")
            label_add = []
        if not isinstance(labels.get("remove"), list):
            errors.append(f"{prefix}.labels.remove must be an array")

    if expected_next is not None:
        subagent = expected_next.get("subagent")
        executor = expected_next.get("executor")
        if subagent and f"next:{subagent}" not in label_add:
            errors.append(f"{prefix}.labels.add must include next:{subagent}")
        if executor and f"executor:{executor}" not in label_add:
            errors.append(f"{prefix}.labels.add must include executor:{executor}")
        next_labels = expected_next.get("labels", [])
        if isinstance(next_labels, list):
            for label in next_labels:
                if label not in label_add:
                    errors.append(f"{prefix}.labels.add must include next label {label}")

    create = data.get("create")
    comment = data.get("comment")
    target = data.get("target")
    if ticket is not None:
        if target is not None:
            errors.append(f"{prefix}.target must be null for generated ticket creation")
        if comment is not None:
            errors.append(f"{prefix}.comment must be null for generated ticket creation")
        if not isinstance(create, dict):
            errors.append(f"{prefix}.create must be an object for generated ticket creation")
        else:
            for key in ["kind", "title", "body", "labels"]:
                if create.get(key) != ticket.get(key):
                    errors.append(f"{prefix}.create.{key} must match ticket.{key}")
    else:
        if create is not None:
            errors.append(f"{prefix}.create must be null for existing-ticket handoffs")
        if not isinstance(target, dict):
            errors.append(f"{prefix}.target must identify the existing GitHub thread")
        if not isinstance(comment, dict) or not nonempty_string(comment.get("body")):
            errors.append(f"{prefix}.comment.body must be a non-empty string for existing-ticket handoffs")
    return errors


def validate_agent_handoff(data: Any, active_goal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["agent handoff must be an object"]
    required = [
        "schema",
        "goal",
        "run",
        "original_goal",
        "fresh_context",
        "results",
        "rationale",
        "evidence",
        "required_evidence",
        "next",
        "github",
        "stop_condition",
    ]
    errors.extend(_require_keys(data, required, "handoff"))
    if data.get("schema") != HANDOFF_SCHEMA:
        errors.append(f"handoff.schema must be {HANDOFF_SCHEMA}")
    errors.extend(validate_goal_ref(data.get("goal"), active_goal, "handoff.goal"))
    if data.get("original_goal") != active_goal.get("immutable_goal"):
        errors.append("handoff.original_goal must exactly match active immutable_goal")
    if not isinstance(data.get("fresh_context"), dict):
        errors.append("handoff.fresh_context must be an object")
    if not isinstance(data.get("results"), dict):
        errors.append("handoff.results must be an object")
    if not nonempty_string(data.get("rationale")):
        errors.append("handoff.rationale must be a non-empty string")
    if not isinstance(data.get("evidence"), list):
        errors.append("handoff.evidence must be an array")
    if not isinstance(data.get("required_evidence"), list):
        errors.append("handoff.required_evidence must be an array")
    errors.extend(validate_next(data.get("next"), "handoff.next"))
    errors.extend(validate_github_projection(data.get("github"), "handoff.github", data.get("next")))
    if not nonempty_string(data.get("stop_condition")):
        errors.append("handoff.stop_condition must be a non-empty string")

    run = data.get("run")
    if not isinstance(run, dict):
        errors.append("handoff.run must be an object")
    else:
        run_required = ["run_id", "actor_type", "actor", "attempt"]
        errors.extend(_require_keys(run, run_required, "handoff.run"))
        if run.get("actor_type") not in {"human", "webgpt", "subagent", "github-actions", "local-cron"}:
            errors.append("handoff.run.actor_type is invalid")
        if not nonempty_string(run.get("actor")):
            errors.append("handoff.run.actor must be a non-empty string")
        if not isinstance(run.get("attempt"), int) or run.get("attempt", 0) < 1:
            errors.append("handoff.run.attempt must be a positive integer")
    return errors


def validate_human_interjection(data: Any, active_goal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["human interjection must be an object"]
    required = [
        "schema",
        "authority",
        "channel",
        "goal",
        "decision",
        "course_correction",
        "next",
        "github",
        "required_evidence",
        "stop_condition",
    ]
    errors.extend(_require_keys(data, required, "human_interjection"))
    if data.get("schema") != HUMAN_INTERJECTION_SCHEMA:
        errors.append(f"human_interjection.schema must be {HUMAN_INTERJECTION_SCHEMA}")
    if data.get("authority") != "human":
        errors.append("human_interjection.authority must be human")
    if data.get("channel") not in {"github", "chatgpt-interface"}:
        errors.append("human_interjection.channel must be github or chatgpt-interface")

    goal = data.get("goal")
    if not isinstance(goal, dict):
        errors.append("human_interjection.goal must be an object")
    else:
        if goal.get("goal_id") != active_goal.get("goal_id"):
            errors.append("human_interjection.goal.goal_id must match active goal")
        if goal.get("current_goal_version") != active_goal.get("version"):
            errors.append("human_interjection.goal.current_goal_version must match active goal version")
        if goal.get("current_goal_hash") != active_goal.get("goal_hash"):
            errors.append("human_interjection.goal.current_goal_hash must match active goal hash")
        if goal.get("goal_action") not in {"preserve", "create_new_version", "accept_amendment", "reject_amendment"}:
            errors.append("human_interjection.goal.goal_action is invalid")
    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("human_interjection.decision must be an object")
    else:
        if decision.get("type") not in {"course_correct", "reprioritize", "pause", "resume", "reject_branch", "approve_branch", "create_ticket", "route_ticket", "stop"}:
            errors.append("human_interjection.decision.type is invalid")
        if not nonempty_string(decision.get("summary")):
            errors.append("human_interjection.decision.summary must be a non-empty string")
        if not nonempty_string(decision.get("rationale")):
            errors.append("human_interjection.decision.rationale must be a non-empty string")
    if not isinstance(data.get("course_correction"), dict):
        errors.append("human_interjection.course_correction must be an object")
    if not isinstance(data.get("required_evidence"), list):
        errors.append("human_interjection.required_evidence must be an array")
    errors.extend(validate_next(data.get("next"), "human_interjection.next"))
    errors.extend(validate_github_projection(data.get("github"), "human_interjection.github", data.get("next")))
    if not nonempty_string(data.get("stop_condition")):
        errors.append("human_interjection.stop_condition must be a non-empty string")
    return errors


def validate_generated_ticket(data: Any, active_goal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["generated ticket must be an object"]
    required = ["schema", "goal", "ticket", "handoff", "github", "goal_amendment_proposal"]
    errors.extend(_require_keys(data, required, "generated_ticket"))
    if data.get("schema") != GENERATED_TICKET_SCHEMA:
        errors.append(f"generated_ticket.schema must be {GENERATED_TICKET_SCHEMA}")
    errors.extend(validate_goal_ref(data.get("goal"), active_goal, "generated_ticket.goal"))

    ticket = data.get("ticket")
    if not isinstance(ticket, dict):
        errors.append("generated_ticket.ticket must be an object")
    else:
        if ticket.get("kind") not in {"issue", "pr"}:
            errors.append("generated_ticket.ticket.kind must be issue or pr")
        if not nonempty_string(ticket.get("title")):
            errors.append("generated_ticket.ticket.title must be a non-empty string")
        if not nonempty_string(ticket.get("body")):
            errors.append("generated_ticket.ticket.body must be a non-empty string")
        labels = ticket.get("labels")
        if not isinstance(labels, list) or not labels:
            errors.append("generated_ticket.ticket.labels must be a non-empty array")
        elif not any(str(label).startswith("next:") for label in labels):
            errors.append("generated_ticket.ticket.labels must include a next:* route")

    handoff = data.get("handoff")
    if not isinstance(handoff, dict):
        errors.append("generated_ticket.handoff must be an object")
    else:
        required_handoff = [
            "original_goal",
            "fresh_context",
            "rationale",
            "next",
            "next_subagent",
            "required_result",
            "stop_condition",
        ]
        errors.extend(_require_keys(handoff, required_handoff, "generated_ticket.handoff"))
        if handoff.get("original_goal") != active_goal.get("immutable_goal"):
            errors.append("generated_ticket.handoff.original_goal must exactly match active immutable_goal")
        if not isinstance(handoff.get("fresh_context"), dict):
            errors.append("generated_ticket.handoff.fresh_context must be an object")
        if handoff.get("next_subagent") not in ALLOWED_SUBAGENTS:
            errors.append("generated_ticket.handoff.next_subagent is invalid")
        next_errors = validate_next(handoff.get("next"), "generated_ticket.handoff.next")
        errors.extend(next_errors)
        if isinstance(handoff.get("next"), dict) and handoff.get("next_subagent") != handoff["next"].get("subagent"):
            errors.append("generated_ticket.handoff.next_subagent must match handoff.next.subagent")
        if not nonempty_string(handoff.get("rationale")):
            errors.append("generated_ticket.handoff.rationale must be a non-empty string")
        if not nonempty_string(handoff.get("required_result")):
            errors.append("generated_ticket.handoff.required_result must be a non-empty string")
        if not nonempty_string(handoff.get("stop_condition")):
            errors.append("generated_ticket.handoff.stop_condition must be a non-empty string")

    if data.get("goal_amendment_proposal") is not None:
        labels = []
        if isinstance(ticket, dict) and isinstance(ticket.get("labels"), list):
            labels = ticket["labels"]
        next_subagent = handoff.get("next_subagent") if isinstance(handoff, dict) else None
        if next_subagent not in {"human", "goal-guardian"} and "next:human" not in labels and "next:goal-guardian" not in labels:
            errors.append("generated_ticket with goal_amendment_proposal must route to human or goal-guardian")
    next_block = handoff.get("next") if isinstance(handoff, dict) else None
    errors.extend(validate_github_projection(data.get("github"), "generated_ticket.github", next_block, ticket if isinstance(ticket, dict) else None))
    return errors
