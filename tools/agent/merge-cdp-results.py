"""Fold browser-submit results into the local AC ledger.

Two sources feed the ledger:

  - session-accepted.json, written by the driver itself the moment a submission
    is Accepted. It is the driver's private file, so folding it in cannot race
    with the driver's own writes.
  - the submit-*.json result files, which carry the full per-problem record
    including any judge diagnostics.

Both are idempotent: merging twice produces the same ledger.
"""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
LEDGER = os.path.join(DIR, 'accepted.json')

with open(LEDGER, encoding='utf-8') as handle:
    ledger = json.load(handle)

updated = 0

# 1. The driver's own ledger, keyed by slug already.
session_path = os.path.join(DIR, 'session-accepted.json')
if os.path.exists(session_path):
    with open(session_path, encoding='utf-8') as handle:
        session = json.load(handle)
    for slug, record in session.items():
        if record.get('statusMsg') != 'Accepted':
            continue
        ledger[slug] = {
            'statusMsg': 'Accepted',
            'totalCorrect': record.get('totalCorrect'),
            'totalTestcases': record.get('totalTestcases'),
            'submissionId': record.get('submissionId'),
            'url': record.get('url'),
            'source': 'session-accepted.json',
        }
        updated += 1

# 2. The result files. The patterns cover every shape a run has produced, so a
#    new mode's output is picked up by the merge rather than needing a one-off
#    script - which is how two verified acceptances were once left unrecorded,
#    leaving them pending for the next window to submit again as duplicates.
patterns = (
    'cdp*result*.json',
    'parallel-*-result.json',
    'submit-*-result.json',
    'verify-*-result.json',
)
seen = set()
for pattern in patterns:
    for path in sorted(glob.glob(os.path.join(DIR, pattern))):
        if path in seen:
            continue
        seen.add(path)
        with open(path, encoding='utf-8') as handle:
            records = json.load(handle)
        for record in records:
            if record.get('statusMsg') != 'Accepted':
                continue
            slug = record['slug']
            ledger[slug] = {
                'statusMsg': 'Accepted',
                'totalCorrect': record.get('totalCorrect'),
                'totalTestcases': record.get('totalTestcases'),
                'submissionId': record.get('submissionId'),
                'url': record.get('url'),
                'source': os.path.basename(path),
            }
            updated += 1

with open(LEDGER, 'w', encoding='utf-8') as handle:
    json.dump(ledger, handle, ensure_ascii=False, indent=1)

accepted = [slug for slug, record in ledger.items() if record.get('statusMsg') == 'Accepted']
print(f'ledger updated from browser results: {updated} entries')
print(f'accepted total: {len(accepted)}')
