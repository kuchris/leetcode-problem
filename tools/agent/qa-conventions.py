"""Conventions checker for solutions/* (read-only).

Three languages live in solutions/, chosen by extension:

  .py   Python 3, submitted as python3
  .sql  PostgreSQL, submitted as postgresql
  .sh   Bash, submitted as bash

Common checks: file name is <frontendId>-<slug>.<ext>, the first line is a
"<comment> <id>. <Title>" header, the problem URL matches the slug, and there is
a Time/Space complexity line.

Python-only checks: the judged entry point exists, no `from __future__ import`,
builtin generics (no bare typing generics), and quoted ListNode/TreeNode
annotations.

The entry point is normally `Solution`, but design problems are judged through a
differently named class (LRUCache for 146, MinStack for 155, BSTIterator for 173).
A file judged that way declares it in its header:

    # Entry point: LRUCache

Mirrors tests/test_solution_conventions.py, which enforces the same rules, so the
two checkers cannot drift apart again.
"""
import sys

sys.dont_write_bytecode = True

import ast
import glob
import os
import re

REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SOLUTIONS = os.path.join(REPO, 'solutions')

BARE_GENERIC = re.compile(r'\b(?:List|Dict|Tuple|Set|FrozenSet|Optional|Union|Callable|Iterable|Sequence|Mapping|Deque|DefaultDict)\s*\[')
ENTRY_POINT = re.compile(r'^\s*(?:#|--)\s*Entry point:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', re.MULTILINE)
DEFAULT_ENTRY_POINT = 'Solution'

# How each language writes a comment, for the header and complexity checks.
COMMENT = {'.py': '#', '.sql': '--', '.sh': '#'}

# Files written before this repository had conventions, in the VS Code LeetCode
# extension's format. AGENTS.md says to preserve existing solutions, so they are
# reported as legacy rather than as failures; the point of the check is to keep
# NEW files conventional. tests/test_solution_conventions.py applies the same
# exemption.
LEGACY = re.compile(r'^\s*#\s*@lc\s+app=leetcode', re.MULTILINE)


def declared_entry_point(source):
    """The class the judge instantiates, defaulting to ``Solution``."""
    match = ENTRY_POINT.search(source)
    return match.group(1) if match else DEFAULT_ENTRY_POINT


def annotation_mentions(node):
    """True when an AST annotation node names ListNode/TreeNode."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id in ('ListNode', 'TreeNode'):
            return True
        if isinstance(sub, ast.Attribute) and sub.attr in ('ListNode', 'TreeNode'):
            return True
    return False


def unquoted_annotations(tree, lines):
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            anns = [a.annotation for a in node.args.args + node.args.kwonlyargs + node.args.posonlyargs]
            if node.args.vararg:
                anns.append(node.args.vararg.annotation)
            if node.args.kwarg:
                anns.append(node.args.kwarg.annotation)
            anns.append(node.returns)
            for ann in anns:
                if ann is not None and not isinstance(ann, ast.Constant) and annotation_mentions(ann):
                    bad.append((getattr(ann, 'lineno', node.lineno),
                                lines[getattr(ann, 'lineno', node.lineno) - 1].strip()))
        if isinstance(node, ast.AnnAssign) and not isinstance(node.annotation, ast.Constant) \
                and annotation_mentions(node.annotation):
            bad.append((node.lineno, lines[node.lineno - 1].strip()))
    return bad


def check(path):
    name = os.path.basename(path)
    match = re.match(r'^(\d+)-(.+)\.(py|sql|sh)$', name)
    problems = []
    notes = []
    if not match:
        return name, ['file name is not <frontendId>-<slug>.<py|sql|sh>'], []
    frontend_id, slug, extension = match.group(1), match.group(2), '.' + match.group(3)
    source = open(path, encoding='utf-8').read()
    lines = source.splitlines()
    comment = re.escape(COMMENT[extension])

    if not lines or not re.match(rf'^\s*{comment}\s*{int(frontend_id)}\.\s+\S', lines[0]):
        problems.append(
            f'first line is not a "{COMMENT[extension]} <id>. <Title>" header: '
            f'{lines[0][:60]!r}')
    if f'https://leetcode.com/problems/{slug}/' not in source:
        problems.append(f'missing problem URL for slug {slug}')

    same_line = (
        re.search(rf'^\s*{comment}.*\bTime:.*\bSpace:', source, re.M)
        or re.search(rf'^\s*{comment}.*\bSpace:.*\bTime:', source, re.M)
    )
    split = (
        re.search(rf'^\s*{comment}\s*Time:', source, re.M)
        and re.search(rf'^\s*{comment}\s*Space:', source, re.M)
    )
    if not (same_line or split):
        problems.append('no "Time: ... Space: ..." complexity line')
    elif split and not same_line:
        notes.append('Time: and Space: are on separate comment lines')

    if extension == '.sql':
        body = '\n'.join(
            line for line in lines if not line.strip().startswith('--'))
        statements = [s for s in body.split(';') if s.strip()]
        if len(statements) != 1:
            problems.append(
                f'{len(statements)} statements; the judge runs a single one')
        elif not re.search(r'\b(select|delete|update|insert)\b', statements[0], re.I):
            problems.append('the statement is not a SELECT/DELETE/UPDATE/INSERT')
        return name, problems, notes

    if extension == '.sh':
        body = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        if not body:
            problems.append('the script has no commands, only comments')
        return name, problems, notes

    # Python-only checks from here.
    entry_point = declared_entry_point(source)
    if not re.search(rf'^\s*class {re.escape(entry_point)}\b', source, re.M):
        problems.append(f'no `class {entry_point}` (the judged entry point)')
    if ENTRY_POINT.search(source) and entry_point == DEFAULT_ENTRY_POINT:
        notes.append('declares the default entry point; the declaration is only '
                     'needed when it differs')
    if 'from __future__ import' in source:
        problems.append('from __future__ import present')

    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith('#'):
            continue
        for bare in BARE_GENERIC.finditer(line):
            problems.append(f'line {i}: bare typing generic {bare.group(0)!r}')
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        problems.append(f'SyntaxError: {exc}')
        return name, problems, notes
    for lineno, text in unquoted_annotations(tree, lines):
        problems.append(f'line {lineno}: unquoted ListNode/TreeNode annotation: {text[:80]!r}')
    return name, problems, notes


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else '*'
    files = []
    for extension in COMMENT:
        files.extend(glob.glob(os.path.join(SOLUTIONS, pattern + extension)))
    files = sorted(set(files))

    bad = 0
    legacy = []
    for path in files:
        name, problems, notes = check(path)
        if problems:
            if LEGACY.search(open(path, encoding='utf-8').read()):
                legacy.append(name)
                continue
            bad += 1
            print(f'FAIL {name}')
            for problem in problems:
                print(f'   - {problem}')
        elif notes:
            print(f'ok   {name}  ({"; ".join(notes)})')
        else:
            print(f'ok   {name}')
    for name in legacy:
        print(f'legacy {name}  (pre-existing format, preserved by AGENTS.md)')
    checked = len(files) - len(legacy)
    print(f'\n{checked - bad}/{checked} clean'
          + (f'  ({len(legacy)} legacy file(s) excluded)' if legacy else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
