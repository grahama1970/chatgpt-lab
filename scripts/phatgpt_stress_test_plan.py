#!/usr/bin/env python3
"""Collect a read-only PhatGPT stress-test plan artifact."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from phatgpt_capability_inventory import CAPABILITY_TARGETS, memory_recall, run_readonly
except ModuleNotFoundError:
    from scripts.phatgpt_capability_inventory import CAPABILITY_TARGETS, memory_recall, run_readonly


EXPERIMENTS_ROOT = Path("/home/graham/workspace/experiments")


def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def inspect_repo_file(root: Path, relative: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
    path = root / relative
    commands.append(run_readonly(["test", "-e", str(path)], root))
    summary: dict[str, Any] = {
        "path": relative,
        "exists": path.exists(),
        "kind": "directory" if path.is_dir() else ("file" if path.is_file() else "missing"),
    }
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")
        summary["line_count"] = len(text.splitlines())
        summary["excerpt"] = "\n".join(text.splitlines()[:20])[:1500]
    return summary


def inspect_local_context(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for target in CAPABILITY_TARGETS:
        if target["domain"] not in {"embry_os", "sparta_qra", "graph_memory", "agent_skills"}:
            continue
        path_summaries = []
        for path in target["paths"]:
            path = Path(path)
            commands.append(run_readonly(["test", "-e", str(path)], EXPERIMENTS_ROOT))
            markers: list[str] = []
            if path.exists() and path.is_dir():
                for marker in ("README.md", "PROJECT_KNOWLEDGE.md", "AGENTS.md", "pyproject.toml", ".ingest-code.json"):
                    marker_path = path / marker
                    if marker_path.exists():
                        markers.append(str(marker_path))
            path_summaries.append(
                {
                    "path": str(path),
                    "exists": path.exists(),
                    "type": "directory" if path.is_dir() else ("file" if path.is_file() else "missing"),
                    "markers": markers,
                }
            )
        summaries.append({"domain": target["domain"], "paths": path_summaries})
    return summaries


def collect_stress_test_plan(root: Path, artifact_root: Path, kind: str, number: int) -> tuple[Path, list[dict[str, Any]]]:
    commands: list[dict[str, Any]] = []
    out_dir = artifact_root / f"{kind}-{number}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "stress-test-plan.json"

    repo_files = [
        "goals/current.json",
        "controller-state/current.json",
        "queue-state/current.json",
        "PROJECT_KNOWLEDGE.md",
        "README.md",
        "scripts/phatgpt_local_worker_cycle.py",
        "scripts/phatgpt_subagent_selector.py",
        "scripts/phatgpt_deployer_cycle.py",
    ]
    files_inspected = [inspect_repo_file(root, relative, commands) for relative in repo_files]
    memory_queries = [
        "Embry OS UX Lab QuerySpec SPARTA Explorer greenfield task",
        "ingest-sparta sparta explorer pipeline ux-lab memory task-monitor",
        "PhatGPT-LAB subagent coder reviewer deployer stress test",
    ]
    memory_recalls = [memory_recall(query) for query in memory_queries]
    local_context = inspect_local_context(commands)

    try:
        result = subprocess.run(
            [
                "python3",
                "scripts/phatgpt_subagent_selector.py",
                "--task",
                "Implement the next bounded PhatGPT stress-test coder task after researcher planning",
                "--with-memory",
                "--json",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        commands.append(
            {
                "command": "python3 scripts/phatgpt_subagent_selector.py --task <stress task> --with-memory --json",
                "exit_code": result.returncode,
                "stdout": result.stdout[:4000],
                "stderr": result.stderr[:2000],
            }
        )
        selector = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else {}
    except Exception as exc:  # pragma: no cover - fail-closed metadata path
        selector = {"status": "UNAVAILABLE", "reason": repr(exc)}

    plan = {
        "schema": "chatgpt_lab.stress_test_plan.v1",
        "target": f"{kind}#{number}",
        "generated_at": now(),
        "main_commit_context": "c9472f78d5c0e00f7323360328169a343a827fb2",
        "purpose": "Use PhatGPT-LAB to drive a greenfield Embry OS / SPARTA Explorer task through GitHub-visible researcher, coder, reviewer, and deployer lanes.",
        "control_plane_invariants_to_stress": [
            {
                "invariant": "required_outputs_are_real_artifacts",
                "stress": "Researcher and coder must not mark COMPLETED unless declared artifacts exist and are listed in receipts.",
            },
            {
                "invariant": "next_subagent_is_explicit_and_label_backed",
                "stress": "Every handoff must identify exactly one next subagent and the corresponding GitHub label must match.",
            },
            {
                "invariant": "release_gate_is_evidence_based_not_advisory_check_based",
                "stress": "Deployer should gate on configured required checks and receipt evidence, while long-running advisory checks cannot create false blockers.",
            },
            {
                "invariant": "local_context_is_verified_before_coding",
                "stress": "Local Embry OS / SPARTA / UX Lab context must be inspected through researcher artifacts before coder mutates repo files.",
            },
        ],
        "recommended_greenfield_direction": {
            "name": "Embry OS / SPARTA Explorer QuerySpec stress slice",
            "summary": "Create a repo-local, read-only fixture that captures a single QuerySpec-style task contract for SPARTA Explorer and validates routing through the PhatGPT harness before any product implementation.",
        },
        "next_bounded_coder_task": {
            "title": "Add stress fixture and validator for Embry OS / SPARTA Explorer QuerySpec handoff",
            "next_agent": "coder",
            "objective": "Add a small JSON fixture and validator that prove the control plane can represent an Embry OS / SPARTA Explorer task without touching the external projects.",
            "allowed_paths": [
                "examples/stress/embry-sparta-queryspec-task.json",
                "schemas/stress-test-plan.schema.json",
                "scripts/validate_stress_fixtures.py",
                "tests/test_stress_fixtures.py",
                "docs/operations/PHATGPT_STRESS_TESTS.md",
            ],
            "validation_commands": [
                "python3 scripts/validate_control_plane.py",
                "python3 scripts/validate_stress_fixtures.py",
                "python3 -m unittest discover -s tests",
            ],
        },
        "next_subagent": {
            "name": "coder",
            "reason": "The researcher artifact has reduced the next step to a bounded repo-local fixture/validator task.",
        },
        "files_inspected": files_inspected,
        "local_context_sources": local_context,
        "memory_recalls": memory_recalls,
        "subagent_selector": selector,
        "commands_run": commands,
    }
    out_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path, commands


__all__ = ["collect_stress_test_plan"]
