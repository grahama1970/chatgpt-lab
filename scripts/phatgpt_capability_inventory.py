#!/usr/bin/env python3
"""Collect a read-only PhatGPT local capability inventory.

The researcher worker uses this primitive when a GitHub task asks for local
context that WebGPT cannot inspect directly. It recalls memory first, validates
known local paths with read-only checks, scans agent contracts for evidence-gate
risk patterns, and writes one deterministic JSON artifact.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MEMORY_URL = "http://127.0.0.1:8601"
MEMORY_COLLECTIONS = [
    "workspace_locations",
    "project_knowledge",
    "code_symbols",
    "subagent_memory",
    "subagent_approval_registry",
    "lessons",
]
EXPERIMENTS_ROOT = Path("/home/graham/workspace/experiments")
AGENT_ROOT = EXPERIMENTS_ROOT / "agent-skills" / "agents"
SKILL_ROOT = EXPERIMENTS_ROOT / "agent-skills" / "skills"

CAPABILITY_TARGETS = [
    {
        "domain": "f36_plant",
        "queries": ["F36 plant local project capability", "ops-f36-plant skill contract"],
        "paths": [SKILL_ROOT / "ops-f36-plant"],
    },
    {
        "domain": "embry_os",
        "queries": ["Embry OS local project capability", "Embry agent configuration capability"],
        "paths": [
            EXPERIMENTS_ROOT / "embry-os",
            SKILL_ROOT / "ops-embry-agent",
            SKILL_ROOT / "embry-config",
        ],
    },
    {
        "domain": "pdf_lab",
        "queries": ["pdf-lab local capability", "PDF lab artifacts and review workflow"],
        "paths": [SKILL_ROOT / "pdf-lab"],
    },
    {
        "domain": "sparta_qra",
        "queries": ["SPARTA QRA local capability", "SPARTA review agent capability"],
        "paths": [
            EXPERIMENTS_ROOT / "sparta",
            SKILL_ROOT / "sparta-qra-validator-gpt",
            SKILL_ROOT / "sparta-review",
        ],
    },
    {
        "domain": "lean4",
        "queries": ["Lean4 proof local capability", "lean4-prove skill contract"],
        "paths": [EXPERIMENTS_ROOT / "lean4", SKILL_ROOT / "lean4-prove"],
    },
    {
        "domain": "graph_memory",
        "queries": ["graph memory local capability", "memory recall subagent registry"],
        "paths": [EXPERIMENTS_ROOT / "memory", SKILL_ROOT / "memory"],
    },
    {
        "domain": "watch",
        "queries": ["watch agent local capability", "watch skill contract"],
        "paths": [SKILL_ROOT / "watch", AGENT_ROOT / "watch"],
    },
    {
        "domain": "agent_skills",
        "queries": ["agent-skills agents registry local capability", "subagent evidence receipt contracts"],
        "paths": [EXPERIMENTS_ROOT / "agent-skills", AGENT_ROOT],
    },
]


def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_readonly(args: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    record: dict[str, Any] = {"command": " ".join(str(arg) for arg in args), "exit_code": result.returncode}
    if result.stdout.strip():
        record["stdout"] = result.stdout.strip()[:4000]
    if result.stderr.strip():
        record["stderr"] = result.stderr.strip()[:2000]
    return record


def compact_memory_item(item: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {
        "key": item.get("_key"),
        "source": item.get("_source"),
    }
    for key in ("problem", "solution", "title", "path", "project", "text"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            compact[key] = value.strip()[:500]
    scores = item.get("scores")
    if isinstance(scores, dict):
        compact["scores"] = {key: scores.get(key) for key in ("bm25", "dense", "graph", "freshness") if key in scores}
    return compact


def memory_recall(query: str) -> dict[str, Any]:
    try:
        import httpx

        with httpx.Client(base_url=MEMORY_URL, timeout=httpx.Timeout(10.0, connect=2.0)) as client:
            response = client.post(
                "/recall",
                json={"q": query, "k": 4, "collections": MEMORY_COLLECTIONS},
            )
            response.raise_for_status()
            data = response.json()
    except ModuleNotFoundError:
        payload = json.dumps({"q": query, "k": 4, "collections": MEMORY_COLLECTIONS}).encode("utf-8")
        request = urllib.request.Request(
            f"{MEMORY_URL}/recall",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10.0) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            return {
                "query": query,
                "status": "UNAVAILABLE",
                "reason": str(exc),
                "items": [],
            }
    except Exception as exc:
        return {
            "query": query,
            "status": "UNAVAILABLE",
            "reason": str(exc),
            "items": [],
        }
    return {
        "query": query,
        "status": "FOUND" if data.get("found") else "NO_MATCH",
        "confidence": data.get("confidence"),
        "should_scan": data.get("should_scan"),
        "items": [
            compact_memory_item(item)
            for item in (data.get("items") or [])[:4]
            if isinstance(item, dict)
        ],
    }


def inspect_path(path: Path, commands: list[dict[str, Any]]) -> dict[str, Any]:
    commands.append(run_readonly(["test", "-e", str(path)], EXPERIMENTS_ROOT))
    exists = path.exists()
    summary: dict[str, Any] = {
        "path": str(path),
        "exists": exists,
        "type": "directory" if path.is_dir() else ("file" if path.is_file() else "missing"),
        "markers": [],
    }
    if not exists:
        return summary
    for marker in ("AGENTS.md", "SKILL.md", "README.md", "PROJECT_KNOWLEDGE.md", "pyproject.toml", ".ingest-code.json"):
        marker_path = path / marker if path.is_dir() else path.parent / marker
        if marker_path.exists():
            summary["markers"].append(str(marker_path))
    if path.is_dir():
        commands.append(run_readonly(["find", str(path), "-maxdepth", "2", "-type", "f"], EXPERIMENTS_ROOT))
    return summary


def scan_agent_contract_evidence_risks(commands: list[dict[str, Any]]) -> dict[str, Any]:
    if not AGENT_ROOT.is_dir():
        return {"status": "UNAVAILABLE", "reason": "agent root missing", "matches": []}
    command = [
        "rg",
        "-n",
        "task_contract_validated|COMPLETED|completed|required_outputs|receipt|evidence",
        str(AGENT_ROOT),
        "-g",
        "AGENTS.md",
        "-g",
        "persona.yaml",
    ]
    commands.append(run_readonly(command, EXPERIMENTS_ROOT))
    matches: list[dict[str, Any]] = []
    for path in sorted(AGENT_ROOT.glob("*/persona.yaml")):
        text = path.read_text(encoding="utf-8", errors="replace")
        risk_terms = []
        if "COMPLETED" in text or "completed" in text:
            risk_terms.append("completion_language")
        if "required_outputs" not in text and "artifact_contract" not in text and "receipt" in text:
            risk_terms.append("receipt_without_required_outputs_contract")
        if risk_terms:
            matches.append({"agent": path.parent.name, "path": str(path), "risk_terms": risk_terms})
    return {
        "status": "COMPLETED",
        "scope": str(AGENT_ROOT),
        "matches": matches[:50],
        "match_count": len(matches),
    }


def collect_capability_inventory(root: Path, artifact_root: Path, kind: str, number: int) -> tuple[Path, list[dict[str, Any]]]:
    commands: list[dict[str, Any]] = []
    out_dir = artifact_root / f"{kind}-{number}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "capability-inventory.json"

    capabilities = []
    for target in CAPABILITY_TARGETS:
        recalls = [memory_recall(query) for query in target["queries"]]
        path_summaries = [inspect_path(Path(path), commands) for path in target["paths"]]
        available_paths = [item["path"] for item in path_summaries if item["exists"]]
        capabilities.append(
            {
                "domain": target["domain"],
                "status": "AVAILABLE" if available_paths else "MISSING_OR_UNVERIFIED",
                "memory_recalls": recalls,
                "paths": path_summaries,
                "summary": (
                    f"{target['domain']} has {len(available_paths)} validated local path(s)."
                    if available_paths
                    else f"{target['domain']} was not validated locally from known paths."
                ),
            }
        )

    agent_scan = scan_agent_contract_evidence_risks(commands)
    inventory = {
        "schema": "chatgpt_lab.capability_inventory.v1",
        "target": f"{kind}#{number}",
        "generated_at": now(),
        "strategy": "memory_first_then_live_read_only_path_validation",
        "capabilities": capabilities,
        "agent_contract_evidence_scan": agent_scan,
        "recommended_next_task": {
            "title": "Add researcher inventory collection as a reusable primitive after one live issue proof",
            "next_agent": "reviewer",
            "reason": "The current artifact should be reviewed before promotion into agent-skills.",
        },
        "intended_next_agent": "reviewer",
        "receipt_path": str((out_dir / "local-subagent-receipt.json").relative_to(root)),
        "commands_run": commands,
    }
    out_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path, commands


__all__ = ["collect_capability_inventory"]
