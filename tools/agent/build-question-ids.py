"""Build a slug -> internal questionId map from the batch fetch files.

LeetCode's submit endpoint wants the internal questionId (not the displayed
frontend id), which get_problem returns alongside the statement.
"""
import glob
import json
import os

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')

mapping = {}
for path in sorted(glob.glob(os.path.join(DIR, 'batch*.json'))):
    with open(path, encoding='utf-8') as handle:
        for entry in json.load(handle):
            if entry.get('ok'):
                problem = entry['problem']
                mapping[problem['titleSlug']] = int(problem['questionId'])

with open(os.path.join(DIR, 'question-ids.json'), 'w', encoding='utf-8') as handle:
    json.dump(mapping, handle, ensure_ascii=False, indent=0, sort_keys=True)

print(f'collected {len(mapping)} slug -> questionId entries')
for slug in ('multiply-strings', 'wildcard-matching', 'permutations', 'plus-one'):
    print(f'  {slug}: {mapping.get(slug)}')
