"""Conventions every solution file must satisfy, checked across the whole tree.

Three languages live in ``solutions/``, chosen by extension:

  ``.py``   Python 3, submitted as ``python3``
  ``.sql``  PostgreSQL, submitted as ``postgresql``
  ``.sh``   Bash, submitted as ``bash``

LeetCode prepends its own preamble to Python submissions, which creates two
traps: a ``from __future__ import`` statement would no longer be first (the judge
rejects it with a SyntaxError), and an annotation naming a preamble type must not
be evaluated at import time. Quoting such annotations satisfies both.

The entry point is normally ``Solution``, but design problems are judged through
a differently named class: ``MinStack`` for 155, ``LRUCache`` for 146,
``BSTIterator`` for 173. A file judged that way declares it in the header::

    # Entry point: MinStack

Declaring the real entry point is better than adding an unused ``class Solution``
alias, because the alias makes the file look conventional while hiding which
class the judge actually runs.
"""

import re
import unittest

from _loader import SOLUTIONS_DIR, load_solution

FORBIDDEN_SOURCE = 'from __future__ import'
ENTRY_POINT = re.compile(
    r'^\s*(?:#|--)\s*Entry point:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', re.MULTILINE)
DEFAULT_ENTRY_POINT = 'Solution'

# How each language writes a comment, for the header and complexity checks.
COMMENT = {'.py': '#', '.sql': '--', '.sh': '#'}

# Files written before this repository had conventions, in the VS Code LeetCode
# extension's format. AGENTS.md says to preserve existing solutions, so they are
# skipped rather than rewritten; the point of the check is to keep NEW files
# conventional. tools/agent/qa-conventions.py applies the same exemption.
LEGACY = re.compile(r'^\s*#\s*@lc\s+app=leetcode', re.MULTILINE)


def declared_entry_point(source: str) -> str:
    """The class the judge instantiates, defaulting to ``Solution``."""
    match = ENTRY_POINT.search(source)
    return match.group(1) if match else DEFAULT_ENTRY_POINT


def header_ok(source: str, path_name: str, comment: str) -> bool:
    """The first non-blank line is ``<comment> <id>. <Title>``.

    A shell script may open with a shebang, which is legitimate and useful, so it
    is skipped before the header is looked for.
    """
    frontend_id = int(path_name.split('-', 1)[0])
    lines = [line for line in source.splitlines() if line.strip()]
    if lines and lines[0].startswith('#!'):
        lines = lines[1:]
    if not lines:
        return False
    return bool(re.match(rf'^\s*{re.escape(comment)}\s*{frontend_id}\.\s+\S', lines[0]))


def sql_statements(source: str):
    """Split a SQL file into statements, ignoring comments and quoted bodies.

    Dollar-quoted blocks (``$$ ... $$``) are how PostgreSQL writes a function
    body, and the body contains semicolons of its own. Counting those as
    statement separators would report a single CREATE FUNCTION as many
    statements, which is why they are masked out first.
    """
    text = '\n'.join(
        line for line in source.splitlines()
        if not line.strip().startswith('--')
    )
    text = re.sub(r'\$\$.*?\$\$', '$$BODY$$', text, flags=re.DOTALL)
    return [statement for statement in text.split(';') if statement.strip()]


class SolutionConventionTests(unittest.TestCase):
    def solutions(self):
        """Every solution file that is subject to these conventions."""
        found = []
        for path in sorted(SOLUTIONS_DIR.glob('*')):
            if path.suffix not in COMMENT or path.name.startswith('_'):
                continue
            if LEGACY.search(path.read_text(encoding='utf-8')):
                continue
            found.append(path)
        return found

    def test_solutions_directory_is_populated(self):
        self.assertTrue(self.solutions())

    def test_every_solution_has_a_header_and_url(self):
        for path in self.solutions():
            with self.subTest(file=path.name):
                source = path.read_text(encoding='utf-8')
                comment = COMMENT[path.suffix]
                self.assertTrue(
                    header_ok(source, path.name, comment),
                    f'{path.name} does not start with "{comment} <id>. <Title>"',
                )
                slug = path.name.split('-', 1)[1][: -len(path.suffix)]
                self.assertIn(
                    f'https://leetcode.com/problems/{slug}/', source,
                    f'{path.name} is missing its problem URL',
                )

    def test_python_solutions_load_and_define_their_entry_point(self):
        for path in self.solutions():
            if path.suffix != '.py':
                continue
            with self.subTest(file=path.name):
                source = path.read_text(encoding='utf-8')
                self.assertNotIn(
                    FORBIDDEN_SOURCE, source,
                    '__future__ imports are not the first statement once the '
                    'judge prepends its preamble',
                )
                entry_point = declared_entry_point(source)
                module = load_solution(path.name)
                self.assertTrue(
                    hasattr(module, entry_point),
                    f'{path.name} does not define its entry point {entry_point!r}',
                )

    def test_entry_point_declarations_name_a_real_class(self):
        """A declaration that does not match anything would silently pass."""
        for path in self.solutions():
            if path.suffix != '.py':
                continue
            source = path.read_text(encoding='utf-8')
            if not ENTRY_POINT.search(source):
                continue
            with self.subTest(file=path.name):
                entry_point = declared_entry_point(source)
                self.assertNotEqual(
                    entry_point, DEFAULT_ENTRY_POINT,
                    f'{path.name} declares the default entry point; the '
                    'declaration is only needed when it differs',
                )
                self.assertIn(
                    f'class {entry_point}', source,
                    f'{path.name} declares {entry_point!r} but never defines it',
                )

    def test_every_solution_states_its_complexity(self):
        for path in self.solutions():
            with self.subTest(file=path.name):
                source = path.read_text(encoding='utf-8')
                comment = re.escape(COMMENT[path.suffix])
                same_line = (
                    re.search(rf'^\s*{comment}.*\bTime:.*\bSpace:', source, re.M)
                    or re.search(rf'^\s*{comment}.*\bSpace:.*\bTime:', source, re.M)
                )
                split = (
                    re.search(rf'^\s*{comment}\s*Time:', source, re.M)
                    and re.search(rf'^\s*{comment}\s*Space:', source, re.M)
                )
                self.assertTrue(
                    same_line or split,
                    f'{path.name} has no "Time: ... Space: ..." complexity line',
                )

    def test_sql_solutions_are_a_single_statement(self):
        """A SQL submission is one statement.

        It is not always a SELECT: 177 requires a function definition, and 196 is
        a DELETE, so the check accepts any single statement that reads or writes.
        """
        for path in self.solutions():
            if path.suffix != '.sql':
                continue
            with self.subTest(file=path.name):
                statements = sql_statements(path.read_text(encoding='utf-8'))
                self.assertEqual(
                    len(statements), 1,
                    f'{path.name} holds {len(statements)} statements; the judge '
                    'runs a single one',
                )
                self.assertRegex(
                    statements[0].lower(),
                    r'\b(select|delete|update|insert|create\s+(or\s+replace\s+)?function)\b',
                    f'{path.name} has no query or function definition',
                )


if __name__ == '__main__':
    unittest.main()
