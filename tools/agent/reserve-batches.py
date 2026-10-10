"""Reserve disjoint batches so concurrent solvers cannot pick the same problems.

select-batch.py writes a single slugs.json, so solvers running it at the same
time would fetch identical work. This reserves every half up front instead.
"""
import glob
import json
import os
import sys

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
LEVELS = {1: 'Easy', 2: 'Medium', 3: 'Hard'}

solvers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
batch = int(sys.argv[2]) if len(sys.argv) > 2 else 8

with open(os.path.join(DIR, 'backlog.json'), encoding='utf-8') as handle:
    backlog = json.load(handle)
with open(os.path.join(DIR, 'solved-slugs.json'), encoding='utf-8') as handle:
    solved = set(json.load(handle))

local_slugs = set()
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    name = os.path.basename(path)
    local_slugs.add(name.split('-', 1)[1][:-3] if '-' in name else name[:-3])

done = solved | local_slugs
pending = [row for row in backlog if row['slug'] not in done]

chunks = []
for index in range(solvers):
    chunk = pending[index * batch:(index + 1) * batch]
    chunks.append(chunk)
    path = os.path.join(DIR, f'slugs-solver{index + 1}.json')
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump([row['slug'] for row in chunk], handle, ensure_ascii=False, indent=0)
    print(f'slugs-solver{index + 1}.json: {len(chunk)} problems')
    for row in chunk:
        print(f"  {row['frontendId']:>4}  {LEVELS[row['level']]:<6} {row['slug']}")

seen = set()
overlap = 0
for chunk in chunks:
    for row in chunk:
        if row['slug'] in seen:
            overlap += 1
        seen.add(row['slug'])
print(f'\noverlap across all batches: {overlap} (must be 0)')
print(f'pending remaining after reservation: {len(pending) - len(seen)}')
