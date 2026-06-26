#!/usr/bin/env python3
"""Start a GitHub Copilot cloud-agent task for a bounded issue.

This script is intentionally narrow. It reads one GitHub issue, sends its title
and body to the public-preview Agent Tasks API, and writes
agent-state/last-result.json so failures become durable control-plane evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "agent-state/last-result.json"
STDOUT_PATH = ROOT / "stdout.txt"
STDERR_PATH = ROOT / "stderr.txt"
API_VERSION = "2022-11-28"
WORKFLOW_NAME = "assign-copilot-agent.yml"


def api_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("X-GitHub-Api-Version", API_VERSION)
    if payload is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"message": body}
        return exc.code, parsed


def write_receipt(
    *,
    command_id: str,
    status: str,
    stdout_payload: dict[str, Any],
    stderr_payload: dict[str, Any],
) -> None:
    stdout_text = json.dumps(stdout_payload, indent=2, sort_keys=True)
    stderr_text = json.dumps(stderr_payload, indent=2, sort_keys=True)
    STDOUT_PATH.write_text(stdout_text + "\n", encoding="utf-8")
    STDERR_PATH.write_text(stderr_text + "\n", encoding="utf-8")

    payload = {
        "schema": "chatgpt_lab.workflow_result.v1",
        "command_id": command_id,
        "status": status,
        "repository": os.environ.get("GITHUB_REPOSITORY", "grahama1970/chatgpt-lab"),
        "workflow": WORKFLOW_NAME,
        "run_id": int(os.environ["GITHUB_RUN_ID"]) if os.environ.get("GITHUB_RUN_ID") else None,
        "run_attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]) if os.environ.get("GITHUB_RUN_ATTEMPT") else None,
        "head_sha": os.environ.get("GITHUB_SHA"),
        "output_path": "agent-state/last-result.json",
        "stdout": stdout_text,
        "stderr": stderr_text,
        "checked_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


def classify_failure(status_code: int) -> str:
    if status_code in {401, 403}:
        return "BLOCKED_CLOUD_AGENT_AUTH"
    return "BLOCKED_CLOUD_AGENT_API"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--base-ref", default="main")
    parser.add_argument("--create-pull-request", action="store_true")
    parser.add_argument("--model", default="")
    args = parser.parse_args()

    repository = os.environ.get("GITHUB_REPOSITORY", "grahama1970/chatgpt-lab")
    command_id = f"copilot-agent-issue-{args.issue_number}"
    github_token = os.environ.get("GITHUB_TOKEN", "")
    task_token = os.environ.get("COPILOT_AGENT_TASK_TOKEN", "")

    if "/" not in repository:
        write_receipt(
            command_id=command_id,
            status="BLOCKED_CLOUD_AGENT_API",
            stdout_payload={},
            stderr_payload={"error": "GITHUB_REPOSITORY must be owner/repo", "repository": repository},
        )
        return 2

    owner, repo = repository.split("/", 1)

    if not task_token:
        write_receipt(
            command_id=command_id,
            status="BLOCKED_CLOUD_AGENT_AUTH",
            stdout_payload={},
            stderr_payload={
                "error": "missing COPILOT_AGENT_TASK_TOKEN",
                "required_secret": "COPILOT_AGENT_TASK_TOKEN",
                "note": "GitHub Agent Tasks API requires a user-to-server token; GITHUB_TOKEN is not sufficient.",
            },
        )
        return 2

    read_token = github_token or task_token
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{args.issue_number}"
    issue_status, issue = api_request("GET", issue_url, read_token)
    if issue_status >= 400:
        write_receipt(
            command_id=command_id,
            status=classify_failure(issue_status),
            stdout_payload={},
            stderr_payload={
                "error": "failed to read issue",
                "http_status": issue_status,
                "response": issue,
            },
        )
        return 2

    issue_title = str(issue.get("title", "")).strip()
    issue_body = str(issue.get("body", "")).strip()
    html_url = str(issue.get("html_url", "")).strip()
    prompt = (
        f"Implement GitHub issue #{args.issue_number}: {issue_title}\n\n"
        f"Issue URL: {html_url}\n\n"
        "Follow the issue exactly. Keep the change minimal. Do not broaden scope. "
        "Open a pull request and include exact files changed, validation commands, "
        "GitHub Actions run IDs, Pages proof run ID if applicable, and any blockers.\n\n"
        f"Issue body:\n{issue_body}\n"
    )

    task_payload: dict[str, Any] = {
        "prompt": prompt,
        "base_ref": args.base_ref,
        "create_pull_request": args.create_pull_request,
    }
    if args.model.strip():
        task_payload["model"] = args.model.strip()

    task_url = f"https://api.github.com/agents/repos/{owner}/{repo}/tasks"
    task_status, task_response = api_request("POST", task_url, task_token, task_payload)
    if task_status >= 400:
        write_receipt(
            command_id=command_id,
            status=classify_failure(task_status),
            stdout_payload={
                "issue_number": args.issue_number,
                "issue_url": html_url,
                "base_ref": args.base_ref,
                "create_pull_request": args.create_pull_request,
            },
            stderr_payload={
                "error": "failed to start Copilot cloud-agent task",
                "http_status": task_status,
                "response": task_response,
            },
        )
        return 2

    write_receipt(
        command_id=command_id,
        status="PASS",
        stdout_payload={
            "issue_number": args.issue_number,
            "issue_url": html_url,
            "base_ref": args.base_ref,
            "create_pull_request": args.create_pull_request,
            "task_response": task_response,
        },
        stderr_payload={},
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
