"""Fold browser-submit results into the local AC ledger."""
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
patterns = ('cdp*result*.json', 'parallel-*-result.json', 'submit-*-result.json')
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
