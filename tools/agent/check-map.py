"""Verify the submit map covers every pending solution before a window starts.

The driver skips any slug it cannot resolve, so a gap here is silent: the watch
window reports "nothing pending" rather than an error. This check turns that
into a loud failure.
"""
import glob
import json
import os
import sys

DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(DIR, 'question-ids.json'), encoding='utf-8') as handle:
    question_ids = json.load(handle)
with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)
accepted = {slug for slug, row in ledger.items() if row.get('statusMsg') == 'Accepted'}

pending = []
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    stem = os.path.basename(path)[:-3]
    if '-' not in stem:
        continue
    frontend_id, slug = stem.split('-', 1)
    if not frontend_id.isdigit() or slug in accepted:
        continue
    pending.append((int(frontend_id), slug))
pending.sort()

unmapped = [slug for _, slug in pending if slug not in question_ids]

print(f'pending solutions : {len(pending)}')
print(f'  ids             : {", ".join(str(i) for i, _ in pending) or "(none)"}')
print(f'mapped            : {len(pending) - len(unmapped)}')
print(f'UNMAPPED          : {len(unmapped)}')
for slug in unmapped:
    print(f'    {slug}')

if unmapped:
    print('\nA window would silently skip the unmapped slugs and look idle.')
    sys.exit(1)
print('\nOK - every pending solution resolves to a questionId')
