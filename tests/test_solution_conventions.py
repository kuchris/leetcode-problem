"""Conventions every solution file must satisfy, checked across the whole tree.

LeetCode prepends its own preamble (``class ListNode``, typing names, ...)
before the submitted source, which creates two traps:

  - a ``from __future__ import ...`` statement would no longer be the first
    statement of the file, so the judge rejects it with a SyntaxError;
  - an annotation that names a preamble type must not be evaluated at import
    time, or the file cannot be loaded outside the judge either.

Quoting such annotations (``"ListNode | None"``) satisfies both. This module
turns those rules into a check that scales with the repository.
"""

import unittest

from _loader import SOLUTIONS_DIR, load_solution

FORBIDDEN_SOURCE = 'from __future__ import'


class SolutionConventionTests(unittest.TestCase):
    def test_solutions_directory_is_populated(self):
        self.assertTrue(sorted(SOLUTIONS_DIR.glob('*.py')))

    def test_every_solution_loads_and_defines_solution(self):
        for path in sorted(SOLUTIONS_DIR.glob('*.py')):
            with self.subTest(file=path.name):
                source = path.read_text(encoding='utf-8')
                self.assertNotIn(
                    FORBIDDEN_SOURCE, source,
                    '__future__ imports are not the first statement once the '
                    'judge prepends its preamble',
                )
                module = load_solution(path.name)
                self.assertTrue(
                    hasattr(module, 'Solution'),
                    f'{path.name} does not define a Solution class',
                )


if __name__ == '__main__':
    unittest.main()
