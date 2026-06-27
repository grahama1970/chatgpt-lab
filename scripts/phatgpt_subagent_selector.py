#!/usr/bin/env python3
"""Select PhatGPT-LAB subagent lanes from live agent contracts.

The agent registry on disk is authoritative for available subagents. Memory may
recall prior routing lessons, but it is not the source of truth for what a
subagent is allowed to do.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_AGENT_ROOT = Path("/home/graham/workspace/experiments/agent-skills/agents")
MEMORY_URL = "http://127.0.0.1:8601/recall"

ROLE_CONFIG = {
    "phatgpt-deployer": {
        "priority": 10,
        "name": "deployer",
        "role": "deployer",
        "kind": "pr",
        "label": "phatgpt-ready-to-deploy",
        "command": [
            "python3",
            "scripts/phatgpt_deployer_cycle.py",
            "--repo",
            "{repo}",
            "--label",
            "{label}",
            "--dry-run",
            "--comment",
        ],
    },
    "phatgpt-reviewer": {
        "priority": 20,
        "name": "reviewer",
        "role": "reviewer",
        "kind": "pr",
        "label": "phatgpt-ready-for-review",
        "command": [
            "python3",
            "scripts/phatgpt_local_worker_cycle.py",
            "--repo",
            "{repo}",
            "--role",
            "reviewer",
            "--target-kind",
            "pr",
            "--label",
            "{label}",
            "--comment",
        ],
    },
    "phatgpt-coder": {
        "priority": 30,
        "name": "coder",
        "role": "coder",
        "kind": "pr",
        "label": "phatgpt-local-agent",
        "command": [
            "python3",
            "scripts/phatgpt_local_worker_cycle.py",
            "--repo",
            "{repo}",
            "--role",
            "coder",
            "--target-kind",
            "pr",
            "--label",
            "{label}",
            "--comment",
        ],
    },
    "phatgpt-researcher": {
        "priority": 40,
        "name": "researcher-issue",
        "role": "researcher",
        "kind": "issue",
        "label": "phatgpt-needs-task",
        "command": [
            "python3",
            "scripts/phatgpt_local_worker_cycle.py",
            "--repo",
            "{repo}",
            "--role",
            "researcher",
            "--target-kind",
            "issue",
            "--label",
            "{label}",
            "--comment",
        ],
    },
}


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    match = re.match(r"---\n(?P<body>.*?)\n---", text, flags=re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_contracts(agent_root: Path = DEFAULT_AGENT_ROOT) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    if not agent_root.is_dir():
        return contracts
    for agent_dir in sorted(agent_root.iterdir()):
        contract_path = agent_dir / "AGENTS.md"
        if not contract_path.is_file():
            continue
        frontmatter = read_frontmatter(contract_path)
        agent_id = frontmatter.get("id") or agent_dir.name
        contracts.append(
            {
                "id": agent_id,
                "path": str(contract_path),
                "directory": str(agent_dir),
                "title": frontmatter.get("title", agent_id),
                "kind": frontmatter.get("kind", ""),
                "mode": frontmatter.get("mode", ""),
                "surface": frontmatter.get("surface", ""),
                "services": str(agent_dir / "services.yaml") if (agent_dir / "services.yaml").is_file() else None,
                "persona": str(agent_dir / "persona.yaml") if (agent_dir / "persona.yaml").is_file() else None,
            }
        )
    return contracts


def build_lanes(agent_root: Path = DEFAULT_AGENT_ROOT) -> list[dict[str, Any]]:
    contracts = {contract["id"]: contract for contract in load_contracts(agent_root)}
    lanes: list[dict[str, Any]] = []
    for agent_id, config in ROLE_CONFIG.items():
        contract = contracts.get(agent_id)
        if not contract:
            continue
        lane = dict(config)
        lane["agent_id"] = agent_id
        lane["contract_path"] = contract["path"]
        lane["agent_directory"] = contract["directory"]
        lane["selector_source"] = "agent-skills/agents"
        lanes.append(lane)
        if agent_id == "phatgpt-researcher":
            pr_lane = dict(lane)
            pr_lane["priority"] = 41
            pr_lane["name"] = "researcher-pr"
            pr_lane["kind"] = "pr"
            pr_lane["command"] = [
                "python3",
                "scripts/phatgpt_local_worker_cycle.py",
                "--repo",
                "{repo}",
                "--role",
                "researcher",
                "--target-kind",
                "pr",
                "--label",
                "{label}",
                "--comment",
            ]
            lanes.append(pr_lane)
    return sorted(lanes, key=lambda lane: int(lane["priority"]))


def memory_recall_subagent(task: str, timeout_seconds: float = 2.0) -> dict[str, Any]:
    """Ask memory for advisory subagent routing evidence.

    Memory is not authoritative. Callers must validate any suggested subagent
    against the live agent registry returned by build_lanes().
    """
    if not task.strip():
        return {
            "schema": "chatgpt_lab.memory_subagent_recall.v1",
            "status": "SKIPPED",
            "reason": "empty_task",
            "suggested_subagent": None,
            "items": [],
        }
    payload = json.dumps(
        {
            "q": f"For this PhatGPT-LAB task, which subagent should handle it? Task: {task}",
            "k": 5,
            "collections": ["subagent_memory", "subagent_approval_registry", "project_knowledge", "lessons"],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        MEMORY_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "schema": "chatgpt_lab.memory_subagent_recall.v1",
            "status": "UNAVAILABLE",
            "reason": str(exc),
            "suggested_subagent": None,
            "items": [],
        }

    return {
        "schema": "chatgpt_lab.memory_subagent_recall.v1",
        "status": "FOUND" if data.get("found") else "NO_MATCH",
        "confidence": data.get("confidence"),
        "should_scan": data.get("should_scan"),
        "items": data.get("items", [])[:5],
    }


def recommend_subagent(task: str, memory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Recommend a subagent for a natural-language task.

    This is deliberately simple and auditable. Memory is attached as evidence,
    but keyword intent keeps broad project-knowledge records from voting for a
    role just because they mention every role.
    """
    normalized = task.lower()
    if any(word in normalized for word in ["deploy", "release", "merge", "pages proof", "ready-to-deploy"]):
        agent = "phatgpt-deployer"
        reason = "release_or_deploy_gate_task"
    elif any(word in normalized for word in ["review", "verify", "validate", "pass/fail", "read-only", "read only"]):
        agent = "phatgpt-reviewer"
        reason = "read_only_review_or_validation_task"
    elif any(word in normalized for word in ["implement", "edit", "change", "patch", "code", "fix", "mutate"]):
        agent = "phatgpt-coder"
        reason = "bounded_code_mutation_task"
    elif any(word in normalized for word in ["research", "inventory", "inspect", "prepare", "task block", "local context"]):
        agent = "phatgpt-researcher"
        reason = "research_or_task_preparation_task"
    else:
        agent = "phatgpt-researcher"
        reason = "ambiguous_task_defaults_to_researcher_for_refusal_or_task_contract"

    return {
        "schema": "chatgpt_lab.subagent_recommendation.v1",
        "task": task,
        "recommended_subagent": agent,
        "reason": reason,
        "memory_status": (memory or {}).get("status"),
        "memory_confidence": (memory or {}).get("confidence"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-root", type=Path, default=Path(os.environ.get("PHATGPT_AGENT_ROOT", DEFAULT_AGENT_ROOT)))
    parser.add_argument("--task", default="")
    parser.add_argument("--with-memory", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    lanes = build_lanes(args.agent_root)
    memory = memory_recall_subagent(args.task) if args.with_memory else None
    recommendation = recommend_subagent(args.task, memory) if args.task else None
    known_agent_ids = {lane["agent_id"] for lane in lanes}
    recommendation_valid = (
        recommendation is not None
        and recommendation.get("recommended_subagent") in known_agent_ids
    )
    payload = {
        "schema": "chatgpt_lab.phatgpt_subagent_selector.v1",
        "agent_root": str(args.agent_root),
        "memory_role": "advisory_task_to_subagent_recall_only",
        "memory": memory,
        "recommendation": recommendation,
        "recommendation_valid": recommendation_valid if recommendation is not None else None,
        "lane_count": len(lanes),
        "lanes": lanes,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for lane in lanes:
            print(f"{lane['priority']:02d} {lane['name']} {lane['kind']} {lane['label']} {lane['contract_path']}")
    return 0 if lanes else 1


if __name__ == "__main__":
    raise SystemExit(main())
