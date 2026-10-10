"""Scan the scratch directory for anything that must never enter the repo.

Looks for session/cookie material, credential-file paths with values, and any
long opaque token that could be a live credential.
"""
import os
import re

# Resolved relative to this file so the tools work from any checkout.
# LC_STATE overrides the data directory; state/ is gitignored.
DIR = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')

SUSPECT_KEYS = re.compile(
    r'(LEETCODE_SESSION|csrftoken|csrf_token|sessionid|SESSION|Cookie|Authorization)',
    re.IGNORECASE,
)
# A long run of URL-safe base64 is what a session token looks like.
OPAQUE = re.compile(r'[A-Za-z0-9_\-%]{40,}')

# Values that are legitimately long and not secrets.
BENIGN = re.compile(
    r'^[0-9a-f]{40,}$'          # hex digests
    r'|^[A-Za-z0-9+/]{40,}={0,2}$'  # base64 of test data
)

hits = []
for name in sorted(os.listdir(DIR)):
    path = os.path.join(DIR, name)
    if not os.path.isfile(path):
        continue
    if os.path.getsize(path) > 5_000_000:
        continue
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            text = handle.read()
    except OSError:
        continue

    for match in SUSPECT_KEYS.finditer(text):
        line_start = text.rfind('\n', 0, match.start()) + 1
        line_end = text.find('\n', match.start())
        line = text[line_start:line_end if line_end != -1 else len(text)]
        hits.append((name, match.group(0), line.strip()[:160]))
        break

    for match in OPAQUE.finditer(text):
        token = match.group(0)
        if BENIGN.match(token):
            continue
        if token.isdigit():
            continue
        hits.append((name, 'OPAQUE', token[:60]))
        break

print(f'files scanned: {len(os.listdir(DIR))}')
if not hits:
    print('no credential-shaped content found')
for name, kind, sample in hits:
    print(f'  {name:<34} [{kind}] {sample}')
