#!/usr/bin/env python3
"""Apply a single exact text replacement from agent-state/next-command.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_agent_state import NEXT_COMMAND_PATH, validate_next_command

ROOT = Path(__file__).resolve().parents[1]
TOUCHED_FILES_PATH = ".agent-dispatch-touched-files.txt"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--state-path", default=NEXT_COMMAND_PATH)
    args = parser.parse_args()

    root = args.root.resolve()
    state_path = root / args.state_path
    touched_path = root / TOUCHED_FILES_PATH
    if touched_path.exists():
        touched_path.unlink()

    try:
        command = load_json(state_path)
    except (OSError, json.JSONDecodeError) as exc:
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "invalid_next_command_json",
            "error": str(exc),
        })
        return 2

    errors = validate_next_command(command)
    if errors:
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "next_command_validation_failed",
            "errors": errors,
        })
        return 2

    if command.get("command") != "apply_text_patch":
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "wrong_command",
            "command": command.get("command"),
        })
        return 2

    payload = command["payload"]
    relative_path = payload["path"]
    target = (root / relative_path).resolve()
    if not target.is_file():
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "target_file_missing",
            "path": relative_path,
        })
        return 2

    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "target_file_not_utf8",
            "path": relative_path,
            "error": str(exc),
        })
        return 2

    old = payload["exact_old"]
    new = payload["exact_new"]
    expected = payload["expected_replacements"]
    actual = text.count(old)
    if actual != expected:
        emit({
            "schema": "chatgpt_lab.apply_text_patch_result.v1",
            "status": "REFUSED",
            "reason": "replacement_count_mismatch",
            "path": relative_path,
            "expected_replacements": expected,
            "actual_replacements": actual,
        })
        return 2

    target.write_text(text.replace(old, new, expected), encoding="utf-8")
    touched_path.write_text(f"{relative_path}\n", encoding="utf-8")
    emit({
        "schema": "chatgpt_lab.apply_text_patch_result.v1",
        "status": "PASS",
        "path": relative_path,
        "replacements": expected,
        "touched_files_manifest": TOUCHED_FILES_PATH,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
