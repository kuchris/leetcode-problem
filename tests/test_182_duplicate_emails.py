"""Tests for 182. Duplicate Emails.

Oracles:
  - ``EXISTS_ORACLE``: keeps an email when some *other* row carries the same
    email, which is a row-pair reading rather than the solution's grouping and
    counting.
  - ``python_oracle``: ``collections.Counter`` over the email column.

The statement's Person.email holds no NULLs, so the oracle's comparison can be a
plain "=". Several NULL emails would additionally be reported as one NULL row by
the solution, because PostgreSQL groups NULL keys together; that is asserted on
the solution alone rather than against the oracle, since "=" cannot express it.
"""

import collections
import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'duplicate-emails'
SOLUTION = load_sql('182-duplicate-emails.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: an email is a duplicate when a different row shares it.
EXISTS_ORACLE = """
SELECT DISTINCT person.email AS "Email"
FROM Person AS person
WHERE EXISTS (
    SELECT 1
    FROM Person AS other
    WHERE other.email = person.email
      AND other.id <> person.id
)
"""

COLUMN = 'Email'


def run(rows, sql):
    connection = build(SCHEMA, rows)
    try:
        return as_multiset(query(connection, sql))
    finally:
        connection.close()


def column_names(rows, sql):
    connection = build(SCHEMA, rows)
    try:
        return [description[0] for description in connection.execute(sql).description]
    finally:
        connection.close()


def python_oracle(persons):
    counts = collections.Counter(row[1] for row in persons)
    return as_multiset([(email,) for email, count in counts.items() if count > 1])


def people(*rows):
    return {'Person': [list(row) for row in rows]}


class DuplicateEmailsTests(unittest.TestCase):
    def agree(self, rows):
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, EXISTS_ORACLE),
                         'solution and EXISTS oracle disagree')
        self.assertEqual(result, python_oracle(rows['Person']),
                         'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        self.assertEqual(self.agree(EXAMPLE), [('a@b.com',)])

    def test_output_column_is_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), [COLUMN])

    def test_three_copies_are_reported_once(self):
        rows = people((1, 'x@y.com'), (2, 'x@y.com'), (3, 'x@y.com'))
        self.assertEqual(self.agree(rows), [('x@y.com',)])

    def test_several_duplicated_emails(self):
        rows = people(
            (1, 'a@b.com'), (2, 'a@b.com'),
            (3, 'c@d.com'), (4, 'c@d.com'), (5, 'c@d.com'),
            (6, 'unique@b.com'),
        )
        self.assertEqual(self.agree(rows), [('a@b.com',), ('c@d.com',)])

    def test_all_distinct(self):
        rows = people((1, 'a@b.com'), (2, 'c@d.com'), (3, 'e@f.com'))
        self.assertEqual(self.agree(rows), [])

    def test_single_row(self):
        self.assertEqual(self.agree(people((1, 'only@b.com'))), [])

    def test_empty_table(self):
        self.assertEqual(self.agree({'Person': []}), [])

    def test_email_comparison_is_case_sensitive(self):
        rows = people((1, 'A@b.com'), (2, 'a@b.com'))
        self.assertEqual(self.agree(rows), [])

    def test_null_emails_group_together(self):
        # PostgreSQL groups NULL keys, so two NULL emails count as a duplicate and
        # the answer carries a single NULL row. The oracle cannot express this
        # with "=", and the statement's data has no NULL emails, so this asserts
        # the solution's behaviour on its own.
        self.assertEqual(run(people((1, None), (2, None)), SOLUTION), [(None,)])

    def test_random_tables(self):
        rng = random.Random(1820)
        for trial in range(400):
            size = rng.randint(0, 15)
            rows = [[index + 1, f'{rng.randint(1, 4)}@x.com'] for index in range(size)]
            with self.subTest(trial=trial, size=size):
                self.agree({'Person': rows})


if __name__ == '__main__':
    unittest.main()
