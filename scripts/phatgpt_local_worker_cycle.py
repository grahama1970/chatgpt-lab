#!/usr/bin/env python3
"""Short-lived PhatGPT-LAB local worker cycle.

The worker is intentionally fail-closed. It inspects one GitHub issue or pull
request, requires a structured phatgpt-task:v1 JSON block, writes a receipt, and
exits. The preferred trigger is OpenCode via GitHub events or `opencode serve`;
this script remains a deterministic fallback and smoke harness.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import re
import shlex
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
ROLE_DONE_LABELS = {
    "coder": "phatgpt-ready-for-review",
    "reviewer": "phatgpt-pass",
    "researcher": "phatgpt-local-agent",
}
ROLE_FAILED_LABELS = {
    "coder": "phatgpt-needs-changes",
    "reviewer": "phatgpt-needs-changes",
    "researcher": "phatgpt-needs-task",
}
LEASE_LABEL = "maintainer-active"


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


def shell_record(command: str, exit_code: int, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    record: dict[str, Any] = {
        "command": command,
        "exit_code": exit_code,
    }
    if stdout.strip():
        record["stdout"] = stdout.strip()
    if stderr.strip():
        record["stderr"] = stderr.strip()
    return record


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
            "number,title,body,labels,headRefName,headRefOid,url,state,isDraft,files",
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


def update_labels(repo: str, kind: str, number: int, *, add: list[str] | None = None, remove: list[str] | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    command_kind = "pr" if kind == "pr" else "issue"
    for label in add or []:
        args = ["gh", command_kind, "edit", str(number), "--repo", repo, "--add-label", label]
        exit_code, _, stderr = run_command(args)
        record = command_record(args, exit_code)
        record["stderr"] = stderr.strip()
        records.append(record)
    for label in remove or []:
        args = ["gh", command_kind, "edit", str(number), "--repo", repo, "--remove-label", label]
        exit_code, _, stderr = run_command(args)
        record = command_record(args, exit_code)
        record["stderr"] = stderr.strip()
        records.append(record)
    return records


def path_allowed(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if path == pattern or fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def changed_files_allowlist(task: dict[str, Any], item: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    files = item.get("files") or []
    paths = [
        file_info["path"]
        for file_info in files
        if isinstance(file_info, dict) and isinstance(file_info.get("path"), str)
    ]
    allowed = [str(pattern) for pattern in task.get("allowed_paths") or []]
    outside = [path for path in paths if not path_allowed(path, allowed)]
    return not outside, paths, outside


def comment_body(*, role: str, target: str, status: str, reason: str | None, receipt_path: Path, commands_run: list[dict[str, Any]], next_required_action: str | None) -> str:
    command_lines = "\n".join(
        f"- `{record.get('command')}` -> `{record.get('exit_code')}`"
        for record in commands_run
        if record.get("command")
    )
    return (
        f"PhatGPT {role} receipt\n\n"
        f"- target: `{target}`\n"
        f"- status: `{status}`\n"
        f"- reason: `{reason or 'n/a'}`\n"
        f"- receipt: `{receipt_path.relative_to(ROOT)}`\n"
        f"- next: `{next_required_action or 'n/a'}`\n\n"
        "Commands:\n"
        f"{command_lines or '- none'}\n"
    )


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
    files_touched: list[str] | None = None,
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
        "files_touched": files_touched or [],
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


def maybe_comment(
    repo: str,
    kind: str,
    number: int,
    receipt_path: Path,
    enabled: bool,
    *,
    role: str,
    status: str,
    reason: str | None,
    commands_run: list[dict[str, Any]],
    next_required_action: str | None,
) -> dict[str, Any] | None:
    if not enabled:
        return None
    body = comment_body(
        role=role,
        target=f"{kind}#{number}",
        status=status,
        reason=reason,
        receipt_path=receipt_path,
        commands_run=commands_run,
        next_required_action=next_required_action,
    )
    args = ["gh", kind, "comment", str(number), "--repo", repo, "--body", body]
    exit_code, _, stderr = run_command(args)
    return {
        "command": " ".join(args),
        "exit_code": exit_code,
        "stderr": stderr.strip(),
    }


def apply_text_patch_payload(payload: dict[str, Any]) -> tuple[int, str, str, list[str]]:
    relative_path = str(payload["path"])
    target = (ROOT / relative_path).resolve()
    if not str(target).startswith(str(ROOT.resolve()) + "/"):
        return 2, "", "path_outside_workspace", []
    if not target.is_file():
        return 2, "", "target_file_missing", []
    text = target.read_text(encoding="utf-8")
    old = payload["exact_old"]
    new = payload["exact_new"]
    expected = payload["expected_replacements"]
    actual = text.count(old)
    if actual != expected:
        return 2, "", f"replacement_count_mismatch expected={expected} actual={actual}", []
    target.write_text(text.replace(old, new, expected), encoding="utf-8")
    return 0, f"patched {relative_path}", "", [relative_path]


def delete_file_payload(payload: dict[str, Any]) -> tuple[int, str, str, list[str]]:
    relative_path = str(payload["path"])
    target = (ROOT / relative_path).resolve()
    if not str(target).startswith(str(ROOT.resolve()) + "/"):
        return 2, "", "path_outside_workspace", []
    if not target.is_file():
        return 2, "", "target_file_missing", []
    target.unlink()
    return 0, f"deleted {relative_path}", "", [relative_path]


def run_validation_commands(task: dict[str, Any], commands_run: list[dict[str, Any]]) -> bool:
    allowed = set(task.get("allowed_commands") or [])
    ok = True
    for command in task.get("validation_commands") or []:
        if command not in allowed and not any(command.startswith(prefix + " ") for prefix in allowed):
            commands_run.append(shell_record(command, 2, stderr="command_not_allowlisted"))
            ok = False
            continue
        result = subprocess.run(shlex.split(command), cwd=ROOT, capture_output=True, text=True, check=False)
        commands_run.append(shell_record(command, result.returncode, result.stdout, result.stderr))
        if result.returncode != 0:
            ok = False
    return ok


def git_has_changes() -> bool:
    result = subprocess.run(["git", "diff", "--quiet"], cwd=ROOT, check=False)
    return result.returncode == 1


def git_worktree_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def execute_coder_task(task: dict[str, Any], item: dict[str, Any], commands_run: list[dict[str, Any]]) -> tuple[str, str | None, list[str], list[str]]:
    task_command = task.get("command", "validate_only")
    if task_command not in {"apply_text_patch", "delete_file"}:
        return "COMPLETED", "task_contract_validated", [], []
    if task.get("mode") != "bounded_execution":
        return "REFUSED", "task_not_implementation_ready", ["bounded_execution mode"], []
    payload_path = str(task.get("payload", {}).get("path") or "")
    if not path_allowed(payload_path, [str(pattern) for pattern in task.get("allowed_paths") or []]):
        return "REFUSED", "path_outside_allowlist", [payload_path], []
    branch = str(task.get("target", {}).get("branch") or item.get("headRefName") or "")
    if not branch:
        return "REFUSED", "target_branch_missing", ["target.branch"], []
    if git_worktree_dirty():
        return "REFUSED", "dirty_worktree", ["clean git worktree"], []

    changed_files: list[str] = []
    fetch_command = ["git", "fetch", "origin", branch]
    exit_code, stdout, stderr = run_command(fetch_command)
    commands_run.append(shell_record(" ".join(fetch_command), exit_code, stdout, stderr))
    if exit_code != 0:
        return "FAILED", "git_branch_checkout_failed", [], changed_files

    switch_command = ["git", "switch", branch]
    exit_code, stdout, stderr = run_command(switch_command)
    commands_run.append(shell_record(" ".join(switch_command), exit_code, stdout, stderr))
    if exit_code != 0:
        track_command = ["git", "switch", "--track", f"origin/{branch}"]
        exit_code, stdout, stderr = run_command(track_command)
        commands_run.append(shell_record(" ".join(track_command), exit_code, stdout, stderr))
        if exit_code != 0:
            return "FAILED", "git_branch_checkout_failed", [], changed_files

    if task_command == "apply_text_patch":
        exit_code, stdout, stderr, touched = apply_text_patch_payload(task["payload"])
        command_label = "apply_text_patch_payload"
    else:
        exit_code, stdout, stderr, touched = delete_file_payload(task["payload"])
        command_label = "delete_file_payload"
    commands_run.append(shell_record(command_label, exit_code, stdout, stderr))
    changed_files.extend(touched)
    if exit_code != 0:
        return "REFUSED", stderr or f"{task_command}_failed", [], changed_files

    validation_ok = run_validation_commands(task, commands_run)
    if not validation_ok:
        return "FAILED", "validation_failed", [], changed_files

    if not git_has_changes():
        return "REFUSED", "no_file_changes_after_patch", [], changed_files

    task_id = str(task["task_id"])
    for command in (
        ["git", "add", *changed_files],
        ["git", "commit", "-m", f"Apply PhatGPT task {task_id}"],
        ["git", "push", "origin", branch],
    ):
        exit_code, stdout, stderr = run_command(list(command))
        commands_run.append(shell_record(" ".join(command), exit_code, stdout, stderr))
        if exit_code != 0:
            return "FAILED", "git_commit_or_push_failed", [], changed_files
    return "COMPLETED", "task_executed_and_pushed", [], changed_files


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
    parser.add_argument("--no-comment", action="store_true")
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
        status = "FAILED"
        reason = "github_lookup_failed"
        next_required_action = "Check gh authentication, repository access, and target number."
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-lookup",
            status=status,
            reason=reason,
            missing=[],
            next_required_action=next_required_action,
            commands_run=commands_run,
            target=None,
        )
        print(json.dumps({"status": "FAILED", "receipt": str(receipt)}, indent=2))
        return 1

    label_names = labels_from(item)
    if args.label not in label_names and not args.allow_unlabeled:
        status = "REFUSED"
        reason = "missing_required_label"
        next_required_action = f"Add label `{args.label}` or rerun with --allow-unlabeled for manual diagnostics."
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-unleased",
            status=status,
            reason=reason,
            missing=[args.label],
            next_required_action=next_required_action,
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment and not args.no_comment, role=args.role, status=status, reason=reason, commands_run=commands_run, next_required_action=next_required_action)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": "missing_required_label", "receipt": str(receipt)}, indent=2))
        return 0

    task, task_error = extract_task(item.get("body") or "")
    if task is None:
        status = "REFUSED"
        reason = task_error or "missing_structured_task_block"
        next_required_action = "WebGPT must update the PR/issue body with a structured phatgpt-task:v1 JSON block."
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=f"{kind}-{number}-missing-task",
            status=status,
            reason=reason,
            missing=expected_missing_for_no_task(),
            next_required_action=next_required_action,
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment and not args.no_comment, role=args.role, status=status, reason=reason, commands_run=commands_run, next_required_action=next_required_action)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": task_error, "receipt": str(receipt)}, indent=2))
        return 0

    validation_errors = validate_task(task)
    if validation_errors:
        status = "REFUSED"
        reason = "task_not_implementation_ready"
        next_required_action = "WebGPT must repair the structured phatgpt-task:v1 block before local execution."
        receipt = write_receipt(
            role=args.role,
            kind=kind,
            number=number,
            task_id=str(task.get("task_id") or f"{kind}-{number}-invalid-task"),
            status=status,
            reason=reason,
            missing=validation_errors,
            next_required_action=next_required_action,
            commands_run=commands_run,
            target=item,
        )
        comment_record = maybe_comment(args.repo, kind, number, receipt, args.comment and not args.no_comment, role=args.role, status=status, reason=reason, commands_run=commands_run, next_required_action=next_required_action)
        if comment_record:
            commands_run.append(comment_record)
        print(json.dumps({"status": "REFUSED", "reason": "task_not_implementation_ready", "receipt": str(receipt)}, indent=2))
        return 0

    if args.role == "coder":
        commands_run.extend(update_labels(args.repo, kind, number, add=[LEASE_LABEL]))
        status, reason, missing, changed_files = execute_coder_task(task, item, commands_run)
        files_touched = changed_files
        done_label = ROLE_DONE_LABELS["coder"] if status == "COMPLETED" else ROLE_FAILED_LABELS["coder"]
        commands_run.extend(update_labels(args.repo, kind, number, add=[done_label], remove=[LEASE_LABEL]))
        next_required_action = (
            "Reviewer event worker should inspect this PR and comment a verdict."
            if status == "COMPLETED"
            else "Coder or WebGPT must repair the task or implementation evidence."
        )
    elif args.role == "reviewer":
        files_allowed, actual_files, outside_files = changed_files_allowlist(task, item)
        commands_run.append(
            shell_record(
                "changed_files_allowlist_check",
                0 if files_allowed else 2,
                stdout=json.dumps(
                    {
                        "actual_files": actual_files,
                        "outside_allowed_paths": outside_files,
                    },
                    sort_keys=True,
                ),
            )
        )
        validation_ok = run_validation_commands(task, commands_run)
        review_ok = validation_ok and files_allowed
        status = "COMPLETED" if review_ok else "FAILED"
        reason = "review_pass" if review_ok else "review_needs_changes"
        missing = []
        if not validation_ok:
            missing.append("validation_commands_pass")
        if not files_allowed:
            missing.append("changed_files_within_allowed_paths")
        files_touched = []
        done_label = ROLE_DONE_LABELS["reviewer"] if review_ok else ROLE_FAILED_LABELS["reviewer"]
        stale_label = ROLE_FAILED_LABELS["reviewer"] if review_ok else ROLE_DONE_LABELS["reviewer"]
        commands_run.extend(update_labels(args.repo, kind, number, add=[done_label], remove=[stale_label]))
        next_required_action = "Merge decision can proceed only after deterministic proof is accepted." if review_ok else "Coder event worker should address reviewer findings."
    else:
        status = "COMPLETED"
        reason = "task_contract_validated"
        missing = []
        files_touched = []
        commands_run.extend(update_labels(args.repo, kind, number, add=[ROLE_DONE_LABELS["researcher"]]))
        next_required_action = "Coder event worker may process this implementation-ready task."

    receipt = write_receipt(
        role=args.role,
        kind=kind,
        number=number,
        task_id=str(task["task_id"]),
        status=status,
        reason=reason,
        missing=missing,
        next_required_action=next_required_action,
        commands_run=commands_run,
        files_touched=files_touched,
        target=item,
    )
    comment_enabled = (args.comment or args.role == "reviewer" or status == "COMPLETED") and not args.no_comment
    comment_record = maybe_comment(args.repo, kind, number, receipt, comment_enabled, role=args.role, status=status, reason=reason, commands_run=commands_run, next_required_action=next_required_action)
    if comment_record:
        commands_run.append(comment_record)
    print(json.dumps({"status": status, "reason": reason, "receipt": str(receipt), "files_touched": files_touched}, indent=2))
    return 0 if status in {"COMPLETED", "REFUSED"} else 1


if __name__ == "__main__":
    sys.exit(main())
