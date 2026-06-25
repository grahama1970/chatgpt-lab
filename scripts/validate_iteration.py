#!/usr/bin/env python3
"""Validate a ChatGPT-Lab iteration or iteration status JSON file.

This validator is intentionally dependency-free so it can run in GitHub Actions
and local project-agent shells before the full control-plane package exists.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ITERATION_SCHEMA = "chatgpt_lab.iteration.v1"
STATUS_SCHEMA = "chatgpt_lab.iteration_status.v1"
VERDICTS = {"PASS", "NEEDS_CHANGES", "BLOCKED", "INSUFFICIENT_EVIDENCE"}
STATUS_STATES = {"READY", "RUNNING", "PASS", "NEEDS_CHANGES", "BLOCKED", "INSUFFICIENT_EVIDENCE"}


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


def validate_iteration(data: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "iteration", errors)
    if errors:
        return errors

    required = [
        "schema",
        "iteration_id",
        "started_at",
        "control_plane",
        "skills",
        "candidate",
        "evidence",
        "reviews",
        "verdict",
    ]
    for key in required:
        if key not in root:
            errors.append(f"missing required field: {key}")

    if root.get("schema") != ITERATION_SCHEMA:
        errors.append(f"schema must be {ITERATION_SCHEMA}")

    if not is_nonempty_string(root.get("iteration_id")):
        errors.append("iteration_id must be a non-empty string")

    if root.get("started_at") is not None and not is_nonempty_string(root.get("started_at")):
        errors.append("started_at must be a non-empty string or null")

    control_plane = require_object(root.get("control_plane"), "control_plane", errors)
    if control_plane:
        if not is_nonempty_string(control_plane.get("repository")):
            errors.append("control_plane.repository must be a non-empty string")
        if not is_nonempty_string(control_plane.get("ref")):
            errors.append("control_plane.ref must be a non-empty string")

    skills = require_object(root.get("skills"), "skills", errors)
    if skills:
        if not is_nonempty_string(skills.get("registry_repository")):
            errors.append("skills.registry_repository must be a non-empty string")
        if not is_nonempty_string(skills.get("registry_ref")):
            errors.append("skills.registry_ref must be a non-empty string")
        if not isinstance(skills.get("selected"), list):
            errors.append("skills.selected must be an array")

    candidate = require_object(root.get("candidate"), "candidate", errors)
    if candidate:
        if not is_nonempty_string(candidate.get("repository")):
            errors.append("candidate.repository must be a non-empty string")
        if not is_nonempty_string(candidate.get("branch")):
            errors.append("candidate.branch must be a non-empty string")
        commit = candidate.get("commit")
        if commit is not None and not is_nonempty_string(commit):
            errors.append("candidate.commit must be a non-empty string or null")

    evidence = require_object(root.get("evidence"), "evidence", errors)
    if evidence:
        if not isinstance(evidence.get("screenshots"), list):
            errors.append("evidence.screenshots must be an array")
        ci = evidence.get("ci")
        candidate_commit = candidate.get("commit") if candidate else None
        if ci is not None:
            if not isinstance(ci, dict):
                errors.append("evidence.ci must be an object or null")
            elif candidate_commit and ci.get("head_sha") not in (candidate_commit, None):
                errors.append("evidence.ci.head_sha must match candidate.commit when both are present")

    reviews = require_object(root.get("reviews"), "reviews", errors)
    if reviews:
        if "code" not in reviews:
            errors.append("reviews.code is required")
        if "design" not in reviews:
            errors.append("reviews.design is required")

    verdict = root.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"verdict must be one of {sorted(VERDICTS)}")

    if verdict == "PASS":
        candidate_commit = candidate.get("commit") if candidate else None
        ci = evidence.get("ci") if evidence else None
        if not candidate_commit:
            errors.append("PASS requires candidate.commit")
        if not isinstance(ci, dict):
            errors.append("PASS requires evidence.ci")
        elif candidate_commit and ci.get("head_sha") != candidate_commit:
            errors.append("PASS requires evidence.ci.head_sha to equal candidate.commit")
        if not evidence.get("screenshots"):
            errors.append("PASS requires screenshot evidence")

    return errors


def validate_status(data: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "status", errors)
    if errors:
        return errors

    required = [
        "schema",
        "iteration_id",
        "state",
        "phase",
        "candidate_commit",
        "required_next_evidence",
        "blockers",
        "updated_at",
    ]
    for key in required:
        if key not in root:
            errors.append(f"missing required field: {key}")

    if root.get("schema") != STATUS_SCHEMA:
        errors.append(f"schema must be {STATUS_SCHEMA}")
    if not is_nonempty_string(root.get("iteration_id")):
        errors.append("iteration_id must be a non-empty string")
    if root.get("state") not in STATUS_STATES:
        errors.append(f"state must be one of {sorted(STATUS_STATES)}")
    if not is_nonempty_string(root.get("phase")):
        errors.append("phase must be a non-empty string")
    if root.get("candidate_commit") is not None and not is_nonempty_string(root.get("candidate_commit")):
        errors.append("candidate_commit must be a non-empty string or null")
    if not isinstance(root.get("required_next_evidence"), list):
        errors.append("required_next_evidence must be an array")
    if not isinstance(root.get("blockers"), list):
        errors.append("blockers must be an array")
    if not is_nonempty_string(root.get("updated_at")):
        errors.append("updated_at must be a non-empty string")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--status", action="store_true", help="validate an iteration_status file instead of an iteration record")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        data = load_json(args.path)
        errors = validate_status(data) if args.status else validate_iteration(data)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"unable to read JSON: {exc}"]

    result = {
        "schema": "chatgpt_lab.iteration_validation.v1",
        "path": str(args.path),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
