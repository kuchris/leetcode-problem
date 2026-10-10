"""Build the browser-submit task list from the local solutions and the ledger.

Output: [{slug, questionId, path}] for every solution whose slug is not yet
Accepted, in frontend-id order.
"""
import glob
import json
import os
import sys

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
SOLUTIONS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'solutions')

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
out_name = sys.argv[2] if len(sys.argv) > 2 else 'tasks.json'

with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)
with open(os.path.join(DIR, 'question-ids.json'), encoding='utf-8') as handle:
    question_ids = json.load(handle)

accepted = {slug for slug, record in ledger.items() if record.get('statusMsg') == 'Accepted'}

entries = []
missing_ids = []
for path in glob.glob(os.path.join(SOLUTIONS, '*.py')):
    stem = os.path.basename(path)[:-3]
    frontend_id, slug = stem.split('-', 1)
    if slug in accepted:
        continue
    if slug not in question_ids:
        missing_ids.append(slug)
        continue
    entries.append({
        'frontendId': int(frontend_id),
        'slug': slug,
        'questionId': question_ids[slug],
        'path': path,
    })

entries.sort(key=lambda entry: entry['frontendId'])
if limit:
    entries = entries[:limit]

for entry in entries:
    entry.pop('frontendId', None)

with open(os.path.join(DIR, out_name), 'w', encoding='utf-8') as handle:
    json.dump(entries, handle, ensure_ascii=False, indent=1)

print(f'tasks written: {len(entries)} -> {out_name}')
for entry in entries:
    print(f"  {entry['slug']}  (questionId={entry['questionId']})")
if missing_ids:
    print(f'no questionId known for: {sorted(missing_ids)}')
