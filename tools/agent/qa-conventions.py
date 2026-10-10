"""Conventions checker for solutions/*.py (read-only).

Checks: title header, problem URL matching the file slug, the judged entry
point, a Time/Space line, builtin generics (no bare typing generics), no
``from __future__ import``, and quoted ListNode/TreeNode annotations.

The entry point is normally ``Solution``, but design problems are judged through
a differently named class (``LRUCache`` for 146, ``MinStack`` for 155). A file
judged that way declares it in its header::

    # Entry point: LRUCache

Mirrors tests/test_solution_conventions.py, which enforces the same rule, so the
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
ENTRY_POINT = re.compile(r'^#\s*Entry point:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', re.MULTILINE)
DEFAULT_ENTRY_POINT = 'Solution'

# Files written before this repository had conventions, in the VS Code LeetCode
# extension's format. AGENTS.md says to preserve existing solutions, so they are
# reported as legacy rather than as failures; the point of the check is to keep
# NEW files conventional.
LEGACY = re.compile(r'^#\s*@lc\s+app=leetcode', re.MULTILINE)


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
    m = re.match(r'^(\d+)-(.+)\.py$', name)
    problems = []
    notes = []
    if not m:
        return name, ['file name is not <frontendId>-<slug>.py'], []
    frontend_id, slug = m.group(1), m.group(2)
    source = open(path, encoding='utf-8').read()
    lines = source.splitlines()

    if not lines or not re.match(rf'^#\s*{int(frontend_id)}\.\s+\S', lines[0]):
        problems.append(f'first line is not a "# <id>. <Title>" header: {lines[0][:60]!r}')
    if f'https://leetcode.com/problems/{slug}/' not in source:
        problems.append(f'missing problem URL for slug {slug}')

    entry_point = declared_entry_point(source)
    if not re.search(rf'^\s*class {re.escape(entry_point)}\b', source, re.M):
        problems.append(f'no `class {entry_point}` (the judged entry point)')
    if ENTRY_POINT.search(source) and entry_point == DEFAULT_ENTRY_POINT:
        notes.append('declares the default entry point; the declaration is only '
                     'needed when it differs')

    has_single = re.search(r'^#.*Time:.*Space:', source, re.M) or re.search(r'^#.*Space:.*Time:', source, re.M)
    has_split = re.search(r'^#\s*Time:', source, re.M) and re.search(r'^#\s*Space:', source, re.M)
    if not (has_single or has_split):
        problems.append('no "# Time: ... Space: ..." complexity line')
    elif has_split and not has_single:
        notes.append('Time: and Space: are on separate comment lines')
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
    files = sorted(glob.glob(os.path.join(SOLUTIONS, pattern + '.py')))
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
