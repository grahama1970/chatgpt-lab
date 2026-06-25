#!/usr/bin/env python3
"""Validate a Slice 001 benchmark evidence directory.

The validator checks the artifact layout produced by
`monocle-man-site/scripts/collect-evidence.mjs`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_FILES = [
    "run-metadata.json",
    "source-metadata.json",
    "test-results.json",
    "console-errors.json",
    "network-errors.json",
    "accessibility.json",
    "interactions.json",
    "deployment-metadata.json",
    "artifact-manifest.json",
    "verdict.json",
]
REQUIRED_SCREENSHOTS = [
    "screenshots/desktop.png",
    "screenshots/mobile.png",
]
VERDICTS = {"PASS", "NEEDS_CHANGES", "BLOCKED", "INSUFFICIENT_EVIDENCE"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path.name}: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir", type=Path)
    args = parser.parse_args()

    evidence_dir = args.evidence_dir
    errors: list[str] = []
    warnings: list[str] = []

    if not evidence_dir.is_dir():
        errors.append(f"evidence_dir is not a directory: {evidence_dir}")
    else:
        for relative in REQUIRED_FILES + REQUIRED_SCREENSHOTS:
            path = evidence_dir / relative
            if not path.is_file():
                errors.append(f"missing required artifact: {relative}")
            elif path.stat().st_size <= 0:
                errors.append(f"empty required artifact: {relative}")

    run_metadata = load_json(evidence_dir / "run-metadata.json", errors) if (evidence_dir / "run-metadata.json").is_file() else {}
    source_metadata = load_json(evidence_dir / "source-metadata.json", errors) if (evidence_dir / "source-metadata.json").is_file() else {}
    deployment = load_json(evidence_dir / "deployment-metadata.json", errors) if (evidence_dir / "deployment-metadata.json").is_file() else {}
    manifest = load_json(evidence_dir / "artifact-manifest.json", errors) if (evidence_dir / "artifact-manifest.json").is_file() else {}
    verdict = load_json(evidence_dir / "verdict.json", errors) if (evidence_dir / "verdict.json").is_file() else {}

    if isinstance(run_metadata, dict):
        if run_metadata.get("schema") != "chatgpt_lab.github_actions_run.v1":
            errors.append("run-metadata.json has unexpected schema")
        if run_metadata.get("repository") != "grahama1970/snippets":
            errors.append("run-metadata.repository must be grahama1970/snippets")
        if run_metadata.get("artifact_name") != "monocle-man-benchmark-evidence":
            errors.append("run-metadata.artifact_name must be monocle-man-benchmark-evidence")

    if isinstance(source_metadata, dict):
        if source_metadata.get("schema") != "chatgpt_lab.benchmark_source.v1":
            errors.append("source-metadata.json has unexpected schema")
        if source_metadata.get("path") != "monocle-man-site/":
            errors.append("source-metadata.path must be monocle-man-site/")

    head_sha = run_metadata.get("head_sha") if isinstance(run_metadata, dict) else None
    source_commit = source_metadata.get("commit") if isinstance(source_metadata, dict) else None
    if head_sha and source_commit and head_sha != source_commit:
        errors.append("run-metadata.head_sha must equal source-metadata.commit")

    if isinstance(deployment, dict):
        if deployment.get("schema") != "chatgpt_lab.deployment_proof.v1":
            errors.append("deployment-metadata.json has unexpected schema")
        if deployment.get("status") == "PROVEN":
            if not deployment.get("url"):
                errors.append("PROVEN deployment requires url")
            if not deployment.get("commit"):
                errors.append("PROVEN deployment requires commit")
            if source_commit and deployment.get("commit") != source_commit:
                errors.append("deployment commit must equal source-metadata.commit when status is PROVEN")
        else:
            warnings.append("deployment proof is not established; no live-site claim is supported")

    if isinstance(verdict, dict):
        value = verdict.get("verdict")
        if value not in VERDICTS:
            errors.append(f"verdict.json verdict must be one of {sorted(VERDICTS)}")
        if value == "PASS" and verdict.get("live_site_claim") is True:
            if not isinstance(deployment, dict) or deployment.get("status") != "PROVEN":
                errors.append("live_site_claim=true requires PROVEN deployment metadata")
    else:
        errors.append("verdict.json must contain an object")

    manifest_paths = set()
    if isinstance(manifest, dict):
        entries = manifest.get("files")
        if not isinstance(entries, list):
            errors.append("artifact-manifest.files must be an array")
        else:
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                    manifest_paths.add(entry["path"])
            for relative in REQUIRED_FILES + REQUIRED_SCREENSHOTS:
                if relative not in manifest_paths and relative != "artifact-manifest.json":
                    errors.append(f"artifact manifest does not list {relative}")
    else:
        errors.append("artifact-manifest.json must contain an object")

    files = []
    if evidence_dir.is_dir():
        for path in sorted(p for p in evidence_dir.rglob("*") if p.is_file()):
            files.append({
                "path": str(path.relative_to(evidence_dir)).replace("\\", "/"),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            })

    receipt = {
        "schema": "chatgpt_lab.benchmark_evidence_validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "evidence_dir": str(evidence_dir),
        "files": files,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
