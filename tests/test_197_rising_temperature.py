"""197. Rising Temperature -- tests for solutions/197-rising-temperature.sql.

Harness limit, stated plainly: _sql.py runs SQLite and no PostgreSQL is installed
on this machine, while the judge runs PostgreSQL 16. SQLite has no `date + integer`
operator and PostgreSQL has no `date(x, '+1 day')` function, so the submitted text
cannot be executed locally as written. The test therefore runs the same statement
with exactly one documented substitution -- PostgreSQL's `p.recordDate + 1`
becomes SQLite's `date(p.recordDate, '+1 day')` -- and asserts the substitution
actually applied, so a solution that stops containing the construct fails loudly
instead of quietly testing a different query.

What that leaves verified here is the logic: comparing against the calendar day
before (not merely the previous row), gaps, month and year boundaries, leap day,
id order, and empty input. The dialect itself is *not* verified locally and needs
the judge's confirmation.

Oracle: a Python implementation over datetime.date that steps one calendar day
back and compares temperatures, using no SQL at all.
"""
import datetime
import json
import unittest
from pathlib import Path

from _sql import build, load_sql, query

SOLUTION = '197-rising-temperature.sql'
SLUG = 'rising-temperature'
META_PATH = (
    Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
)
POSTGRES_DAY_OFFSET = 'p.recordDate + 1'
SQLITE_DAY_OFFSET = "date(p.recordDate, '+1 day')"

CASES = [
    # The statement's own example.
    [[1, '2015-01-01', 10], [2, '2015-01-02', 25], [3, '2015-01-03', 20], [4, '2015-01-04', 30]],
    # A single day has no yesterday.
    [[1, '2015-01-01', 10]],
    [],
    # A gap: the previous *row* is two days earlier, so nothing is rising.
    [[1, '2015-01-01', 10], [2, '2015-01-03', 25]],
    # Month boundary.
    [[1, '2015-01-31', 10], [2, '2015-02-01', 11]],
    # Year boundary.
    [[1, '2015-12-31', 10], [2, '2016-01-01', 5], [3, '2016-01-02', 7]],
    # Leap day.
    [[1, '2020-02-28', 10], [2, '2020-02-29', 11], [3, '2020-03-01', 9]],
    # Ids out of date order; the answer is reported by id.
    [[2, '2015-01-02', 30], [1, '2015-01-01', 20], [4, '2015-01-04', 5], [3, '2015-01-03', 40]],
    # Equal temperatures are not rising.
    [[1, '2015-01-01', 20], [2, '2015-01-02', 20]],
    # Falls, then rises.
    [[1, '2015-01-01', 25], [2, '2015-01-02', 20], [3, '2015-01-03', 21]],
    # Sparse dates interleaved with dense ones.
    [[1, '2015-03-01', 5], [2, '2015-03-02', 6], [3, '2015-03-10', 40], [4, '2015-03-11', 41]],
]


def problem_meta():
    return json.loads(META_PATH.read_text(encoding='utf-8'))[SLUG]


def example_rows(schema, meta):
    """The example's rows, in schema column order (cross-checked, not assumed)."""
    payload = json.loads(meta['exampleTestcases'])
    rows = {}
    for table, columns in schema.items():
        declared = [name.lower() for name in payload['headers'][table]]
        expected = [name.lower() for name in columns]
        if declared != expected:
            raise AssertionError(f'{table}: example headers {declared} != schema {expected}')
        rows[table] = payload['rows'][table]
    return rows


def sqlite_statement():
    """The submitted statement, with its PostgreSQL day offset spelled for SQLite."""
    statement = load_sql(SOLUTION)
    if POSTGRES_DAY_OFFSET not in statement:
        raise AssertionError(
            f'{SOLUTION} no longer contains {POSTGRES_DAY_OFFSET!r}; the SQLite '
            'substitution below would silently run an untested statement'
        )
    return statement.replace(POSTGRES_DAY_OFFSET, SQLITE_DAY_OFFSET)


def previous_day(date_text):
    return (datetime.date.fromisoformat(date_text) - datetime.timedelta(days=1)).isoformat()


def python_expectation(weather_rows):
    """Compare each day with the day before it, if that day is in the table."""
    by_date = {}
    for identifier, date_text, temperature in weather_rows:
        if date_text in by_date:
            raise AssertionError('case violates the no-duplicate-recordDate guarantee')
        by_date[date_text] = (identifier, temperature)
    rising = [
        identifier
        for identifier, date_text, temperature in weather_rows
        if previous_day(date_text) in by_date
        and temperature > by_date[previous_day(date_text)][1]
    ]
    return sorted(rising)


def rising_ids(schema, weather_rows, statement=None):
    connection = build(schema, {'Weather': weather_rows})
    rows = query(connection, statement or sqlite_statement())
    return [row[0] for row in rows]


class RisingTemperatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = problem_meta()
        cls.schema = cls.meta['databaseSchema']

    def test_solution_still_carries_the_postgresql_day_offset(self):
        """The file must stay PostgreSQL: the judge is not running SQLite."""
        statement = load_sql(SOLUTION)
        self.assertIn(POSTGRES_DAY_OFFSET, statement)
        self.assertNotIn("date(", statement, 'SQLite spelling must not reach the submitted file')

    def test_official_example(self):
        rows = example_rows(self.schema, self.meta)['Weather']
        self.assertEqual(
            rows,
            [[1, '2015-01-01', 10], [2, '2015-01-02', 25], [3, '2015-01-03', 20], [4, '2015-01-04', 30]],
        )
        self.assertEqual(rising_ids(self.schema, rows), [2, 4])

    def test_matches_the_python_oracle(self):
        for rows in CASES:
            with self.subTest(rows=rows):
                self.assertEqual(rising_ids(self.schema, rows), python_expectation(rows))

    def test_a_gap_is_not_yesterday(self):
        """The previous row being two days earlier must not count as yesterday."""
        rows = [[1, '2015-01-01', 10], [2, '2015-01-03', 25]]
        self.assertEqual(rising_ids(self.schema, rows), [])
        self.assertEqual(python_expectation(rows), [])

    def test_month_and_year_boundaries(self):
        month = [[1, '2015-01-31', 10], [2, '2015-02-01', 11]]
        year = [[1, '2015-12-31', 10], [2, '2016-01-01', 15]]
        leap = [[1, '2020-02-28', 10], [2, '2020-02-29', 11]]
        self.assertEqual(rising_ids(self.schema, month), [2])
        self.assertEqual(rising_ids(self.schema, year), [2])
        self.assertEqual(rising_ids(self.schema, leap), [2])

    def test_result_is_ids_in_ascending_order(self):
        rows = [[30, '2015-05-10', 40], [10, '2015-05-11', 41], [20, '2015-05-12', 42]]
        self.assertEqual(rising_ids(self.schema, rows), [10, 20])

    def test_equal_temperatures_are_not_rising(self):
        rows = [[1, '2015-01-01', 20], [2, '2015-01-02', 20]]
        self.assertEqual(rising_ids(self.schema, rows), [])

    def test_empty_table_returns_no_rows(self):
        self.assertEqual(rising_ids(self.schema, []), [])

    def test_every_day_rising(self):
        rows = [[day, f'2015-06-{day:02d}', day * 10] for day in range(1, 11)]
        self.assertEqual(rising_ids(self.schema, rows), list(range(2, 11)))


if __name__ == '__main__':
    unittest.main()
