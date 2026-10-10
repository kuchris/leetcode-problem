"""Check whether a slug is recorded as accepted, and show wave-4 progress."""
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')

with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)

slug = 'merge-two-sorted-lists'
entry = ledger.get(slug)
print(f'ledger entry for {slug}:')
print(json.dumps(entry, ensure_ascii=False, indent=2) if entry else '  ABSENT')

print('\nall submissions recorded for that slug across result files:')
for name in sorted(os.listdir(DIR)):
    if not (name.startswith('submit') and name.endswith('.json')):
        continue
    if 'result' not in name:
        continue
    try:
        with open(os.path.join(DIR, name), encoding='utf-8') as handle:
            records = json.load(handle)
    except Exception:
        continue
    for record in records:
        if record.get('slug') == slug:
            print(f"  {name:<32} {record.get('statusMsg')} "
                  f"{record.get('totalCorrect')}/{record.get('totalTestcases')} "
                  f"id={record.get('submissionId')}")

print('\nwave 4 progress:')
path = os.path.join(DIR, 'submit-wave4-result.json')
if os.path.exists(path):
    with open(path, encoding='utf-8') as handle:
        records = json.load(handle)
    for record in records:
        print(f"  {record['slug']:<34} {record.get('statusMsg')} "
              f"{record.get('totalCorrect')}/{record.get('totalTestcases')}")
else:
    print('  (no file)')
