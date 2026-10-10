"""Build the slug -> internal questionId map the submit driver needs.

LeetCode's submit endpoint wants the internal questionId, not the displayed
frontend id, so this map is a hard dependency: scanPending skips any slug it
cannot resolve, which means a stale map makes a watch window look idle instead
of reporting an error.

Two sources, merged:

  - all-problems.json, the full 4073-entry universe. This is the primary source
    because it covers every problem the account can see, so the map cannot go
    stale merely because a solver fetched its batch into a different directory.
  - the batch*.json fetch files, kept as a fallback for anything the universe
    file does not list.

Building from the batch files alone was the original design and it failed: a map
written at 23:08 did not cover problems fetched at 23:37, and re-running the
builder still missed ten problems because two solvers had written their fetch
output outside this directory. The driver's silent skip turned that into a watch
window that would have idled for twelve minutes reporting "nothing pending".
"""
import glob
import json
import os

DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')

mapping = {}
from_universe = 0

universe_path = os.path.join(DIR, 'all-problems.json')
if os.path.exists(universe_path):
    with open(universe_path, encoding='utf-8') as handle:
        for row in json.load(handle):
            slug = row.get('slug')
            question_id = row.get('questionId')
            if slug and question_id is not None:
                mapping[slug] = int(question_id)
                from_universe += 1

before = len(mapping)
for path in sorted(glob.glob(os.path.join(DIR, 'batch*.json'))):
    try:
        with open(path, encoding='utf-8') as handle:
            entries = json.load(handle)
    except (OSError, json.JSONDecodeError):
        continue
    for entry in entries:
        if not entry.get('ok'):
            continue
        problem = entry['problem']
        mapping[problem['titleSlug']] = int(problem['questionId'])
from_batches = len(mapping) - before

with open(os.path.join(DIR, 'question-ids.json'), 'w', encoding='utf-8') as handle:
    json.dump(mapping, handle, ensure_ascii=False, indent=0, sort_keys=True)

print(f'collected {len(mapping)} slug -> questionId entries')
print(f'  from all-problems.json : {from_universe}')
print(f'  added from batch files : {from_batches}')

# A range probe, because the failure this replaces was silent rather than loud.
by_id = {value: key for key, value in mapping.items()}
for frontend_id in (133, 146, 152, 155):
    print(f'  sanity: id {frontend_id} -> {by_id.get(frontend_id, "MISSING")}')
