#!/usr/bin/env python3
"""Store compact PhatGPT receipt summaries in memory.

Raw receipts, PR comments, CI runs, screenshots, and deployment proof remain the
canonical evidence. Memory stores only a searchable index pointing back to those
artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("receipt must be a JSON object")
    return value


def summarize(path: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    target = str(receipt.get("target") or "")
    role = str(receipt.get("role") or "")
    status = str(receipt.get("status") or receipt.get("verdict") or "")
    key = "phatgpt_" + "_".join(part for part in [role, target.replace("#", "_"), status.lower()] if part)
    reason = receipt.get("reason")
    receipt_path = str(path.relative_to(ROOT))
    tags = [
        "phatgpt",
        "subagent",
        "chatgpt-lab",
    ]
    if role:
        tags.append(f"role:{role}")
    if status:
        tags.append(f"status:{status.lower()}")
    if target:
        tags.append(target.replace("#", "-"))
    return {
        "_key": key[:254],
        "type": "phatgpt_subagent_receipt_summary",
        "problem": f"Recall the PhatGPT {role or 'subagent'} receipt for {target or 'an unknown target'} in chatgpt-lab.",
        "solution": (
            f"{role or 'subagent'} reported {status or 'UNKNOWN'} for {target or 'unknown target'}"
            f" with reason {reason or 'unspecified'}; canonical proof remains in {receipt_path}."
        ),
        "tags": tags,
        "project": "chatgpt-lab",
        "repository": "grahama1970/chatgpt-lab",
        "role": role,
        "target": target,
        "status": status,
        "reason": reason,
        "receipt_path": receipt_path,
        "head_sha": receipt.get("head_sha"),
        "head_ref": receipt.get("head_ref"),
        "missing": receipt.get("missing") or receipt.get("findings") or [],
        "next_required_action": receipt.get("next_required_action"),
        "source": "phatgpt_memory_sync.py",
    }


def store(document: dict[str, Any], base_url: str, collection: str) -> dict[str, Any]:
    payload = json.dumps({"collection": collection, "documents": [document]}).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/upsert",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--collection", default="subagent_memory")
    parser.add_argument("--base-url", default="http://127.0.0.1:8601")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = (ROOT / args.receipt).resolve()
    try:
        receipt = load_json(path)
        document = summarize(path, receipt)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}, indent=2))
        return 1

    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "document": document}, indent=2, sort_keys=True))
        return 0
    try:
        response = store(document, args.base_url, args.collection)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc), "document": document}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"status": "STORED", "collection": args.collection, "response": response, "document": document}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
