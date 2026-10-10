"""Build the submit queue from QA-passed problems only.

The submitter must never receive a problem that has not been cleared by qa-1
(or repaired and re-marked by qa-2), so the verdict file is the sole source of
truth for what may be submitted.
"""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(DIR, 'queue.json')

with open(os.path.join(DIR, 'qa-verdicts.json'), encoding='utf-8') as handle:
    verdicts = json.load(handle)
with open(os.path.join(DIR, 'accepted.json'), encoding='utf-8') as handle:
    ledger = json.load(handle)
with open(os.path.join(DIR, 'question-ids.json'), encoding='utf-8') as handle:
    question_ids = json.load(handle)

accepted = {s for s, r in ledger.items() if r.get('statusMsg') == 'Accepted'}

files = {}
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    stem = os.path.basename(path)[:-3]
    frontend_id, slug = stem.split('-', 1)
    files[slug] = (int(frontend_id), path)

queue = []
missing_ids = []
for slug, entry in verdicts.items():
    if entry.get('verdict') != 'PASS':
        continue
    if slug in accepted or slug not in files:
        continue
    if slug not in question_ids:
        missing_ids.append(slug)
        continue
    frontend_id, path = files[slug]
    queue.append({
        'frontendId': frontend_id,
        'slug': slug,
        'questionId': question_ids[slug],
        'path': path,
    })

queue.sort(key=lambda item: item['frontendId'])
for item in queue:
    item.pop('frontendId', None)

with open(OUT, 'w', encoding='utf-8') as handle:
    json.dump(queue, handle, ensure_ascii=False, indent=1)

print(f'queue.json written: {len(queue)} problems')
for item in queue:
    print(f"  {item['slug']}  (questionId={item['questionId']})")
if missing_ids:
    print(f'no questionId known for: {sorted(missing_ids)}')
