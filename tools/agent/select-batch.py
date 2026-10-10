"""Select the next unsolved problems in strict frontend-id order.

A problem counts as done when either the upstream solved list contains it or a
solution file for it already exists in solutions/ (the local guard keeps a
crash mid-batch from re-queuing work that was already written).
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

count = int(sys.argv[1]) if len(sys.argv) > 1 else 6

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
batch = pending[:count]

with open(os.path.join(DIR, 'slugs.json'), 'w', encoding='utf-8') as handle:
    json.dump([row['slug'] for row in batch], handle, ensure_ascii=False, indent=0)

print(f'pending total: {len(pending)}   batch size: {len(batch)}')
for row in batch:
    print(f"  {row['frontendId']:>4}  {LEVELS[row['level']]:<6} {row['slug']}")
