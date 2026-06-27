#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
queue = json.loads((root / 'queue-state/current.json').read_text())
errors = []
if queue.get('schema') != 'chatgpt_lab.queue_state.v1':
    errors.append('schema')
if queue.get('repository') != 'grahama1970/chatgpt-lab':
    errors.append('repository')
if not isinstance(queue.get('active_items'), list):
    errors.append('active_items')
if not isinstance(queue.get('stale_or_superseded_items'), list):
    errors.append('stale_or_superseded_items')
for section in ['active_items', 'stale_or_superseded_items']:
    for index, item in enumerate(queue.get(section, [])):
        if not isinstance(item, dict):
            errors.append(section + '[' + str(index) + ']')
            continue
        for key in ['kind', 'number', 'url', 'title', 'classification', 'reason', 'recommended_action']:
            if key not in item:
                errors.append(section + '[' + str(index) + '].' + key)
print(json.dumps({'schema': 'chatgpt_lab.queue_state_validation.v1', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}, indent=2))
sys.exit(0 if not errors else 1)
