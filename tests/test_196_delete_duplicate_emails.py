"""196. Delete Duplicate Emails -- tests for solutions/196-delete-duplicate-emails.sql.

The statement asks for a DELETE ("you are supposed to write a DELETE statement and
not a SELECT one") and the judge displays the Person table after running it, so
what has to be tested is the state of the table afterwards, not a returned result
set.

Harness note: _sql.py runs SQLite because no PostgreSQL is installed on this
machine, while the judge runs PostgreSQL 16. This statement uses only NOT IN, MIN
and GROUP BY, which behave identically in both, so the local run exercises the
text the judge receives rather than a stand-in.

Oracle: a second DELETE written the opposite way round. Where the solution computes
the survivors with MIN(id) GROUP BY email and excludes everything else, the oracle
deletes a row exactly when an older row with the same email exists. They are
asserted to agree on the same database, and both are checked against a plain
Python expectation that uses no SQL at all.
"""
import json
import unittest
from pathlib import Path

from _sql import build, load_sql, query

SOLUTION = '196-delete-duplicate-emails.sql'
SLUG = 'delete-duplicate-emails'
META_PATH = (
    Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
)

ORACLE_SQL = """
DELETE FROM Person
WHERE EXISTS (
    SELECT 1
    FROM Person older
    WHERE older.email = Person.email AND older.id < Person.id
)
"""

CASES = [
    # The statement's own example.
    [[1, 'john@example.com'], [2, 'bob@example.com'], [3, 'john@example.com']],
    # One row, and every email distinct: nothing to delete.
    [[1, 'a@example.com']],
    [[1, 'a@example.com'], [2, 'b@example.com'], [3, 'c@example.com']],
    # A duplicate whose smallest id comes last in the table.
    [[30, 'dup@example.com'], [20, 'dup@example.com'], [10, 'dup@example.com']],
    # Several emails duplicated to different depths, with non-contiguous ids.
    [
        [5, 'a@example.com'], [9, 'b@example.com'], [12, 'a@example.com'],
        [20, 'c@example.com'], [30, 'b@example.com'], [40, 'a@example.com'],
    ],
    # Every row the same email.
    [[1, 'same@example.com'], [2, 'same@example.com'], [3, 'same@example.com']],
    # No rows at all: the DELETE must not fail.
    [],
]


def problem_meta():
    return json.loads(META_PATH.read_text(encoding='utf-8'))[SLUG]


def example_rows(schema, meta):
    """The example's rows, in schema column order.

    exampleTestcases carries its own column order, so the two are cross-checked
    rather than assumed: a mismatch would insert every row under the wrong column
    and the test would pass while testing nothing.
    """
    payload = json.loads(meta['exampleTestcases'])
    rows = {}
    for table, columns in schema.items():
        declared = [name.lower() for name in payload['headers'][table]]
        expected = [name.lower() for name in columns]
        if declared != expected:
            raise AssertionError(f'{table}: example headers {declared} != schema {expected}')
        rows[table] = payload['rows'][table]
    return rows


def survivors(statement, schema, person_rows):
    """Run ``statement`` against a fresh Person table and read what is left."""
    connection = build(schema, {'Person': person_rows})
    connection.execute(statement)
    connection.commit()
    return query(connection, 'SELECT id, email FROM Person ORDER BY id')


def python_expectation(person_rows):
    """Keep the smallest id per email, computed without SQL."""
    best = {}
    for identifier, email in person_rows:
        if email not in best or identifier < best[email]:
            best[email] = identifier
    return sorted((identifier, email) for email, identifier in best.items())


class DeleteDuplicateEmailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = problem_meta()
        cls.schema = cls.meta['databaseSchema']
        cls.statement = load_sql(SOLUTION)

    def test_solution_is_a_single_delete_statement(self):
        statements = [part for part in self.statement.split(';') if part.strip()]
        self.assertEqual(len(statements), 1, 'the judge runs a single statement')
        self.assertRegex(
            statements[0].strip().lower(), r'^delete\s',
            'the statement must be a DELETE, not a SELECT',
        )

    def test_official_example(self):
        rows = example_rows(self.schema, self.meta)['Person']
        self.assertEqual(rows, [[1, 'john@example.com'], [2, 'bob@example.com'], [3, 'john@example.com']])
        self.assertEqual(
            survivors(self.statement, self.schema, rows),
            [(1, 'john@example.com'), (2, 'bob@example.com')],
        )

    def test_example_keeps_the_row_with_the_smallest_id(self):
        rows = example_rows(self.schema, self.meta)['Person']
        self.assertEqual(survivors(self.statement, self.schema, rows), python_expectation(rows))

    def test_matches_the_independent_delete_oracle(self):
        for rows in CASES:
            with self.subTest(rows=rows):
                self.assertEqual(
                    survivors(self.statement, self.schema, rows),
                    survivors(ORACLE_SQL, self.schema, rows),
                )

    def test_every_email_keeps_its_smallest_id(self):
        for rows in CASES:
            with self.subTest(rows=rows):
                self.assertEqual(
                    survivors(self.statement, self.schema, rows), python_expectation(rows)
                )

    def test_distinct_emails_are_all_kept(self):
        rows = [[7, 'x@example.com'], [8, 'y@example.com'], [9, 'z@example.com']]
        self.assertEqual(survivors(self.statement, self.schema, rows), python_expectation(rows))
        self.assertEqual(len(survivors(self.statement, self.schema, rows)), 3)

    def test_empty_table_stays_empty(self):
        self.assertEqual(survivors(self.statement, self.schema, []), [])

    def test_deleting_twice_changes_nothing_the_second_time(self):
        rows = [[1, 'a@example.com'], [2, 'a@example.com'], [3, 'b@example.com']]
        connection = build(self.schema, {'Person': rows})
        connection.execute(self.statement)
        connection.execute(self.statement)
        connection.commit()
        self.assertEqual(
            query(connection, 'SELECT id, email FROM Person ORDER BY id'),
            python_expectation(rows),
        )


if __name__ == '__main__':
    unittest.main()
