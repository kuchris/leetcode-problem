"""Tests for 181. Employees Earning More Than Their Managers.

Oracles:
  - ``SUBQUERY_ORACLE``: a correlated scalar subquery that reads the manager's
    salary instead of joining a second copy of the table, so it shares no join
    structure with the solution.
  - ``python_oracle``: a dictionary lookup in Python.

Employees whose manager is missing are the interesting case. The solution's
inner join drops them, and so does the subquery, because a scalar subquery that
matches no row yields NULL and "salary > NULL" is unknown rather than true. A
test asserts that both readings drop them, and the official example shows it too:
Sam and Max carry a NULL managerId and neither appears in the expected output.
"""

import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'employees-earning-more-than-their-managers'
SOLUTION = load_sql('181-employees-earning-more-than-their-managers.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: no second copy of the table, just a correlated read of
# the one manager salary. A missing manager makes the comparison unknown.
SUBQUERY_ORACLE = """
SELECT employee.name AS "Employee"
FROM Employee AS employee
WHERE employee.salary > (
    SELECT manager.salary
    FROM Employee AS manager
    WHERE manager.id = employee.managerId
)
"""

COLUMN = 'Employee'


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


def python_oracle(employees):
    """Look the manager up in a dict; a NULL or missing manager never qualifies."""
    by_id = {row[0]: row for row in employees}
    found = []
    for _id, name, salary, manager_id in employees:
        manager = by_id.get(manager_id)
        if manager is not None and salary > manager[2]:
            found.append((name,))
    return as_multiset(found)


def employees(*rows):
    return {'Employee': [list(row) for row in rows]}


class EmployeesEarningMoreThanTheirManagersTests(unittest.TestCase):
    def agree(self, rows):
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, SUBQUERY_ORACLE),
                         'solution and correlated-subquery oracle disagree')
        self.assertEqual(result, python_oracle(rows['Employee']),
                         'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        # Joe's 70000 beats manager Sam's 60000; Henry's 80000 loses to Max's
        # 90000; Sam and Max have a NULL managerId and cannot qualify.
        self.assertEqual(self.agree(EXAMPLE), [('Joe',)])

    def test_output_column_is_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), [COLUMN])

    def test_manager_id_pointing_at_a_missing_row_is_dropped(self):
        self.assertEqual(self.agree(employees((1, 'Solo', 90000, 99))), [])

    def test_null_manager_id_is_dropped(self):
        self.assertEqual(self.agree(employees((1, 'Boss', 90000, None))), [])

    def test_equal_salaries_do_not_qualify(self):
        rows = employees((1, 'Boss', 100, None), (2, 'Twin', 100, 1))
        self.assertEqual(self.agree(rows), [])

    def test_each_employee_is_compared_with_its_own_manager(self):
        rows = employees(
            (1, 'Top', 500, None),
            (2, 'Middle', 300, 1),
            (3, 'Bottom', 400, 2),
        )
        self.assertEqual(self.agree(rows), [('Bottom',)])

    def test_every_link_of_a_chain_can_qualify(self):
        rows = employees(
            (1, 'A', 10, None),
            (2, 'B', 20, 1),
            (3, 'C', 30, 2),
            (4, 'D', 40, 3),
        )
        self.assertEqual(self.agree(rows), [('B',), ('C',), ('D',)])

    def test_a_manager_is_also_an_employee(self):
        # Lead beats Chief and loses to nobody; Junior beats Lead.
        rows = employees(
            (1, 'Chief', 1000, None),
            (2, 'Lead', 1100, 1),
            (3, 'Junior', 1200, 2),
        )
        self.assertEqual(self.agree(rows), [('Junior',), ('Lead',)])

    def test_one_manager_can_be_beaten_by_several_reports(self):
        rows = employees(
            (1, 'Boss', 100, None),
            (2, 'Low', 90, 1),
            (3, 'High', 200, 1),
            (4, 'Mid', 150, 1),
        )
        self.assertEqual(self.agree(rows), [('High',), ('Mid',)])

    def test_empty_table(self):
        self.assertEqual(self.agree({'Employee': []}), [])

    def test_random_tables(self):
        rng = random.Random(1810)
        for trial in range(400):
            size = rng.randint(0, 12)
            ids = list(range(1, size + 1))
            rows = []
            for employee_id in ids:
                candidates = [other for other in ids if other != employee_id]
                roll = rng.random()
                if roll < 0.2 or not candidates:
                    manager_id = None
                elif roll < 0.3:
                    manager_id = size + rng.randint(1, 5)  # dangling reference
                else:
                    manager_id = rng.choice(candidates)
                rows.append([employee_id, f'e{employee_id}',
                             rng.randrange(0, 5) * 1000, manager_id])
            with self.subTest(trial=trial, size=size):
                self.agree({'Employee': rows})


if __name__ == '__main__':
    unittest.main()
