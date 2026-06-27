#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
queue = json.loads((root / 'queue-state/current.json').read_text())
errors = []
if queue.get('schema') != 'chatgpt_lab.queue_state.v1':
    errors.append('schema')
if not isinstance(queue.get('active_items'), list):
    errors.append('active_items')
if not isinstance(queue.get('stale_or_superseded_items'), list):
    errors.append('stale_or_superseded_items')
print(json.dumps({'schema': 'chatgpt_lab.queue_state_validation.v1', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}, indent=2))
