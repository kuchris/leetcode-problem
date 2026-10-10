"""Print a compact, readable digest of fetched problems."""
import html
import json
import re
import sys

LEVELS = {'Easy': 'Easy', 'Medium': 'Medium', 'Hard': 'Hard'}
BODY_LIMIT = 2200


def text(fragment: str) -> str:
    fragment = re.sub(r'<sup>', '^(', fragment)
    fragment = re.sub(r'</sup>', ')', fragment)
    fragment = re.sub(r'<sub>', '_', fragment)
    fragment = re.sub(r'</sub>', '', fragment)
    fragment = re.sub(r'<li>', '\n  - ', fragment)
    fragment = re.sub(r'</(p|div|li|pre|h\d)>', '\n', fragment)
    fragment = re.sub(r'<br\s*/?>', '\n', fragment)
    fragment = re.sub(r'<[^>]+>', '', fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r'[ \t]+', ' ', fragment)
    fragment = re.sub(r'\n\s*\n\s*\n+', '\n\n', fragment)
    return fragment.strip()


with open(sys.argv[1], encoding='utf-8') as handle:
    results = json.load(handle)

out = open(sys.argv[2], 'w', encoding='utf-8') if len(sys.argv) > 2 else sys.stdout


def emit(*args) -> None:
    out.write(' '.join(str(a) for a in args) + '\n')

for entry in results:
    if not entry['ok']:
        emit(f"### FAILED to fetch {entry['slug']}: {entry['error']}\n")
        continue
    problem = entry['problem']
    emit('=' * 76)
    emit(f"# {problem['titleSlug']}  |  {problem['title']}  |  {LEVELS[problem['difficulty']]}")
    emit('=' * 76)
    body = text(problem['content'])
    if len(body) > BODY_LIMIT:
        body = body[:BODY_LIMIT] + f'\n... [truncated, {len(body)} chars total]'
    emit(body)
    emit('-' * 76)
    emit('exampleTestcases:', problem.get('exampleTestcases'))
    for snippet in problem['codeSnippets']:
        if snippet['langSlug'] == 'python3':
            emit('python3 template:')
            emit(snippet['code'])
    hints = problem.get('hints') or []
    if hints:
        emit(f'hints: {len(hints)} available')
    emit()
