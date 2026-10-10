"""Reserve disjoint solver batches within a frontend-id range.

Locked (paid-only) problems are excluded upstream: backlog.json is built from
the free subset, so a gap in the id sequence here means the problem is either
already solved or paywalled.

Usage: python reserve-range.py <maxFrontendId> <solvers> [batchPerSolver]
"""
import glob
import json
import os
import sys

DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
LEVELS = {1: 'Easy', 2: 'Medium', 3: 'Hard'}

max_id = int(sys.argv[1])
solvers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
per_solver = int(sys.argv[3]) if len(sys.argv) > 3 else 8

with open(os.path.join(DIR, 'backlog.json'), encoding='utf-8') as handle:
    backlog = json.load(handle)
with open(os.path.join(DIR, 'solved-slugs.json'), encoding='utf-8') as handle:
    solved = set(json.load(handle))

local_slugs = set()
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    name = os.path.basename(path)
    local_slugs.add(name.split('-', 1)[1][:-3] if '-' in name else name[:-3])

done = solved | local_slugs
pending = [
    row for row in backlog
    if row['slug'] not in done and row['frontendId'] <= max_id
]
pending.sort(key=lambda row: row['frontendId'])

print(f'target: frontend ids up to {max_id}')
print(f'free and unsolved in range: {len(pending)}')
print(f'  ' + ', '.join(str(row['frontendId']) for row in pending))
print()

chunks = []
for index in range(solvers):
    chunk = pending[index * per_solver:(index + 1) * per_solver]
    if not chunk:
        continue
    chunks.append(chunk)
    path = os.path.join(DIR, f'slugs-solver{index + 1}.json')
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump([row['slug'] for row in chunk], handle, ensure_ascii=False, indent=0)
    ids = [row['frontendId'] for row in chunk]
    print(f'solver{index + 1}: {len(chunk)} problems (ids {ids[0]}-{ids[-1]})')
    for row in chunk:
        print(f"  {row['frontendId']:>4}  {LEVELS[row['level']]:<6} {row['slug']}")

covered = {row['slug'] for chunk in chunks for row in chunk}
print(f'\ncovered: {len(covered)} of {len(pending)}')
print(f'overlap: {len(covered) - sum(len(c) for c in chunks)} (must be 0)')
