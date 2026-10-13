"""Tests for 176. Second Highest Salary.

The two oracles are deliberately different mechanisms:

  - `oracle_window` ranks the distinct salaries with DENSE_RANK and takes rank 2;
  - `oracle_aggregate` is a pure aggregate: MAX(salary) below the top salary, with
    no ordering, no OFFSET and no window function at all.

Both are single-row queries, like the solution, so the trap this problem is built
around is checked by every assertion: when there is no second highest salary the
answer must be one row holding NULL, never an empty result.

The official examples are hand-transcribed from the statement:

    Employee [100, 200, 300]  ->  200
    Employee [100]            ->  null

NULL-salary rows are tested on purpose. They are not part of the judge's data,
but PostgreSQL sorts NULLs first under `ORDER BY ... DESC` while SQLite sorts them
last, so the solution carries an explicit `salary IS NOT NULL` guard; without it
the two engines would disagree on such rows and this test would fail.
"""

import contextlib
import json
import pathlib
import random
import unittest

from _sql import build, load_sql, query

META = json.loads(
    (pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json')
    .read_text(encoding='utf-8')
)
SOLUTIONS = pathlib.Path(__file__).resolve().parents[1] / 'solutions'
SLUG = 'second-highest-salary'
SCHEMA = META[SLUG]['databaseSchema']
QUERY = load_sql('176-second-highest-salary.sql')

ROW_ORDER = {'Employee': ['id', 'salary']}
COLUMN = 'SecondHighestSalary'


def example_cases():
    raw = META[SLUG]['exampleTestcases'] or ''
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def rows_in_schema_order(table, row_order, table_rows):
    schema_columns = list(SCHEMA[table])
    indexes = [schema_columns.index(column) for column in row_order]
    return [[row[index] for index in indexes] for row in table_rows]


@contextlib.contextmanager
def connection_for(rows):
    connection = build(SCHEMA, {
        table: rows_in_schema_order(table, ROW_ORDER[table], table_rows)
        for table, table_rows in rows.items()
    })
    try:
        yield connection
    finally:
        connection.close()


@contextlib.contextmanager
def connection_for_case(case):
    connection = build(SCHEMA, {
        table: rows_in_schema_order(table, case['headers'][table], table_rows)
        for table, table_rows in (case.get('rows') or {}).items()
    })
    try:
        yield connection
    finally:
        connection.close()


def oracle_window(connection):
    """DENSE_RANK over the distinct salaries, keeping rank 2."""
    return query(connection, f'''
        SELECT (
            SELECT salary
            FROM (
                SELECT DISTINCT salary,
                       DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
                FROM Employee
                WHERE salary IS NOT NULL
            ) AS ranked
            WHERE rnk = 2
        ) AS "{COLUMN}"
    ''')


def oracle_aggregate(connection):
    """MAX below the top salary: one aggregate, no ordering and no offset."""
    return query(connection, f'''
        SELECT MAX(salary) AS "{COLUMN}"
        FROM Employee
        WHERE salary IS NOT NULL
          AND salary < (SELECT MAX(salary) FROM Employee WHERE salary IS NOT NULL)
    ''')


class SecondHighestSalaryTests(unittest.TestCase):
    def assert_matches_oracles(self, rows):
        with connection_for(rows) as connection:
            result = query(connection, QUERY)
            self.assertEqual(result, oracle_window(connection), f'rows={rows}')
            self.assertEqual(result, oracle_aggregate(connection), f'rows={rows}')
        self.assertEqual(len(result), 1, 'the answer is always exactly one row')
        return result[0][0]

    def employees(self, salaries):
        return {'Employee': [(index + 1, salary) for index, salary in enumerate(salaries)]}

    def test_official_example_one(self):
        with connection_for_case(example_cases()[0]) as connection:
            self.assertEqual(query(connection, QUERY), [(200,)])

    def test_official_example_two(self):
        with connection_for_case(example_cases()[1]) as connection:
            self.assertEqual(query(connection, QUERY), [(None,)])

    def test_official_example_headers(self):
        with connection_for_case(example_cases()[0]) as connection:
            cursor = connection.execute(QUERY)
            try:
                self.assertEqual([description[0] for description in cursor.description], [COLUMN])
            finally:
                cursor.close()

    def test_no_second_highest_returns_null_not_empty(self):
        for salaries in ([100], [], [100, 100, 100], [7, 7]):
            with self.subTest(salaries=salaries):
                with connection_for(self.employees(salaries)) as connection:
                    result = query(connection, QUERY)
                self.assertEqual(len(result), 1)
                self.assertIsNone(result[0][0])

    def test_duplicate_top_salary_is_not_the_second_highest(self):
        # Without DISTINCT this would answer 300.
        self.assertEqual(self.assert_matches_oracles(self.employees([300, 300, 200])), 200)
        self.assertEqual(self.assert_matches_oracles(self.employees([300, 300, 300, 200, 200])), 200)

    def test_two_rows(self):
        self.assertEqual(self.assert_matches_oracles(self.employees([100, 200])), 100)
        self.assertEqual(self.assert_matches_oracles(self.employees([200, 100])), 100)

    def test_descending_and_ascending_input(self):
        self.assertEqual(self.assert_matches_oracles(self.employees([300, 200, 100])), 200)
        self.assertEqual(self.assert_matches_oracles(self.employees([100, 200, 300])), 200)

    def test_negative_salaries(self):
        self.assertEqual(self.assert_matches_oracles(self.employees([-100, -200, -300])), -200)
        self.assertEqual(self.assert_matches_oracles(self.employees([-100, 0, 100])), 0)
        self.assertEqual(self.assert_matches_oracles(self.employees([-100, -100])), None)

    def test_integer_extremes(self):
        self.assertEqual(self.assert_matches_oracles(self.employees([2 ** 31 - 1, 0, -(2 ** 31)])), 0)
        self.assertEqual(self.assert_matches_oracles(self.employees([2 ** 31 - 1, 2 ** 31 - 1])), None)

    def test_null_salaries_are_ignored(self):
        # Postgres would rank a NULL first under DESC; the guard keeps the engines
        # and the two oracles in agreement. With NULLs ignored there is only one
        # distinct salary here, so the answer is still the single NULL row.
        self.assertEqual(self.assert_matches_oracles(self.employees([None, 300])), None)
        self.assertEqual(self.assert_matches_oracles(self.employees([300, None, 200])), 200)
        self.assertEqual(self.assert_matches_oracles(self.employees([None, None])), None)

    def test_randomised_databases(self):
        rng = random.Random(1760)
        for case in range(300):
            size = rng.randint(0, 12)
            salaries = [rng.randint(-5, 5) for _ in range(size)]
            with self.subTest(case=case, salaries=salaries):
                expected = sorted({salary for salary in salaries}, reverse=True)
                self.assertEqual(
                    self.assert_matches_oracles(self.employees(salaries)),
                    expected[1] if len(expected) > 1 else None,
                )

    def test_randomised_wide_values(self):
        rng = random.Random(1761)
        for case in range(100):
            salaries = [rng.randint(-(2 ** 31), 2 ** 31 - 1) for _ in range(rng.randint(0, 20))]
            with self.subTest(case=case):
                expected = sorted(set(salaries), reverse=True)
                self.assertEqual(
                    self.assert_matches_oracles(self.employees(salaries)),
                    expected[1] if len(expected) > 1 else None,
                )

    def test_constraint_sized(self):
        # The statement sets no row bound; 5000 employees is a deliberately large
        # case, checked against both oracles and against the closed form.
        rng = random.Random(1762)
        salaries = [rng.randint(0, 500) for _ in range(5000)]
        distinct = sorted(set(salaries), reverse=True)
        self.assertEqual(self.assert_matches_oracles(self.employees(salaries)), distinct[1])

        all_equal = [7] * 5000
        self.assertEqual(self.assert_matches_oracles(self.employees(all_equal)), None)

        spread = list(range(5000))
        self.assertEqual(self.assert_matches_oracles(self.employees(spread)), 4998)

    def test_file_contains_one_statement(self):
        source = (SOLUTIONS / '176-second-highest-salary.sql').read_text(encoding='utf-8')
        body = '\n'.join(
            line for line in source.splitlines() if not line.strip().startswith('--')
        ).strip()
        self.assertTrue(body.upper().startswith('SELECT'))
        self.assertTrue(body.endswith(';'))
        self.assertEqual(body.count(';'), 1)


if __name__ == '__main__':
    unittest.main()
