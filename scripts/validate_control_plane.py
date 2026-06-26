#!/usr/bin/env python3
"""Validate the versioned ChatGPT-Lab control-plane source."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_REPOSITORY = "grahama1970/chatgpt-lab"
HEADER_PATH = "assets/chatgpt-lab-header.webp"
COMMIT_ATTRIBUTION_POLICY = "Do not author commits under third-party model names"
FORBIDDEN_LATEST_AUTHOR_TOKENS = ("claude", "anthropic")
REQUIRED_FILES = (
    "README.md",
    "PROJECT_KNOWLEDGE.md",
    "AGENTS.md",
    HEADER_PATH,
    "assets/README.md",
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
    "docs/requirements/BENCHMARK_SLICE_001.md",
    "docs/requirements/WEBGPT_PROJECT_AGENT_OPERATING_MODEL.md",
    "docs/architecture/COLLABORATION_LOOP_V0.md",
    "agent-state/current.json",
    "agent-state/skill-router.json",
    "agent-state/next-command.json",
    "agent-state/last-result.json",
    "schemas/agent-state.schema.json",
    "schemas/skill-router.schema.json",
    "schemas/next-command.schema.json",
    "schemas/workflow-result.schema.json",
    "schemas/iteration.schema.json",
    "schemas/iteration-status.schema.json",
    "schemas/commands/apply-text-patch.schema.json",
    "iterations/templates/iteration.slice-001.template.json",
    "iterations/templates/status.slice-001.template.json",
    "iterations/templates/webgpt-local-task-request.example.json",
    "iterations/templates/local-subagent-refusal.example.json",
    "scripts/validate_iteration.py",
    "scripts/validate_benchmark_evidence.py",
    "scripts/validate_local_subagent_contract.py",
    "scripts/validate_agent_state.py",
    "scripts/apply_text_patch.py",
    "scripts/write_workflow_result.py",
    "monocle-man-site/package.json",
    "monocle-man-site/package-lock.json",
    "monocle-man-site/playwright.config.ts",
    "monocle-man-site/scripts/collect-evidence.mjs",
    "monocle-man-site/src/main.jsx",
    "monocle-man-site/tests/monocle-man.spec.ts",
    "monocle-man-site/tests/monocle-man-animation.spec.ts",
    ".github/workflows/source-check.yml",
    ".github/workflows/agent-dispatch.yml",
    ".github/workflows/webgpt-command-dispatcher.yml",
    ".github/workflows/monocle-man-benchmark.yml",
    ".github/workflows/monocle-man-pages.yml",
)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return value


def current_commit_author() -> str | None:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%an <%ae>"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


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
                "monocle-man-github-pages",
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

    readme = ROOT / "README.md"
    if readme.is_file() and HEADER_PATH not in readme.read_text(encoding="utf-8"):
        errors.append(f"README.md does not reference {HEADER_PATH}")

    agents = ROOT / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        if "ChatGPT Web is the primary controller" not in text:
            errors.append("AGENTS.md does not state controller authority")
        if COMMIT_ATTRIBUTION_POLICY not in text:
            errors.append("AGENTS.md does not state commit attribution policy")

    control_authority = ROOT / "docs/requirements/CONTROL_AUTHORITY.md"
    if control_authority.is_file():
        text = control_authority.read_text(encoding="utf-8")
        if COMMIT_ATTRIBUTION_POLICY not in text:
            errors.append(
                "docs/requirements/CONTROL_AUTHORITY.md does not state commit attribution policy"
            )

    author = current_commit_author()
    if author is None:
        errors.append("could not read latest commit author")
    elif any(token in author.lower() for token in FORBIDDEN_LATEST_AUTHOR_TOKENS):
        errors.append(
            "latest commit author uses forbidden third-party attribution: " + author
        )

    header = ROOT / HEADER_PATH
    if header.is_file():
        data = header.read_bytes()
        if len(data) < 4096:
            errors.append(f"{HEADER_PATH} is unexpectedly small")
        elif data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            errors.append(f"{HEADER_PATH} is not a valid WebP file")

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
