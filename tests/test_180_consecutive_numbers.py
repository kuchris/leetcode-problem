"""Tests for 180. Consecutive Numbers.

The answer is a set of numbers: the statement lists each qualifying number once
and fixes no row order, so results are compared as multisets.

Oracles:
  - ``ISLANDS_ORACLE``: the gaps-and-islands formulation. Rows are numbered over
    the id ordering, then inside each value that row number is subtracted from a
    second row number taken per value. The difference is constant exactly across
    adjacent rows carrying the same value, so grouping on it and keeping groups
    of three or more finds the runs without ever consulting a neighbouring row.
    That shares no structure with the solution's LAG.
  - ``python_oracle``: a third reading, in Python, that slides a three-row window
    over the id-ordered values.

The disagreement worth stating is id contiguity. The textbook "id + 1" self-join
reports nothing for ids 1, 5 and 9 holding the same value, while reading the rows
positionally reports that run. The ordering reading is the one implemented, and
the gap case is asserted explicitly so the choice is on the record.
"""

import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'consecutive-numbers'
SOLUTION = load_sql('180-consecutive-numbers.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: gaps and islands. DISTINCT is deliberate, because the
# expected answer names each number once however many runs it has.
ISLANDS_ORACLE = """
SELECT DISTINCT num AS "ConsecutiveNums"
FROM (
    SELECT num,
           ROW_NUMBER() OVER (ORDER BY id)
             - ROW_NUMBER() OVER (PARTITION BY num ORDER BY id) AS island
    FROM Logs
) AS islands
GROUP BY num, island
HAVING COUNT(*) >= 3
"""

COLUMN = 'ConsecutiveNums'


def run(rows, sql):
    """Run ``sql`` over a fresh database built from ``rows``."""
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


def python_oracle(log_rows):
    """Slide a window of three over the id-ordered values."""
    ordered = sorted(log_rows, key=lambda row: row[0])
    found = set()
    for start in range(len(ordered) - 2):
        window = [ordered[start + offset][1] for offset in range(3)]
        if window[0] == window[1] == window[2]:
            found.add(window[0])
    return as_multiset([(value,) for value in found])


def logs(*pairs):
    return {'Logs': [list(pair) for pair in pairs]}


class ConsecutiveNumbersTests(unittest.TestCase):
    def agree(self, rows):
        """Assert the solution, the SQL oracle and the Python oracle agree."""
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, ISLANDS_ORACLE),
                         'solution and gaps-and-islands oracle disagree')
        self.assertEqual(result, python_oracle(rows['Logs']),
                         'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        self.assertEqual(self.agree(EXAMPLE), [(1,)])

    def test_output_column_is_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), [COLUMN])

    def test_run_of_two_is_not_enough(self):
        self.assertEqual(self.agree(logs((1, 5), (2, 5))), [])

    def test_run_of_exactly_three(self):
        self.assertEqual(self.agree(logs((1, 7), (2, 7), (3, 7))), [(7,)])

    def test_run_of_four_reports_the_number_once(self):
        self.assertEqual(self.agree(logs((1, 4), (2, 4), (3, 4), (4, 4))), [(4,)])

    def test_two_separate_runs_of_the_same_number_report_it_once(self):
        rows = logs((1, 3), (2, 3), (3, 3), (4, 9), (5, 3), (6, 3), (7, 3))
        self.assertEqual(self.agree(rows), [(3,)])

    def test_gaps_between_ids_do_not_hide_a_run(self):
        # "id + 1" finds nothing on this data; reading the rows in id order does.
        self.assertEqual(self.agree(logs((1, 6), (5, 6), (9, 6))), [(6,)])

    def test_a_different_value_between_them_breaks_the_run(self):
        rows = logs((1, 6), (2, 6), (5, 9), (7, 6), (8, 6))
        self.assertEqual(self.agree(rows), [])

    def test_three_rows_are_not_enough_when_two_values_interleave(self):
        rows = logs((1, 2), (2, 2), (3, 3), (4, 2))
        self.assertEqual(self.agree(rows), [])

    def test_empty_table(self):
        self.assertEqual(self.agree({'Logs': []}), [])

    def test_null_num_cannot_form_a_reported_run(self):
        # "=" against NULL is unknown rather than true, so a NULL run is never
        # reported. Logs.num holds no NULLs in the statement's data.
        self.assertEqual(run(logs((1, None), (2, None), (3, None)), SOLUTION), [])

    def test_random_tables(self):
        rng = random.Random(1800)
        for trial in range(400):
            size = rng.randint(0, 40)
            # Unique ids drawn with gaps, so contiguity can never be assumed.
            ids = sorted(rng.sample(range(1, 400), size))
            values = [rng.randint(1, 4) for _ in ids]
            rows = {'Logs': [[i, v] for i, v in zip(ids, values)]}
            with self.subTest(trial=trial, size=size):
                self.agree(rows)

    def test_random_tables_built_from_runs(self):
        rng = random.Random(1801)
        for trial in range(200):
            rows = []
            next_id = 1
            for _ in range(rng.randint(1, 8)):
                value = rng.randint(1, 3)
                for _ in range(rng.randint(1, 5)):
                    if rng.random() < 0.25:
                        next_id += rng.randint(1, 3)  # a gap inside the run
                    rows.append([next_id, value])
                    next_id += 1
            with self.subTest(trial=trial, size=len(rows)):
                self.agree({'Logs': rows})


if __name__ == '__main__':
    unittest.main()
