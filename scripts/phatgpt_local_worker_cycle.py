#!/usr/bin/env python3
"""Short-lived PhatGPT-LAB local worker cycle.

The worker is intentionally fail-closed. It inspects one GitHub issue or pull
request, requires a structured phatgpt-task:v1 JSON block, writes a receipt, and
exits. This first slice validates and refuses; it does not patch source code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_pr_local_task import validate_task

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "local-worker"
RECEIPT_SCHEMA = "chatgpt_lab.local_subagent_receipt.v1"
TASK_SCHEMA = "chatgpt_lab.pr_local_task.v1"
DEFAULT_REPO = "grahama1970/chatgpt-lab"
DEFAULT_LABEL = "phatgpt-local-agent"
ROLE_LABELS = {
    "coder": "phatgpt-local-agent",
    "reviewer": "phatgpt-ready-for-review",
    "researcher": "phatgpt-needs-task",
}


def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout, result.stderr


def command_record(args: list[str], exit_code: int) -> dict[str, Any]:
    return {
        "command": " ".join(args),
        "exit_code": exit_code,
    }


def load_gh_json(kind: str, number: int, repo: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if kind == "pr":
        args = [
            "gh",
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,body,labels,headRefName,headRefOid,url,state,isDraft",
        ]
    else:
        args = [
            "gh",
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,body,labels,url,state",
        ]
    exit_code, stdout, stderr = run_command(args)
    record = command_record(args, exit_code)
    record["stderr"] = stderr.strip()
    if exit_code != 0:
        return None, record
    try:
        return json.loads(stdout), record
    except json.JSONDecodeError as exc:
        record["stderr"] = f"invalid gh JSON: {exc}"
        return None, record


def discover_target(kind: str, repo: str, label: str) -> tuple[int | None, dict[str, Any]]:
    if kind == "pr":
        args = [
            "gh",
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            label,
            "--limit",
            "1",
            "--json",
            "number",
        ]
    else:
        args = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            label,
            "--limit",
            "1",
            "--json",
            "number",
        ]
    exit_code, stdout, stderr = run_command(args)
    record = command_record(args, exit_code)
    record["stderr"] = stderr.strip()
    if exit_code != 0:
        return None, record
    try:
        targets = json.loads(stdout)
    except json.JSONDecodeError as exc:
        record["stderr"] = f"invalid gh JSON: {exc}"
        return None, record
    if not isinstance(targets, list) or not targets:
        return None, record
    first = targets[0]
    if not isinstance(first, dict) or not isinstance(first.get("number"), int):
        record["stderr"] = "gh JSON did not contain a numeric target number"
        return None, record
    return first["number"], record


def extract_task(body: str) -> tuple[dict[str, Any] | None, str | None]:
    patterns = [
        r"<!--\s*phatgpt-task:v1\s*(?P<json>\{.*?\})\s*-->",
        r"```json\s*(?P<json>\{.*?\"schema\"\s*:\s*\"chatgpt_lab\.pr_local_task\.v1\".*?\})\s*```",
    ]
    for pattern in patterns:
        match = re.search(pattern, body, flags=re.DOTALL)
        if not match:
            continue
        raw = match.group("json")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, f"invalid_json_task_block: {exc}"
        if value.get("schema") == TASK_SCHEMA:
            return value, None
    return None, "missing_structured_task_block"


def labels_from(item: dict[str, Any]) -> set[str]:
    labels = item.get("labels") or []
    values: set[str] = set()
    for label in labels:
        if isinstance(label, dict) and isinstance(label.get("name"), str):
            values.add(label["name"])
    return values


def expected_missing_for_no_task() -> list[str]:
    return [
        "phatgpt-task:v1 structured task block",
        "allowed_commands",
        "allowed_paths",
        "validation_commands",
        "expected_evidence",
        "stop_condition",
    ]


def write_receipt(
    *,
    role: str,
    kind: str,
    number: int,
    task_id: str,
    status: str,
    reason: str | None,
    missing: list[str],
    next_required_action: str | None,
    commands_run: list[dict[str, Any]],
    target: dict[str, Any] | None,
) -> Path:
    completed_at = now()
    slug = f"{kind}-{number}"
    out_dir = ARTIFACT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = out_dir / "local-subagent-receipt.json"
    target_path = out_dir / "target.json"
    manifest_path = out_dir / "artifact-manifest.json"

    if target is not None:
        target_path.write_text(json.dumps(target, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    artifacts = [
        str(receipt_path.relative_to(ROOT)),
        str(manifest_path.relative_to(ROOT)),
    ]
    if target is not None:
        artifacts.append(str(target_path.relative_to(ROOT)))

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "role": role,
        "task_id": task_id,
        "status": status,
        "reason": reason,
        "missing": missing,
        "next_required_action": next_required_action,
        "commands_run": commands_run,
        "files_touched": [],
        "artifacts": artifacts,
        "started_at": completed_at,
        "completed_at": completed_at,
    }
    manifest = {
        "schema": "chatgpt_lab.local_worker_artifact_manifest.v1",
        "role": role,
        "target": f"{kind}#{number}",
        "receipt": str(receipt_path.relative_to(ROOT)),
        "artifacts": artifacts,
        "generated_at": completed_at,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt_path


def maybe_comment(repo: str, kind: str, number: int, receipt_path: Path, enabled: bool) -> dict[str, Any] | None:
    if not enabled:
        return None
    body = (
        "PhatGPT local worker receipt\n\n"
        f"- target: `{kind}#{number}`\n"
        f"- receipt: `{receipt_path.relative_to(ROOT)}`\n\n"
        "The local worker did not execute product-code changes in this slice."
    )
    args = ["gh", kind, "comment", str(number), "--repo", repo, "--body", body]
    exit_code, _, stderr = run_command(args)
    return {
        "command": " ".join(args),
        "exit_code": exit_code,
        "stderr": stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--role", choices=sorted(ROLE_LABELS), default="coder")
    parser.add_argument("--target-kind", choices=["pr", "issue"], default="pr")
    parser.add_argument("--max-targets", type=int, default=1)
    parser.add_argument("--label")
    parser.add_argument("--allow-unlabeled", action="store_true")
    parser.add_argument("--comment", action="store_true")
    args = parser.parse_args()

    if args.max_targets != 1:
        print("this MVP worker supports exactly --max-targets 1", file=sys.stderr)
        return 2

    if args.label is None:
        args.label = ROLE_LABELS.get(args.role, DEFAULT_LABEL)

    explicit_target = bool(args.pr) or bool(args.issue)
    if args.pr and args.issue:
        print("provide at most one of --pr or --issue", file=sys.stderr)
        return 2

    commands_run: list[dict[str, Any]] = []
    if explicit_target:
        kind = "pr" if args.pr else "issue"
        number = args.pr or args.issue
        assert number is not None
    else:
        kind = args.target_kind
        number, discover_record = discover_target(kind, args.repo, args.label)
        commands_run.append(discover_record)
        if number is None:
            receipt = write_receipt(
                role=args.role,
                kind=kind,
                number=0,
                task_id=f"{args.role}-{kind}-no-target",
                status="REFUSED",
                reason="no_eligible_target",
                missing=[args.label],
                next_required_action=f"Create or label one open {kind} with `{args.label}`.",
                commands_run=commands_run,
                target=None,
            )
            print(json.dumps({"status": "REFUSED", "reason": "no_eligible_target", "receipt": str(receipt)}, indent=2))
            return 0

    item, record = load_gh_json(kind, number, args.repo)
    commands_run.append(record)
    if item is None:
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-lookup",
            status="FAILED",
            reason="github_lookup_failed",
            missing=[],
            next_required_action="Check gh authentication, repository access, and target number.",
            commands_run=commands_run,
            target=None,
        )
        print(json.dumps({"status": "FAILED", "receipt": str(receipt)}, indent=2))
        return 1

    label_names = labels_from(item)
    if args.label not in label_names and not args.allow_unlabeled:
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-unleased",
            status="REFUSED",
            reason="missing_required_label",
            missing=[args.label],
            next_required_action=f"Add label `{args.label}` or rerun with --allow-unlabeled for manual diagnostics.",
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": "missing_required_label", "receipt": str(receipt)}, indent=2))
        return 0

    task, task_error = extract_task(item.get("body") or "")
    if task is None:
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-missing-task",
            status="REFUSED",
            reason=task_error or "missing_structured_task_block",
            missing=expected_missing_for_no_task(),
            next_required_action="WebGPT must update the PR/issue body with a structured phatgpt-task:v1 JSON block.",
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": task_error, "receipt": str(receipt)}, indent=2))
        return 0

    validation_errors = validate_task(task)
    if validation_errors:
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=str(task.get("task_id") or f"{kind}-{number}-invalid-task"),
            status="REFUSED",
            reason="task_not_implementation_ready",
            missing=validation_errors,
            next_required_action="WebGPT must repair the structured phatgpt-task:v1 block before local execution.",
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": "task_not_implementation_ready", "receipt": str(receipt)}, indent=2))
        return 0

    receipt = write_receipt(
        role=args.role,
        kind=kind,
        number=number,
        task_id=str(task["task_id"]),
        status="COMPLETED",
        reason="task_contract_validated",
        missing=[],
        next_required_action="Enable bounded execution in a later slice; this slice validates and records the task contract only.",
        commands_run=commands_run,
        target=item,
    )
    print(json.dumps({"status": "COMPLETED", "receipt": str(receipt)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
