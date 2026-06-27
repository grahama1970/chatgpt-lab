#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/artifacts/watchdog/cron.log"
MARKER="# phatgpt-lab-watchdog"
ENTRY="*/5 * * * * cd $ROOT && $ROOT/scripts/run_phatgpt_watchdog.sh >> $LOG 2>&1 $MARKER"

mkdir -p "$ROOT/artifacts/watchdog"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

crontab -l 2>/dev/null | grep -vF "$MARKER" > "$tmp" || true
printf '%s\n' "$ENTRY" >> "$tmp"
crontab "$tmp"

echo "$ENTRY"
