"""One-shot status report for the LeetCode team.

Counts solutions in all three submitted languages, and reads the driver's session
ledger as well as the main one, so a run that has not been merged yet still shows
up rather than looking like pending work.
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

LANGUAGES = {'.py': 'python3', '.sql': 'postgresql', '.sh': 'bash'}


def accepted_slugs():
    """Accepted in either ledger - the driver's own, and the merged main one."""
    found = set()
    for name in ('accepted.json', 'session-accepted.json'):
        path = os.path.join(DIR, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as handle:
            ledger = json.load(handle)
        found |= {s for s, r in ledger.items() if r.get('statusMsg') == 'Accepted'}
    return found


accepted = accepted_slugs()

files = {}
by_language = {}
for extension, lang in LANGUAGES.items():
    for path in glob.glob(os.path.join(REPO, 'solutions', '*' + extension)):
        stem = os.path.basename(path)[: -len(extension)]
        if '-' not in stem:
            continue
        frontend_id, slug = stem.split('-', 1)
        if not frontend_id.isdigit():
            continue
        files[slug] = int(frontend_id)
        by_language[lang] = by_language.get(lang, 0) + 1

outstanding = sorted((i, s) for s, i in files.items() if s not in accepted)

print(f'solution files : {len(files)}')
print('  by language  : ' + ', '.join(
    f'{lang} {count}' for lang, count in sorted(by_language.items())))
print(f'accepted       : {len(accepted)}')
print(f'outstanding    : {len(outstanding)}')
if outstanding:
    print('  ' + ', '.join(str(i) for i, _ in outstanding))

print()
for name in ('submit-a', 'submit-b', 'cdp-full', 'cdp-powx'):
    path = os.path.join(DIR, f'{name}-result.json')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as handle:
        records = json.load(handle)
    print(f'=== {name} ===')
    for record in records:
        phase = record.get('phase', 'done')
        print(f"  {record['slug']:<26} {str(record.get('statusMsg')):<18} "
              f"{record.get('totalCorrect')}/{record.get('totalTestcases')} "
              f"id={record.get('submissionId')} phase={phase}")
