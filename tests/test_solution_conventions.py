"""Conventions every solution file must satisfy, checked across the whole tree.

LeetCode prepends its own preamble (``class ListNode``, typing names, ...)
before the submitted source, which creates two traps:

  - a ``from __future__ import ...`` statement would no longer be the first
    statement of the file, so the judge rejects it with a SyntaxError;
  - an annotation that names a preamble type must not be evaluated at import
    time, or the file cannot be loaded outside the judge either.

Quoting such annotations (``"ListNode | None"``) satisfies both. This module
turns those rules into a check that scales with the repository.

The entry point is normally ``Solution``, but design problems are judged through
a differently named class: LeetCode instantiates ``MinStack`` for 155 and
``LRUCache`` for 146, and a ``Solution`` there would simply never be called. A
file that is judged that way declares it in the header::

    # Entry point: MinStack

The check then requires that class instead. Declaring the real entry point is
better than adding an unused ``class Solution`` alias, because the alias makes
the file look conventional while hiding which class the judge actually runs.
"""

import re
import unittest

from _loader import SOLUTIONS_DIR, load_solution

FORBIDDEN_SOURCE = 'from __future__ import'
ENTRY_POINT = re.compile(r'^#\s*Entry point:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', re.MULTILINE)
DEFAULT_ENTRY_POINT = 'Solution'


def declared_entry_point(source: str) -> str:
    """The class the judge instantiates, defaulting to ``Solution``."""
    match = ENTRY_POINT.search(source)
    return match.group(1) if match else DEFAULT_ENTRY_POINT


class SolutionConventionTests(unittest.TestCase):
    def test_solutions_directory_is_populated(self):
        self.assertTrue(sorted(SOLUTIONS_DIR.glob('*.py')))

    def test_every_solution_loads_and_defines_its_entry_point(self):
        for path in sorted(SOLUTIONS_DIR.glob('*.py')):
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
                    f'{path.name} does not define its entry point '
                    f'{entry_point!r}',
                )

    def test_entry_point_declarations_name_a_real_class(self):
        """A declaration that does not match anything would silently pass."""
        for path in sorted(SOLUTIONS_DIR.glob('*.py')):
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


if __name__ == '__main__':
    unittest.main()
