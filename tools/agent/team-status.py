"""One-shot status report for the LeetCode team."""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)
accepted = {s for s, r in ledger.items() if r.get('statusMsg') == 'Accepted'}

files = {}
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    stem = os.path.basename(path)[:-3]
    frontend_id, slug = stem.split('-', 1)
    files[slug] = int(frontend_id)

outstanding = sorted((i, s) for s, i in files.items() if s not in accepted)

print(f'solution files : {len(files)}')
print(f'accepted       : {len(accepted)}')
print(f'outstanding    : {len(outstanding)}')
if outstanding:
    print('  ' + ', '.join(str(i) for i, _ in outstanding))

print()
for name in ('submit-a', 'submit-b', 'cdp-full', 'cdp-powx'):
    path = os.path.join(DIR, f'{name}-result.json')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as handle:
        records = json.load(handle)
    print(f'=== {name} ===')
    for record in records:
        phase = record.get('phase', 'done')
        print(f"  {record['slug']:<26} {str(record.get('statusMsg')):<18} "
              f"{record.get('totalCorrect')}/{record.get('totalTestcases')} "
              f"id={record.get('submissionId')} phase={phase}")
