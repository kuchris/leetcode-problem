"""Summarise a submit result file: verdicts, duplicates, and coverage."""
import json
import os
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else r'tools\agent\state\submit-watch-result.json'
with open(path, encoding='utf-8') as handle:
    records = json.load(handle)

print(f'file    : {path}')
print(f'records : {len(records)}')

verdicts = Counter(r.get('statusMsg') or f"phase={r.get('phase')}" for r in records)
print('\nverdicts:')
for verdict, count in verdicts.most_common():
    print(f'  {verdict:<24} {count}')

slugs = [r['slug'] for r in records]
duplicates = {s: c for s, c in Counter(slugs).items() if c > 1}
print(f'\nunique slugs : {len(set(slugs))}')
print(f'duplicates   : {duplicates if duplicates else "none"}')

accepted = [r for r in records if r.get('statusMsg') == 'Accepted']
print(f'\naccepted     : {len(accepted)}')
bad = [r for r in records if r.get('statusMsg') != 'Accepted']
if bad:
    print(f'non-accepted : {len(bad)}')
    for r in bad:
        print(f"  {r['slug']:<40} {r.get('statusMsg')} "
              f"{r.get('totalCorrect')}/{r.get('totalTestcases')} phase={r.get('phase')}")
        for field in ('lastTestcase', 'codeOutput', 'expectedOutput', 'runtimeError'):
            if r.get(field):
                print(f"      {field}: {str(r[field])[:120]}")
