#!/usr/bin/env python3
"""Generate or check the bounded PhatGPT-LAB controller state.

The controller state is deliberately derived from durable evidence files. It is
not a planner and it does not infer success from prose. Its job is to expose the
next safe WebGPT action after the latest release proof.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "controller-state" / "current.json"
RELEASE_RECEIPT_PATH = ROOT / "iterations" / "2026-06-26-webgpt-mvp-loop-caption-002" / "release-receipt.json"
DEPLOYMENT_PROOF_PATH = ROOT / "delivery-proof" / "monocle-man" / "latest" / "deployment-proof.json"
SCHEMA = "chatgpt_lab.controller_state.v1"
REPOSITORY = "grahama1970/chatgpt-lab"
BRANCH = "main"
ITERATION_ID = "2026-06-26-webgpt-mvp-loop-caption-002"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def gate(name: str, ok: bool, evidence: str, reason: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "evidence": evidence,
    }
    if reason:
        item["reason"] = reason
    return item


def build_state(updated_at: str) -> dict[str, Any]:
    release = load_json(RELEASE_RECEIPT_PATH)
    proof = load_json(DEPLOYMENT_PROOF_PATH)

    release_status = release.get("status")
    proof_status = proof.get("status")
    assertions = proof.get("assertions") if isinstance(proof.get("assertions"), dict) else {}
    blocking_count = assertions.get("blocking_network_errors_count")
    release_commit = (
        release.get("post_merge", {})
        .get("deployment_proof", {})
        .get("commit")
        if isinstance(release.get("post_merge"), dict)
        else None
    )
    proof_commit = proof.get("commit")

    gates = [
        gate(
            "release_receipt_deployed",
            release_status == "DEPLOYED",
            rel(RELEASE_RECEIPT_PATH),
            None if release_status == "DEPLOYED" else f"release status is {release_status!r}",
        ),
        gate(
            "pages_proof_pass",
            proof_status == "PASS",
            rel(DEPLOYMENT_PROOF_PATH),
            None if proof_status == "PASS" else f"proof status is {proof_status!r}",
        ),
        gate(
            "blocking_network_errors_zero",
            blocking_count == 0,
            f"{rel(DEPLOYMENT_PROOF_PATH)}#/assertions/blocking_network_errors_count",
            None if blocking_count == 0 else f"blocking_network_errors_count is {blocking_count!r}",
        ),
        gate(
            "release_commit_matches_proof",
            release_commit == proof_commit,
            f"{rel(RELEASE_RECEIPT_PATH)}#/post_merge/deployment_proof/commit",
            None if release_commit == proof_commit else f"release commit {release_commit!r} != proof commit {proof_commit!r}",
        ),
    ]
    all_pass = all(item["status"] == "PASS" for item in gates)

    return {
        "schema": SCHEMA,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "phase": "awaiting-next-webgpt-task" if all_pass else "release-evidence-repair",
        "state": "READY_FOR_NEXT_TASK" if all_pass else "NEEDS_CHANGES",
        "current_iteration": {
            "iteration_id": ITERATION_ID,
            "release_receipt": rel(RELEASE_RECEIPT_PATH),
            "request": f"iterations/{ITERATION_ID}/request.md",
        },
        "latest_release": {
            "status": release_status,
            "pr": release.get("pr", {}).get("number") if isinstance(release.get("pr"), dict) else None,
            "merge_commit": release.get("pr", {}).get("squash_merge_commit") if isinstance(release.get("pr"), dict) else None,
            "proof_commit": release.get("post_merge", {}).get("proof_commit") if isinstance(release.get("post_merge"), dict) else None,
            "proof_path": rel(DEPLOYMENT_PROOF_PATH),
            "proof_status": proof_status,
            "page_url": proof.get("page_url"),
        },
        "gates": gates,
        "next_action": {
            "owner": "WebGPT",
            "type": "create_bounded_pr_task" if all_pass else "repair_release_evidence",
            "instructions": (
                "Create the next implementation-ready GitHub PR or issue using .github/pull_request_template.md "
                "and a valid phatgpt-task:v1 block. Keep scope to one bounded code, proof, or controller improvement."
                if all_pass
                else "Repair the failing release evidence gate before creating a new implementation task."
            ),
        },
        "required_inputs": [
            "objective",
            "allowed_paths",
            "validation_commands",
            "expected_evidence",
            "stop_condition",
        ],
        "stop_condition": (
            "Next task is not actionable until WebGPT or a human creates a GitHub PR/issue with a valid phatgpt-task:v1 block and explicit proof requirements."
            if all_pass
            else "Controller must not advance until release receipt and Pages proof gates all pass."
        ),
        "updated_at": updated_at,
    }


def compare_without_timestamp(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    expected_copy = dict(expected)
    actual_copy = dict(actual)
    expected_copy.pop("updated_at", None)
    actual_copy.pop("updated_at", None)
    return expected_copy == actual_copy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write controller-state/current.json")
    parser.add_argument("--check", action="store_true", help="fail if controller-state/current.json is stale")
    parser.add_argument("--updated-at", default="2026-06-26T21:30:00Z")
    args = parser.parse_args()

    if args.write and args.check:
        print("--write and --check are mutually exclusive", file=sys.stderr)
        return 2

    try:
        generated = build_state(args.updated_at)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "chatgpt_lab.controller_state_update.v1", "status": "FAIL", "error": str(exc)}, indent=2))
        return 1

    if args.write:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(generated, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        print(json.dumps({"schema": "chatgpt_lab.controller_state_update.v1", "status": "PASS", "path": rel(STATE_PATH)}, indent=2))
        return 0

    if args.check:
        try:
            actual = load_json(STATE_PATH)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"schema": "chatgpt_lab.controller_state_update.v1", "status": "FAIL", "error": str(exc)}, indent=2))
            return 1
        if not compare_without_timestamp(generated, actual):
            print(json.dumps({
                "schema": "chatgpt_lab.controller_state_update.v1",
                "status": "FAIL",
                "error": "controller-state/current.json is stale",
                "expected": generated,
                "actual": actual,
            }, indent=2))
            return 1
        print(json.dumps({"schema": "chatgpt_lab.controller_state_update.v1", "status": "PASS", "path": rel(STATE_PATH)}, indent=2))
        return 0

    print(json.dumps(generated, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
