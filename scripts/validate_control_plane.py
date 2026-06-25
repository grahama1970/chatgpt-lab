#!/usr/bin/env python3
"""Validate the versioned ChatGPT-Lab control-plane source."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_REPOSITORY = "grahama1970/chatgpt-lab"
REQUIRED_FILES = (
    "README.md",
    "sources/PROJECT_INSTRUCTIONS.md",
    "sources/SOURCE_INDEX.md",
    "sources/source-manifest.json",
    "sources/README.md",
    "sources/control-plane/OPERATING_CONTRACT.md",
    "sources/control-plane/CURRENT_STATE.md",
    "sources/control-plane/REVIEW_RUBRIC.md",
    "sources/control-plane/DECISIONS.md",
    "sources/control-plane/MIGRATION_NOTES.md",
    "docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md",
    "docs/requirements/CONTROL_AUTHORITY.md",
    "schemas/iteration.schema.json",
    ".github/workflows/source-check.yml",
)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return value


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {relative_path}")

    try:
        manifest = load_json("sources/source-manifest.json")
        if manifest.get("schema") != "chatgpt_lab.source_manifest.v1":
            errors.append("sources/source-manifest.json has an unexpected schema")
        control_plane = manifest.get("control_plane")
        if not isinstance(control_plane, dict):
            errors.append("sources/source-manifest.json is missing control_plane")
        elif control_plane.get("repository") != TARGET_REPOSITORY:
            errors.append(f"control_plane.repository must be {TARGET_REPOSITORY}")
        sources = manifest.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append("sources/source-manifest.json must contain at least one source")
        else:
            ids = [source.get("id") for source in sources if isinstance(source, dict)]
            if len(ids) != len(set(ids)):
                errors.append("sources/source-manifest.json contains duplicate source ids")
            required_source_ids = {
                "agent-skills-registry",
                "monocle-man-source",
                "monocle-man-ci",
                "monocle-man-netlify",
            }
            missing = sorted(required_source_ids.difference(ids))
            if missing:
                errors.append(
                    "sources/source-manifest.json is missing sources: "
                    + ", ".join(missing)
                )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid sources/source-manifest.json: {exc}")

    try:
        iteration_schema = load_json("schemas/iteration.schema.json")
        required = set(iteration_schema.get("required", []))
        expected = {
            "schema",
            "iteration_id",
            "started_at",
            "control_plane",
            "skills",
            "candidate",
            "evidence",
            "reviews",
            "verdict",
        }
        missing = sorted(expected.difference(required))
        if missing:
            errors.append(
                "iteration schema is missing required fields: " + ", ".join(missing)
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid iteration schema: {exc}")

    project_instructions = ROOT / "sources/PROJECT_INSTRUCTIONS.md"
    if project_instructions.is_file():
        text = project_instructions.read_text(encoding="utf-8")
        if TARGET_REPOSITORY not in text:
            errors.append(
                "sources/PROJECT_INSTRUCTIONS.md does not point to the target repository"
            )
        if "ChatGPT Web is the primary controller" not in text:
            errors.append(
                "sources/PROJECT_INSTRUCTIONS.md does not state controller authority"
            )

    source_index = ROOT / "sources/SOURCE_INDEX.md"
    if source_index.is_file():
        text = source_index.read_text(encoding="utf-8")
        if "docs/requirements/CONTROL_AUTHORITY.md" not in text:
            errors.append("sources/SOURCE_INDEX.md does not load CONTROL_AUTHORITY.md")

    result = {
        "schema": "chatgpt_lab.control_plane_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "root": str(ROOT),
        "target_repository": TARGET_REPOSITORY,
        "required_files": list(REQUIRED_FILES),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
