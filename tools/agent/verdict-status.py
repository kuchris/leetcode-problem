"""Report QA verdicts and the resulting submit-ready queue."""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

verdicts_path = os.path.join(DIR, 'qa-verdicts.json')
if not os.path.exists(verdicts_path):
    print('qa-verdicts.json: not written yet')
    raise SystemExit(0)

with open(verdicts_path, encoding='utf-8') as handle:
    verdicts = json.load(handle)

passed = [k for k, v in verdicts.items() if v.get('verdict') == 'PASS']
failed = [k for k, v in verdicts.items() if v.get('verdict') == 'FAIL']
other = [k for k in verdicts if k not in passed and k not in failed]

print(f'verdict entries : {len(verdicts)}')
print(f'  PASS          : {len(passed)}')
print(f'  FAIL          : {len(failed)}')
if other:
    print(f'  other         : {len(other)} -> {sorted(other)}')

if failed:
    print('\nFAILURES:')
    for slug in sorted(failed):
        entry = verdicts[slug]
        print(f"  {slug}")
        print(f"    reason  : {entry.get('reason', '')[:200]}")
        print(f"    evidence: {str(entry.get('evidence', ''))[:200]}")

# What could be submitted right now: passed AND not already accepted AND has a file.
with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)
accepted = {s for s, r in ledger.items() if r.get('statusMsg') == 'Accepted'}

files = {}
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    stem = os.path.basename(path)[:-3]
    frontend_id, slug = stem.split('-', 1)
    files[slug] = int(frontend_id)

ready = sorted((files[s], s) for s in passed if s in files and s not in accepted)
blocked = sorted((files[s], s) for s in files if s not in accepted and s not in passed)

print(f'\nsubmit-ready (PASS, not yet accepted): {len(ready)}')
for frontend_id, slug in ready:
    print(f'  {frontend_id:>4}  {slug}')
print(f'\nnot yet cleared by QA                : {len(blocked)}')
if blocked:
    print('  ' + ', '.join(str(i) for i, _ in blocked))
