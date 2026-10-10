"""Seed the local AC ledger.

Two sources of "already accepted" feed the ledger so the drainer never
resubmits finished work:

  - the upstream solved list (the problems the account had already done);
  - every submit-batch result file written during this session.

Anything else in solutions/ is genuinely new and will be queued.
"""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
LEDGER = os.path.join(DIR, 'accepted.json')

if os.path.exists(LEDGER):
    with open(LEDGER, encoding='utf-8') as handle:
        ledger = json.load(handle)
else:
    ledger = {}

seeded_upstream = 0
with open(os.path.join(DIR, 'solved-slugs.json'), encoding='utf-8') as handle:
    for slug in json.load(handle):
        if slug not in ledger:
            ledger[slug] = {'statusMsg': 'Accepted', 'source': 'pre-existing'}
            seeded_upstream += 1

seeded_session = 0
for path in sorted(glob.glob(os.path.join(DIR, '*-result.json'))):
    with open(path, encoding='utf-8') as handle:
        for record in json.load(handle):
            slug = record.get('slug')
            if not slug:
                continue
            if record.get('statusMsg') == 'Accepted':
                ledger[slug] = {
                    'statusMsg': 'Accepted',
                    'totalCorrect': record.get('totalCorrect'),
                    'totalTestcases': record.get('totalTestcases'),
                    'submissionId': record.get('submissionId'),
                    'url': record.get('url'),
                    'source': os.path.basename(path),
                }
                seeded_session += 1

with open(LEDGER, 'w', encoding='utf-8') as handle:
    json.dump(ledger, handle, ensure_ascii=False, indent=1)

accepted = sum(1 for v in ledger.values() if v.get('statusMsg') == 'Accepted')
print(f'ledger entries: {len(ledger)}  accepted: {accepted}')
print(f'  seeded from upstream solved list: {seeded_upstream}')
print(f'  refreshed from session results:   {seeded_session}')
