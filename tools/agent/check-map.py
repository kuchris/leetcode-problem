"""Verify the submit map covers every pending solution before a window starts.

The driver skips any slug it cannot resolve, so a gap here is silent: the watch
window reports "nothing pending" rather than an error. This check turns that into
a loud failure.

Two things it must get right, both learned the hard way:

  - every submitted language, not just Python. It originally globbed
    ``solutions/*.py`` only, so its "UNMAPPED 0 / OK" said nothing at all about
    SQL and Shell files - which were exactly the ones at risk. Had every one of
    those slugs been missing from the map, it would still have printed OK.
  - both ledgers. The driver writes session-accepted.json and the Lead writes
    accepted.json, so reading only the latter over-reports pending whenever the
    session ledger is ahead of the merge.
"""
import glob
import json
import os
import sys

DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# The same map the submit driver uses, so the two cannot disagree about which
# extensions are submission candidates.
LANG_BY_EXT = {'.py': 'python3', '.sql': 'postgresql', '.sh': 'bash'}

with open(os.path.join(DIR, 'question-ids.json'), encoding='utf-8') as handle:
    question_ids = json.load(handle)

accepted = set()
for name in ('accepted.json', 'session-accepted.json'):
    path = os.path.join(DIR, name)
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as handle:
        ledger = json.load(handle)
    accepted |= {slug for slug, row in ledger.items()
                 if row.get('statusMsg') == 'Accepted'}

pending = []
by_language = {}
for extension, lang in LANG_BY_EXT.items():
    for path in glob.glob(os.path.join(REPO, 'solutions', '*' + extension)):
        stem = os.path.basename(path)[: -len(extension)]
        if '-' not in stem:
            continue
        frontend_id, slug = stem.split('-', 1)
        if not frontend_id.isdigit() or slug in accepted:
            continue
        pending.append((int(frontend_id), slug))
        by_language[lang] = by_language.get(lang, 0) + 1
pending.sort()

unmapped = [slug for _, slug in pending if slug not in question_ids]

print(f'pending solutions : {len(pending)}')
print('  by language     : ' + (', '.join(
    f'{lang} {count}' for lang, count in sorted(by_language.items())) or '(none)'))
print(f'  ids             : {", ".join(str(i) for i, _ in pending) or "(none)"}')
print(f'mapped            : {len(pending) - len(unmapped)}')
print(f'UNMAPPED          : {len(unmapped)}')
for slug in unmapped:
    print(f'    {slug}')

if unmapped:
    print('\nA window would silently skip the unmapped slugs and look idle.')
    sys.exit(1)
print('\nOK - every pending solution resolves to a questionId')
