#!/usr/bin/env python3
"""Read-only review of a PhatGPT deployer receipt.

This is the final MVP gate: source review is not release approval. A reviewer
must inspect the deployer receipt and comment a verdict before a future
non-dry-run deployer can merge or deploy.
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
REVIEW_SCHEMA = "chatgpt_lab.deployer_review_receipt.v1"
DEFAULT_ACCEPTABLE_MERGE_STATES = {"CLEAN", "HAS_HOOKS", "UNSTABLE"}


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


def load_receipt(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("receipt must be a JSON object")
    return value


def review_receipt(receipt: dict[str, Any]) -> tuple[str, str, list[str]]:
    findings: list[str] = []
    if receipt.get("schema") != "chatgpt_lab.deployer_receipt.v1":
        findings.append("receipt_schema_invalid")
    if receipt.get("role") != "deployer":
        findings.append("receipt_role_not_deployer")
    if receipt.get("dry_run") is not True:
        findings.append("receipt_not_dry_run")
    if receipt.get("status") != "WOULD_MERGE":
        findings.append("deployer_status_not_would_merge")
    if receipt.get("missing"):
        findings.append("deployer_missing_gates_not_empty")
    gate_summary = receipt.get("gate_summary")
    if not isinstance(gate_summary, dict):
        findings.append("gate_summary_missing")
    else:
        if gate_summary.get("reviewer_pass_comment") is not True:
            findings.append("reviewer_pass_comment_not_confirmed")
        required_checks = gate_summary.get("required_checks")
        if not isinstance(required_checks, dict) or not required_checks:
            findings.append("required_checks_missing")
        else:
            failed = sorted(name for name, conclusion in required_checks.items() if conclusion != "SUCCESS")
            if failed:
                findings.append("required_checks_not_success:" + ",".join(failed))
        acceptable_states = gate_summary.get("acceptable_merge_states")
        if isinstance(acceptable_states, list) and acceptable_states:
            allowed_merge_states = {str(state) for state in acceptable_states}
        else:
            allowed_merge_states = DEFAULT_ACCEPTABLE_MERGE_STATES
        if gate_summary.get("merge_state") not in allowed_merge_states:
            findings.append("merge_state_not_acceptable")
    if findings:
        return "NEEDS_CHANGES", "deployer_receipt_rejected", findings
    return "PASS", "deployer_receipt_approved", []


def write_review_receipt(pr_number: int, receipt_path: Path, verdict: str, reason: str, findings: list[str], commands_run: list[dict[str, Any]]) -> Path:
    out_dir = ROOT / "artifacts" / "deployer" / f"pr-{pr_number}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "deployer-review-receipt.json"
    payload = {
        "schema": REVIEW_SCHEMA,
        "role": "reviewer",
        "target": f"pr#{pr_number}",
        "deployer_receipt": str(receipt_path.relative_to(ROOT)),
        "verdict": verdict,
        "reason": reason,
        "findings": findings,
        "commands_run": commands_run,
        "files_touched": [],
        "completed_at": now(),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def comment_body(verdict: str, reason: str, receipt_path: Path, review_path: Path, findings: list[str]) -> str:
    finding_lines = "\n".join(f"- `{finding}`" for finding in findings) or "- none"
    return (
        "PhatGPT reviewer verdict — deployer receipt\n\n"
        f"**Verdict:** `{verdict}`\n\n"
        f"- reason: `{reason}`\n"
        f"- deployer receipt: `{receipt_path.relative_to(ROOT)}`\n"
        f"- review receipt: `{review_path.relative_to(ROOT)}`\n"
        "- mocked: `no`\n"
        "- live: `yes`, GitHub PR state/check evidence read from the deployer receipt\n\n"
        "Findings:\n"
        f"{finding_lines}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="grahama1970/chatgpt-lab")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--comment", action="store_true")
    args = parser.parse_args()

    receipt_path = (ROOT / args.receipt).resolve()
    commands_run: list[dict[str, Any]] = []
    try:
        receipt = load_receipt(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}, indent=2))
        return 1

    verdict, reason, findings = review_receipt(receipt)
    review_path = write_review_receipt(args.pr, receipt_path, verdict, reason, findings, commands_run)
    if args.comment:
        body = comment_body(verdict, reason, receipt_path, review_path, findings)
        comment_args = ["gh", "pr", "comment", str(args.pr), "--repo", args.repo, "--body", body]
        exit_code, stdout, stderr = run_command(comment_args)
        commands_run.append(command_record(comment_args, exit_code, stdout, stderr))
        write_review_receipt(args.pr, receipt_path, verdict, reason, findings, commands_run)
        if exit_code != 0:
            print(json.dumps({"status": "FAILED", "reason": "comment_failed", "receipt": str(review_path)}, indent=2))
            return 1
    print(json.dumps({"verdict": verdict, "reason": reason, "findings": findings, "receipt": str(review_path)}, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
