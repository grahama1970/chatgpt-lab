#!/usr/bin/env python3
"""Dry-run route parser for goal-locked GitHub thread fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from goal_contracts import (
    GENERATED_TICKET_SCHEMA,
    HANDOFF_SCHEMA,
    HUMAN_INTERJECTION_SCHEMA,
    ROOT,
    load_json,
    validate_agent_handoff,
    validate_generated_ticket,
    validate_goal_capsule,
    validate_human_interjection,
)

ROUTE_DECISION_SCHEMA = "chatgpt_lab.route_decision.v1"
THREAD_FIXTURE_SCHEMA = "chatgpt_lab.github_thread_fixture.v1"
LEGACY_TASK_MARKER = "phatgpt-task:v1"
CONTRACT_SCHEMAS = {
    HUMAN_INTERJECTION_SCHEMA,
    HANDOFF_SCHEMA,
    GENERATED_TICKET_SCHEMA,
}


def _base_decision(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": ROUTE_DECISION_SCHEMA,
        "status": "NOOP",
        "mode": "dry_run",
        "would_mutate": False,
        "source": {
            "kind": fixture.get("kind"),
            "number": fixture.get("number"),
            "selected_comment_id": None,
            "selected_schema": None,
        },
        "goal": {
            "goal_id": None,
            "goal_version": None,
            "goal_hash": None,
            "matched_active_goal": False,
        },
        "next": None,
        "reasons": [],
        "missing": [],
        "errors": [],
    }


def _extract_json_objects(text: str) -> list[dict[str, Any]]:
    blocks: list[str] = []
    blocks.extend(match.group(1) for match in re.finditer(r"```json\s*(.*?)\s*```", text, re.DOTALL))
    blocks.extend(match.group(1) for match in re.finditer(r"<!--\s*(.*?)\s*-->", text, re.DOTALL))
    if not blocks and text.strip().startswith("{"):
        blocks.append(text.strip())

    values: list[dict[str, Any]] = []
    for block in blocks:
        try:
            value = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            values.append(value)
    return values


def _iter_actionable_blocks(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    body_blocks = _extract_json_objects(fixture.get("body", ""))
    for index, block in enumerate(body_blocks):
        schema = block.get("schema")
        if schema in CONTRACT_SCHEMAS:
            candidates.append(
                {
                    "comment_id": None,
                    "created_at": "",
                    "index": index,
                    "author": fixture.get("author"),
                    "block": block,
                }
            )

    for comment in fixture.get("comments", []):
        for index, block in enumerate(_extract_json_objects(comment.get("body", ""))):
            schema = block.get("schema")
            if schema in CONTRACT_SCHEMAS:
                candidates.append(
                    {
                        "comment_id": comment.get("id"),
                        "created_at": comment.get("created_at", ""),
                        "index": index,
                        "author": comment.get("author"),
                        "block": block,
                    }
                )
    return candidates


def _contains_legacy_task(fixture: dict[str, Any]) -> bool:
    if LEGACY_TASK_MARKER in fixture.get("body", ""):
        return True
    return any(LEGACY_TASK_MARKER in comment.get("body", "") for comment in fixture.get("comments", []))


def _validate_fixture(fixture: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(fixture, dict):
        return ["fixture must be an object"]
    required = ["schema", "kind", "number", "title", "author", "labels", "body", "comments"]
    for key in required:
        if key not in fixture:
            errors.append(f"fixture missing required field: {key}")
    if fixture.get("schema") != THREAD_FIXTURE_SCHEMA:
        errors.append(f"fixture.schema must be {THREAD_FIXTURE_SCHEMA}")
    if fixture.get("kind") not in {"issue", "pr"}:
        errors.append("fixture.kind must be issue or pr")
    if not isinstance(fixture.get("number"), int) or fixture.get("number", 0) < 1:
        errors.append("fixture.number must be a positive integer")
    if not isinstance(fixture.get("labels"), list):
        errors.append("fixture.labels must be an array")
    if not isinstance(fixture.get("comments"), list):
        errors.append("fixture.comments must be an array")
    return errors


def _newest_valid_candidate(candidates: list[dict[str, Any]], active_goal: dict[str, Any], trusted_humans: set[str]) -> tuple[dict[str, Any] | None, list[str]]:
    validation_errors: list[str] = []
    priority = {
        HUMAN_INTERJECTION_SCHEMA: 3,
        HANDOFF_SCHEMA: 2,
        GENERATED_TICKET_SCHEMA: 1,
    }

    ordered = sorted(
        candidates,
        key=lambda item: (priority.get(item["block"].get("schema"), 0), item.get("created_at", ""), item.get("index", 0)),
        reverse=True,
    )
    for candidate in ordered:
        block = candidate["block"]
        schema = block.get("schema")
        if schema == HUMAN_INTERJECTION_SCHEMA and candidate.get("author") not in trusted_humans:
            validation_errors.append("human_interjection author is not trusted: " + str(candidate.get("author")))
            continue
        if schema == HUMAN_INTERJECTION_SCHEMA:
            errors = validate_human_interjection(block, active_goal)
            goal_action = block.get("goal", {}).get("goal_action") if isinstance(block.get("goal"), dict) else None
            next_subagent = block.get("next", {}).get("subagent") if isinstance(block.get("next"), dict) else None
            if goal_action in {"create_new_version", "accept_amendment"} and next_subagent != "goal-guardian":
                errors.append("goal_change_must_route_to_goal_guardian")
        elif schema == HANDOFF_SCHEMA:
            errors = validate_agent_handoff(block, active_goal)
        elif schema == GENERATED_TICKET_SCHEMA:
            errors = validate_generated_ticket(block, active_goal)
        else:
            continue

        if not errors:
            return candidate, validation_errors
        validation_errors.extend(errors)
    return None, validation_errors


def _decision_from_block(fixture: dict[str, Any], candidate: dict[str, Any], active_goal: dict[str, Any]) -> dict[str, Any]:
    block = candidate["block"]
    schema = block["schema"]
    decision = _base_decision(fixture)
    decision["status"] = "ROUTE"
    decision["source"]["selected_comment_id"] = candidate.get("comment_id")
    decision["source"]["selected_schema"] = schema
    decision["goal"] = {
        "goal_id": active_goal["goal_id"],
        "goal_version": active_goal["version"],
        "goal_hash": active_goal["goal_hash"],
        "matched_active_goal": True,
    }
    if schema == GENERATED_TICKET_SCHEMA:
        subagent = block["handoff"]["next_subagent"]
        labels = block["ticket"].get("labels", [])
        executor = "either"
    else:
        next_block = block["next"]
        subagent = next_block["subagent"]
        labels = next_block.get("labels", [])
        executor = next_block["executor"]
    decision["next"] = {
        "subagent": subagent,
        "executor": executor,
        "labels": labels,
    }
    decision["reasons"].append("selected latest valid actionable block")
    return decision


def route_fixture(fixture: dict[str, Any], active_goal: dict[str, Any], trusted_humans: set[str]) -> dict[str, Any]:
    decision = _base_decision(fixture if isinstance(fixture, dict) else {})
    fixture_errors = _validate_fixture(fixture)
    goal_errors = validate_goal_capsule(active_goal)
    if fixture_errors or goal_errors:
        decision["status"] = "REFUSED"
        decision["reason"] = "invalid_fixture_or_goal"
        decision["errors"] = fixture_errors + goal_errors
        decision["next_required_action"] = "Fix the fixture or active goal before dry-run routing."
        return decision

    candidates = _iter_actionable_blocks(fixture)
    candidate, validation_errors = _newest_valid_candidate(candidates, active_goal, trusted_humans)
    if candidate is not None:
        return _decision_from_block(fixture, candidate, active_goal)

    decision["errors"] = validation_errors
    if _contains_legacy_task(fixture):
        decision["status"] = "REFUSED"
        decision["reason"] = "legacy_phatgpt_task_detected_but_not_routable_in_this_slice"
        decision["next_required_action"] = "Wrap or migrate this task into agent_handoff.v1 before generic routing."
        return decision
    if validation_errors:
        decision["status"] = "REFUSED"
        decision["reason"] = "invalid_actionable_block"
        if any(
            "missing required field: subagent" in error
            or "missing required field: next" in error
            for error in validation_errors
        ):
            decision["missing"].append("next.subagent")
            decision["next_required_action"] = "Human, WebGPT, or a subagent must provide a valid next.subagent."
        return decision

    decision["status"] = "NOOP"
    decision["reason"] = "no_actionable_route"
    decision["next_required_action"] = "Add a valid human_interjection.v1, agent_handoff.v1, or generated_ticket.v1 block."
    return decision


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    route = subparsers.add_parser("route-fixture")
    route.add_argument("fixture", type=Path)
    route.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    route.add_argument("--trusted-human", action="append", default=[])
    args = parser.parse_args()

    try:
        fixture = load_json(args.fixture)
        active_goal = load_json(args.active_goal)
        decision = route_fixture(fixture, active_goal, set(args.trusted_human))
    except (OSError, json.JSONDecodeError) as exc:
        decision = _base_decision({})
        decision["status"] = "REFUSED"
        decision["reason"] = "unable_to_read_fixture_or_goal"
        decision["errors"] = [str(exc)]
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["status"] in {"ROUTE", "NOOP"} else 1


if __name__ == "__main__":
    sys.exit(main())
