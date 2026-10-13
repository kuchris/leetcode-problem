"""Reserve disjoint solver batches within a frontend-id range.

Locked (paid-only) problems are excluded upstream: backlog.json is built from
the free subset, so a gap in the id sequence here means the problem is either
already solved or paywalled.

Non-Python problems are excluded by default. The pipeline produces and submits
Python only (AGENTS.md: "Use Python 3 unless the user requests another
language"), and LeetCode judges SQL and Shell problems in their own language, so
handing one to a solver would produce a file that cannot be submitted.
categories.json records the classification; it is built by fetching the range and
reading topicTags, because neither the backlog nor codeSnippets carries a
category.

Pass --all to include every category.

Usage: python reserve-range.py <maxFrontendId> <solvers> [batchPerSolver] [--all]
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

args = [a for a in sys.argv[1:] if not a.startswith('--')]
include_all = '--all' in sys.argv

max_id = int(args[0])
solvers = int(args[1]) if len(args) > 1 else 4
per_solver = int(args[2]) if len(args) > 2 else 8

with open(os.path.join(DIR, 'backlog.json'), encoding='utf-8') as handle:
    backlog = json.load(handle)
with open(os.path.join(DIR, 'solved-slugs.json'), encoding='utf-8') as handle:
    solved = set(json.load(handle))

categories = {}
categories_path = os.path.join(DIR, 'categories.json')
if os.path.exists(categories_path):
    with open(categories_path, encoding='utf-8') as handle:
        categories = json.load(handle)

local_slugs = set()
for path in glob.glob(os.path.join(REPO, 'solutions', '*.py')):
    name = os.path.basename(path)
    local_slugs.add(name.split('-', 1)[1][:-3] if '-' in name else name[:-3])

done = solved | local_slugs
in_range = [
    row for row in backlog
    if row['slug'] not in done and row['frontendId'] <= max_id
]
in_range.sort(key=lambda row: row['frontendId'])

skipped = {}
pending = []
for row in in_range:
    category = categories.get(row['slug'], 'unknown')
    if not include_all and category in ('SQL', 'Shell'):
        skipped.setdefault(category, []).append(row)
        continue
    pending.append(row)

print(f'target: frontend ids up to {max_id}')
print(f'free and unsolved in range: {len(in_range)}')
print(f'  assignable (Python)     : {len(pending)}')
for category, rows in sorted(skipped.items()):
    ids = ', '.join(str(r['frontendId']) for r in rows)
    print(f'  skipped {category:<7}          : {len(rows)}  ({ids})')
if not categories:
    print('  NOTE: categories.json absent - nothing was filtered by language')
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
