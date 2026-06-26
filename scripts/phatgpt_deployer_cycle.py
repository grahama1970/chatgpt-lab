#!/usr/bin/env python3
"""Dry-run PhatGPT-LAB deployer/releaser cycle.

The deployer is intentionally separate from the coder/reviewer worker. It is a
gate checker first: inspect exactly one PR, write a receipt, optionally comment,
and exit. The MVP defaults to dry-run and never edits source code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "deployer"
DEFAULT_REPO = "grahama1970/chatgpt-lab"
DEFAULT_LABEL = "phatgpt-ready-to-deploy"
PASS_LABEL = "phatgpt-pass"
DEPLOYING_LABEL = "phatgpt-deploying"
DEPLOYED_LABEL = "phatgpt-deployed"
DEPLOY_FAILED_LABEL = "phatgpt-deploy-failed"
BLOCKED_MERGE_LABEL = "phatgpt-blocked-merge"
RECEIPT_SCHEMA = "chatgpt_lab.deployer_receipt.v1"
DEFAULT_REQUIRED_CHECKS = (
    "validate-control-plane",
    "Benchmark evidence",
    "Build Pages artifact",
)


def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout, result.stderr


def command_record(args: list[str], exit_code: int, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    record: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": exit_code,
    }
    if stdout.strip():
        record["stdout"] = stdout.strip()
    if stderr.strip():
        record["stderr"] = stderr.strip()
    return record


def discover_pr(repo: str, label: str) -> tuple[int | None, dict[str, Any]]:
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
    exit_code, stdout, stderr = run_command(args)
    record = command_record(args, exit_code, stdout, stderr)
    if exit_code != 0:
        return None, record
    try:
        prs = json.loads(stdout)
    except json.JSONDecodeError as exc:
        record["stderr"] = f"invalid gh JSON: {exc}"
        return None, record
    if not isinstance(prs, list) or not prs:
        return None, record
    number = prs[0].get("number") if isinstance(prs[0], dict) else None
    return number if isinstance(number, int) else None, record


def load_pr(repo: str, number: int) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    args = [
        "gh",
        "pr",
        "view",
        str(number),
        "--repo",
        repo,
        "--json",
        "number,title,url,state,isDraft,labels,headRefName,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,reviewDecision,comments",
    ]
    exit_code, stdout, stderr = run_command(args)
    record = command_record(args, exit_code, stderr=stderr)
    if exit_code != 0:
        return None, record
    try:
        return json.loads(stdout), record
    except json.JSONDecodeError as exc:
        record["stderr"] = f"invalid gh JSON: {exc}"
        return None, record


def labels_from(pr: dict[str, Any]) -> set[str]:
    labels = pr.get("labels") or []
    return {
        label["name"]
        for label in labels
        if isinstance(label, dict) and isinstance(label.get("name"), str)
    }


def check_conclusions(pr: dict[str, Any]) -> dict[str, str]:
    conclusions: dict[str, str] = {}
    for check in pr.get("statusCheckRollup") or []:
        if not isinstance(check, dict):
            continue
        name = check.get("name")
        conclusion = check.get("conclusion")
        if isinstance(name, str):
            conclusions[name] = str(conclusion or check.get("status") or "")
    return conclusions


def has_reviewer_pass_comment(pr: dict[str, Any]) -> bool:
    for comment in pr.get("comments") or []:
        if not isinstance(comment, dict):
            continue
        body = str(comment.get("body") or "")
        if "PhatGPT reviewer receipt" in body and "review_pass" in body:
            return True
        if "PhatGPT reviewer verdict" in body and "`PASS`" in body:
            return True
        if "PhatGPT dispatcher" in body and "Verdict: PASS" in body:
            return True
    return False


def evaluate_pr(pr: dict[str, Any], required_checks: list[str]) -> tuple[str, list[str], dict[str, Any]]:
    missing: list[str] = []
    labels = labels_from(pr)
    checks = check_conclusions(pr)

    if pr.get("state") != "OPEN":
        missing.append("pr_state_open")
    if pr.get("isDraft"):
        missing.append("pr_not_draft")
    if DEFAULT_LABEL not in labels:
        missing.append(DEFAULT_LABEL)
    if PASS_LABEL not in labels:
        missing.append(PASS_LABEL)
    if pr.get("mergeStateStatus") != "CLEAN":
        missing.append("merge_state_clean")
    if pr.get("reviewDecision") == "CHANGES_REQUESTED":
        missing.append("no_blocking_review_decision")
    if not has_reviewer_pass_comment(pr):
        missing.append("reviewer_pass_comment")

    for check_name in required_checks:
        if checks.get(check_name) != "SUCCESS":
            missing.append(f"check_success:{check_name}")

    summary = {
        "labels": sorted(labels),
        "merge_state": pr.get("mergeStateStatus"),
        "review_decision": pr.get("reviewDecision"),
        "required_checks": {name: checks.get(name) for name in required_checks},
        "head_sha": pr.get("headRefOid"),
        "head_ref": pr.get("headRefName"),
        "base_ref": pr.get("baseRefName"),
        "reviewer_pass_comment": has_reviewer_pass_comment(pr),
    }
    return ("WOULD_MERGE" if not missing else "REFUSED"), missing, summary


def write_receipt(
    *,
    pr_number: int,
    status: str,
    reason: str,
    missing: list[str],
    next_required_action: str,
    commands_run: list[dict[str, Any]],
    pr: dict[str, Any] | None,
    gate_summary: dict[str, Any],
    dry_run: bool,
) -> Path:
    completed_at = now()
    out_dir = ARTIFACT_ROOT / f"pr-{pr_number}"
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = out_dir / "deployer-receipt.json"
    target_path = out_dir / "target.json"
    manifest_path = out_dir / "artifact-manifest.json"

    artifacts = [
        str(receipt_path.relative_to(ROOT)),
        str(manifest_path.relative_to(ROOT)),
    ]
    if pr is not None:
        target_path.write_text(json.dumps(pr, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        artifacts.append(str(target_path.relative_to(ROOT)))

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "role": "deployer",
        "target": f"pr#{pr_number}",
        "status": status,
        "reason": reason,
        "dry_run": dry_run,
        "missing": missing,
        "next_required_action": next_required_action,
        "head_sha": gate_summary.get("head_sha"),
        "head_ref": gate_summary.get("head_ref"),
        "base_ref": gate_summary.get("base_ref"),
        "gate_summary": gate_summary,
        "commands_run": commands_run,
        "files_touched": [],
        "artifacts": artifacts,
        "started_at": completed_at,
        "completed_at": completed_at,
    }
    manifest = {
        "schema": "chatgpt_lab.deployer_artifact_manifest.v1",
        "role": "deployer",
        "target": f"pr#{pr_number}",
        "receipt": str(receipt_path.relative_to(ROOT)),
        "artifacts": artifacts,
        "generated_at": completed_at,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt_path


def comment_body(status: str, reason: str, receipt_path: Path, missing: list[str], next_required_action: str) -> str:
    missing_lines = "\n".join(f"- `{item}`" for item in missing) or "- none"
    return (
        "PhatGPT deployer receipt\n\n"
        f"- status: `{status}`\n"
        f"- reason: `{reason}`\n"
        f"- receipt: `{receipt_path.relative_to(ROOT)}`\n"
        f"- next: `{next_required_action}`\n\n"
        "Missing gates:\n"
        f"{missing_lines}\n"
    )


def maybe_comment(repo: str, number: int, enabled: bool, status: str, reason: str, receipt_path: Path, missing: list[str], next_required_action: str) -> dict[str, Any] | None:
    if not enabled:
        return None
    args = [
        "gh",
        "pr",
        "comment",
        str(number),
        "--repo",
        repo,
        "--body",
        comment_body(status, reason, receipt_path, missing, next_required_action),
    ]
    exit_code, stdout, stderr = run_command(args)
    return command_record(args, exit_code, stdout, stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--max-targets", type=int, default=1)
    parser.add_argument("--required-check", action="append", dest="required_checks")
    parser.add_argument("--comment", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    if args.max_targets != 1:
        print("this MVP deployer supports exactly --max-targets 1", file=sys.stderr)
        return 2

    required_checks = args.required_checks or list(DEFAULT_REQUIRED_CHECKS)
    commands_run: list[dict[str, Any]] = []
    if args.pr is None:
        number, discover_record = discover_pr(args.repo, args.label)
        commands_run.append(discover_record)
        if number is None:
            receipt = write_receipt(
                pr_number=0,
                status="REFUSED",
                reason="no_eligible_target",
                missing=[args.label],
                next_required_action=f"Label one open PR with `{args.label}` after reviewer pass.",
                commands_run=commands_run,
                pr=None,
                gate_summary={"required_label": args.label},
                dry_run=True,
            )
            print(json.dumps({"status": "REFUSED", "reason": "no_eligible_target", "receipt": str(receipt)}, indent=2))
            return 0
    else:
        number = args.pr

    pr, record = load_pr(args.repo, number)
    commands_run.append(record)
    if pr is None:
        receipt = write_receipt(
            pr_number=number,
            status="FAILED",
            reason="github_lookup_failed",
            missing=[],
            next_required_action="Check gh authentication, repository access, and target PR number.",
            commands_run=commands_run,
            pr=None,
            gate_summary={},
            dry_run=True,
        )
        print(json.dumps({"status": "FAILED", "reason": "github_lookup_failed", "receipt": str(receipt)}, indent=2))
        return 1

    status, missing, gate_summary = evaluate_pr(pr, required_checks)
    reason = "dry_run_gates_pass" if status == "WOULD_MERGE" else "merge_gates_not_satisfied"
    next_required_action = (
        "Reviewer should inspect this deployer receipt before any real merge/deploy authority is enabled."
        if status == "WOULD_MERGE"
        else "Coder, reviewer, WebGPT, or human must satisfy the missing gates before release."
    )
    receipt = write_receipt(
        pr_number=number,
        status=status,
        reason=reason,
        missing=missing,
        next_required_action=next_required_action,
        commands_run=commands_run,
        pr=pr,
        gate_summary=gate_summary,
        dry_run=True,
    )
    comment_record = maybe_comment(args.repo, number, args.comment, status, reason, receipt, missing, next_required_action)
    if comment_record:
        commands_run.append(comment_record)
    print(json.dumps({"status": status, "reason": reason, "missing": missing, "receipt": str(receipt)}, indent=2))
    return 0 if status in {"WOULD_MERGE", "REFUSED"} else 1


if __name__ == "__main__":
    sys.exit(main())
