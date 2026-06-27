#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p artifacts/watchdog

python3 scripts/phatgpt_watchdog_cycle.py \
  --repo "${PHATGPT_REPO:-grahama1970/chatgpt-lab}" \
  --max-targets 1
