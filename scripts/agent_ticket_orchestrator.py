#!/usr/bin/env python3
"""No-mutation orchestrator dry-run for GitHub ticket routing."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from agent_ticket_route import ROOT, route_fixture
from goal_contracts import load_json


def _label_names(labels: Any) -> list[str]:
    if not isinstance(labels, list):
        return []
    names: list[str] = []
    for label in labels:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            names.append(label["name"])
    return names


def _login(author: Any) -> str:
    if isinstance(author, dict) and isinstance(author.get("login"), str):
        return author["login"]
    if isinstance(author, str):
        return author
    return ""


def github_json_to_thread_fixture(kind: str, data: dict[str, Any]) -> dict[str, Any]:
    comments = []
    for comment in data.get("comments") or []:
        if not isinstance(comment, dict):
            continue
        comments.append(
            {
                "id": int(comment.get("id") or comment.get("databaseId") or 1),
                "author": _login(comment.get("author")),
                "author_association": str(comment.get("authorAssociation") or "UNKNOWN"),
                "created_at": str(comment.get("createdAt") or ""),
                "body": str(comment.get("body") or ""),
            }
        )
    return {
        "schema": "chatgpt_lab.github_thread_fixture.v1",
        "kind": "pr" if kind == "pr" else "issue",
        "number": int(data.get("number")),
        "title": str(data.get("title") or ""),
        "author": _login(data.get("author")),
        "labels": _label_names(data.get("labels")),
        "body": str(data.get("body") or ""),
        "comments": comments,
    }


def fetch_github_thread(repo: str, kind: str, number: int) -> dict[str, Any]:
    command_kind = "pr" if kind == "pr" else "issue"
    fields = "number,title,author,labels,body,comments"
    result = subprocess.run(
        ["gh", command_kind, "view", str(number), "--repo", repo, "--json", fields],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh view failed")
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise ValueError("gh view did not return a JSON object")
    return github_json_to_thread_fixture(command_kind, value)


def route_thread(fixture: dict[str, Any], active_goal: dict[str, Any], trusted_humans: set[str]) -> dict[str, Any]:
    decision = route_fixture(fixture, active_goal, trusted_humans)
    decision["orchestrator"] = {
        "schema": "chatgpt_lab.orchestrator_dry_run.v1",
        "mode": "dry_run",
        "would_mutate": False,
        "source": "github_state",
    }
    return decision


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="grahama1970/chatgpt-lab")
    parser.add_argument("--kind", choices=["issue", "pr"], required=True)
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--active-goal", type=Path, default=ROOT / "goals/current.json")
    parser.add_argument("--trusted-human", action="append", default=["grahama1970"])
    parser.add_argument(
        "--thread-json",
        type=Path,
        help="Read a saved gh issue/pr JSON object instead of calling gh.",
    )
    args = parser.parse_args()

    try:
        active_goal = load_json(args.active_goal)
        if args.thread_json:
            data = load_json(args.thread_json)
            fixture = github_json_to_thread_fixture(args.kind, data)
        else:
            fixture = fetch_github_thread(args.repo, args.kind, args.number)
        decision = route_thread(fixture, active_goal, set(args.trusted_human))
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
        decision = {
            "schema": "chatgpt_lab.route_decision.v1",
            "status": "REFUSED",
            "mode": "dry_run",
            "would_mutate": False,
            "source": {
                "kind": args.kind,
                "number": args.number,
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
            "reason": "unable_to_read_github_thread",
            "next_required_action": "Fetchable GitHub issue or PR state is required for dry-run routing.",
            "reasons": [],
            "missing": [],
            "errors": [str(exc)],
            "orchestrator": {
                "schema": "chatgpt_lab.orchestrator_dry_run.v1",
                "mode": "dry_run",
                "would_mutate": False,
                "source": "github_state",
            },
        }
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["status"] in {"ROUTE", "NOOP"} else 1


if __name__ == "__main__":
    sys.exit(main())
