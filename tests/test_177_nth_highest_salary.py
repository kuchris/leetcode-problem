"""Tests for 177. Nth Highest Salary.

WHAT THIS FILE VERIFIES, AND WHAT IT CANNOT
LeetCode judges problem 177 as a *stored function*: the test data carries an
`argument` (n) and the judge calls `SELECT NthHighestSalary(n)`, so the submission
must define that function -- a bare SELECT cannot receive n. The solution file is
therefore one statement:

    CREATE OR REPLACE FUNCTION NthHighestSalary(N INT) RETURNS INT AS $$
        SELECT ...
    $$ LANGUAGE sql;

The name is NthHighestSalary, not getNthHighestSalary. The expected output labels
its column "getNthHighestSalary(2)", which is a column label rather than the
identifier the harness invokes; naming the function after the label made the judge
report "function nthhighestsalary(integer) does not exist". The signature below is
asserted so that a rename cannot silently reintroduce that failure.

SQLite has no `CREATE FUNCTION` and no `$$`-quoted bodies, so this test does NOT
execute the wrapper. It executes the *body* with `N` substituted by the argument,
which is exactly the value the function returns, and it checks the wrapper's shape
textually. Whether PostgreSQL accepts the wrapper itself can only be confirmed by
submission -- that part is NOT covered here, and is reported to the lead as such.

The oracles are two differently-written queries for the same value:

  - `oracle_limit_offset`: DISTINCT + ORDER BY + LIMIT 1 OFFSET n-1;
  - `oracle_correlated_count`: a correlated COUNT(DISTINCT ...) that needs no
    ordering and no offset, i.e. the "one more than the number of distinct higher
    salaries" definition of the rank.

The official examples are hand-transcribed from the statement:

    Employee [100, 200, 300], n = 2  ->  200
    Employee [100],           n = 2  ->  null
"""

import contextlib
import json
import pathlib
import random
import re
import unittest

from _sql import build, load_sql, query

META = json.loads(
    (pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json')
    .read_text(encoding='utf-8')
)
SOLUTIONS = pathlib.Path(__file__).resolve().parents[1] / 'solutions'
SLUG = 'nth-highest-salary'
SCHEMA = META[SLUG]['databaseSchema']
FILENAME = '177-nth-highest-salary.sql'
SOURCE = (SOLUTIONS / FILENAME).read_text(encoding='utf-8')

ROW_ORDER = {'Employee': ['id', 'salary']}
FUNCTION_SIGNATURE = 'NthHighestSalary(N INT) RETURNS INT'


def example_cases():
    raw = META[SLUG]['exampleTestcases'] or ''
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def function_body(source=SOURCE):
    """The text between the two `$$` delimiters, without the trailing semicolon."""
    parts = source.split('$$')
    assert len(parts) == 3, f'expected one $$-quoted body, found {len(parts) - 1}'
    return parts[1].strip().rstrip(';')


def query_for(n: int, source=SOURCE) -> str:
    """The function body with its parameter replaced by the literal n."""
    substituted, replacements = re.subn(r'\bN\b', str(n), function_body(source))
    assert replacements, 'the function body never mentions its parameter N'
    return substituted


def rows_in_schema_order(table, row_order, table_rows):
    # The metadata declares this table as (Id, Salary) while the judge's headers
    # use (id, salary); SQL identifiers are case-insensitive, so the lookup is too.
    schema_columns = [column.lower() for column in SCHEMA[table]]
    indexes = [schema_columns.index(column.lower()) for column in row_order]
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


def scalar_or_none(rows):
    """The value a scalar function returns for a 0-or-1-row query."""
    return rows[0][0] if rows else None


def oracle_limit_offset(connection, n: int):
    return query(connection, f'''
        SELECT DISTINCT salary
        FROM Employee
        WHERE salary IS NOT NULL
        ORDER BY salary DESC
        LIMIT 1 OFFSET {n - 1}
    ''')


def oracle_correlated_count(connection, n: int):
    return query(connection, f'''
        SELECT DISTINCT e.salary
        FROM Employee AS e
        WHERE e.salary IS NOT NULL
          AND (SELECT COUNT(DISTINCT s.salary)
               FROM Employee AS s
               WHERE s.salary IS NOT NULL AND s.salary > e.salary) = {n - 1}
    ''')


class NthHighestSalaryTests(unittest.TestCase):
    def value_for(self, rows, n: int):
        """The value the function would return, plus both oracle checks."""
        with connection_for(rows) as connection:
            result = scalar_or_none(query(connection, query_for(n)))
            self.assertEqual(result, scalar_or_none(oracle_limit_offset(connection, n)), f'n={n}')
            self.assertEqual(result, scalar_or_none(oracle_correlated_count(connection, n)), f'n={n}')
        return result

    def employees(self, salaries):
        return {'Employee': [(index + 1, salary) for index, salary in enumerate(salaries)]}

    def expected(self, salaries, n: int):
        distinct = sorted({salary for salary in salaries if salary is not None}, reverse=True)
        return distinct[n - 1] if 1 <= n <= len(distinct) else None

    def test_official_example_one(self):
        with connection_for_case(example_cases()[0]) as connection:
            self.assertEqual(scalar_or_none(query(connection, query_for(2))), 200)

    def test_official_example_two(self):
        with connection_for_case(example_cases()[1]) as connection:
            self.assertEqual(scalar_or_none(query(connection, query_for(2))), None)

    def test_n_walks_down_the_distinct_salaries(self):
        for n, want in ((1, 300), (2, 200), (3, 100), (4, None), (5, None)):
            with self.subTest(n=n):
                self.assertEqual(self.value_for(self.employees([100, 200, 300]), n), want)

    def test_n_larger_than_the_row_count_returns_null(self):
        # n = 3 with three rows of only two distinct salaries, and n = 1000.
        self.assertEqual(self.value_for(self.employees([100, 200, 200]), 3), None)
        self.assertEqual(self.value_for(self.employees([100, 200, 300]), 1000), None)

    def test_duplicates_are_counted_once(self):
        salaries = [300, 300, 200, 200, 100]
        for n, want in ((1, 300), (2, 200), (3, 100), (4, None)):
            with self.subTest(n=n):
                self.assertEqual(self.value_for(self.employees(salaries), n), want)

    def test_single_row_and_empty_table(self):
        for n in (1, 2, 3):
            with self.subTest(n=n, rows=1):
                self.assertEqual(self.value_for(self.employees([500]), n), 500 if n == 1 else None)
            with self.subTest(n=n, rows=0):
                self.assertEqual(self.value_for(self.employees([]), n), None)

    def test_negative_and_boundary_salaries(self):
        self.assertEqual(self.value_for(self.employees([-(2 ** 31), 0, 2 ** 31 - 1]), 1), 2 ** 31 - 1)
        self.assertEqual(self.value_for(self.employees([-(2 ** 31), 0, 2 ** 31 - 1]), 3), -(2 ** 31))
        self.assertEqual(self.value_for(self.employees([-1, -2, -3]), 1), -1)
        self.assertEqual(self.value_for(self.employees([-1, -2, -3]), 3), -3)

    def test_null_salaries_are_ignored(self):
        self.assertEqual(self.value_for(self.employees([None, 300, 200]), 1), 300)
        self.assertEqual(self.value_for(self.employees([None, 300, 200]), 2), 200)
        self.assertEqual(self.value_for(self.employees([None, 300, 200]), 3), None)

    def test_randomised_databases(self):
        rng = random.Random(1770)
        for case in range(300):
            salaries = [rng.randint(-4, 4) for _ in range(rng.randint(0, 10))]
            n = rng.randint(1, 6)
            with self.subTest(case=case, n=n, salaries=salaries):
                self.assertEqual(
                    self.value_for(self.employees(salaries), n),
                    self.expected(salaries, n),
                )

    def test_randomised_wide_values(self):
        rng = random.Random(1771)
        for case in range(100):
            salaries = [rng.randint(-(2 ** 31), 2 ** 31 - 1) for _ in range(rng.randint(0, 15))]
            n = rng.randint(1, 5)
            with self.subTest(case=case, n=n):
                self.assertEqual(
                    self.value_for(self.employees(salaries), n),
                    self.expected(salaries, n),
                )

    def test_constraint_sized(self):
        # The statement sets no row bound; 5000 employees, several n values.
        rng = random.Random(1772)
        salaries = [rng.randint(0, 400) for _ in range(5000)]
        with connection_for(self.employees(salaries)) as connection:
            for n in (1, 2, 3, 50, 401, 5000, 5001):
                with self.subTest(n=n):
                    self.assertEqual(
                        scalar_or_none(query(connection, query_for(n))),
                        self.expected(salaries, n),
                    )
        spread = list(range(5000))
        self.assertEqual(self.value_for(self.employees(spread), 1), 4999)
        self.assertEqual(self.value_for(self.employees(spread), 5000), 0)
        self.assertEqual(self.value_for(self.employees(spread), 5001), None)

    def test_body_really_uses_the_parameter(self):
        # Guards the substitution test itself: a body that ignored N would make
        # every assertion above vacuous.
        self.assertRegex(function_body(), r'\bN\b')
        self.assertNotEqual(query_for(1), query_for(2))
        self.assertNotRegex(query_for(2), r'\bN\b')

    def test_file_shape_is_one_function_statement(self):
        self.assertEqual(SOURCE.count('$$'), 2, 'exactly one $$-quoted body')
        self.assertIn(FUNCTION_SIGNATURE, SOURCE)
        self.assertIn('CREATE OR REPLACE FUNCTION', SOURCE)
        self.assertIn('LANGUAGE sql', SOURCE)
        body = '\n'.join(
            line for line in SOURCE.splitlines() if not line.strip().startswith('--')
        ).strip()
        self.assertTrue(body.upper().startswith('CREATE OR REPLACE FUNCTION'))
        self.assertTrue(body.endswith(';'))
        # Exactly one statement: nothing follows the closing semicolon, the only
        # other semicolon is the one inside the $$-quoted body, and there is a
        # single function definition.
        before, _, after = body.rpartition(';')
        self.assertEqual(after.strip(), '')
        self.assertEqual(body.count('CREATE OR REPLACE FUNCTION'), 1)
        self.assertEqual(body.count(';'), 2)
        self.assertEqual(before.count(';'), 1)
        self.assertEqual(body.split('$$')[1].count(';'), 1, 'the inner semicolon is inside the body')
        # The function's own SELECT is the only query in the file.
        self.assertEqual(len(re.findall(r'\bSELECT\b', body)), 3)


if __name__ == '__main__':
    unittest.main()
