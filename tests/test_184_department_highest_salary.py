"""Tests for 184. Department Highest Salary.

Oracles:
  - ``MAX_ORACLE``: a correlated MAX subquery that asks, per employee, whether
    their salary equals their own department's maximum. No window function and
    no rank, so it does not share the solution's mechanism.
  - ``python_oracle``: computes each department's maximum with a dict.

Ties are the point of the problem: two employees sharing a department maximum
must both appear. Departments with no employees, and employees whose
departmentId matches no department, must not appear, because neither can be
reported together with a department name.
"""

import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'department-highest-salary'
SOLUTION = load_sql('184-department-highest-salary.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: compare each salary with its department's maximum.
MAX_ORACLE = """
SELECT department.name AS "Department",
       employee.name AS "Employee",
       employee.salary AS "Salary"
FROM Employee AS employee
INNER JOIN Department AS department ON department.id = employee.departmentId
WHERE employee.salary = (
    SELECT MAX(other.salary)
    FROM Employee AS other
    WHERE other.departmentId = employee.departmentId
)
"""

COLUMNS = ['Department', 'Employee', 'Salary']


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


def python_oracle(rows):
    names = {department[0]: department[1] for department in rows['Department']}
    highest = {}
    for _id, _name, salary, department_id in rows['Employee']:
        if department_id in names:
            highest[department_id] = max(highest.get(department_id, salary), salary)
    found = []
    for _id, name, salary, department_id in rows['Employee']:
        if department_id in highest and salary == highest[department_id]:
            found.append((names[department_id], name, salary))
    return as_multiset(found)


def roster(employees, departments):
    return {'Employee': [list(row) for row in employees],
            'Department': [list(row) for row in departments]}


class DepartmentHighestSalaryTests(unittest.TestCase):
    def agree(self, rows):
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, MAX_ORACLE),
                         'solution and correlated-MAX oracle disagree')
        self.assertEqual(result, python_oracle(rows), 'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        self.assertEqual(
            self.agree(EXAMPLE),
            as_multiset([
                ('IT', 'Jim', 90000),
                ('IT', 'Max', 90000),
                ('Sales', 'Henry', 80000),
            ]),
        )

    def test_output_columns_are_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), COLUMNS)

    def test_a_tie_on_the_maximum_reports_every_employee_involved(self):
        rows = roster([[1, 'A', 500, 1], [2, 'B', 500, 1]], [[1, 'IT']])
        self.assertEqual(self.agree(rows), as_multiset([('IT', 'A', 500), ('IT', 'B', 500)]))

    def test_a_single_employee_department(self):
        rows = roster([[1, 'Solo', 900, 1]], [[1, 'IT']])
        self.assertEqual(self.agree(rows), [('IT', 'Solo', 900)])

    def test_several_departments_are_ranked_independently(self):
        rows = roster(
            [[1, 'A', 100, 1], [2, 'B', 200, 1], [3, 'C', 50, 2], [4, 'D', 60, 2]],
            [[1, 'IT'], [2, 'Sales']],
        )
        self.assertEqual(self.agree(rows), as_multiset([('IT', 'B', 200), ('Sales', 'D', 60)]))

    def test_a_department_without_employees_is_not_reported(self):
        rows = roster([[1, 'A', 100, 1]], [[1, 'IT'], [2, 'Empty']])
        self.assertEqual(self.agree(rows), [('IT', 'A', 100)])

    def test_an_employee_outside_every_department_is_not_reported(self):
        rows = roster([[1, 'A', 999, 7]], [[1, 'IT']])
        self.assertEqual(self.agree(rows), [])

    def test_every_employee_tied_reports_all_of_them(self):
        rows = roster([[1, 'A', 10, 1], [2, 'B', 10, 1], [3, 'C', 10, 1]], [[1, 'IT']])
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 10), ('IT', 'B', 10), ('IT', 'C', 10)]),
        )

    def test_empty_employee_table(self):
        rows = roster([], [[1, 'IT']])
        self.assertEqual(self.agree(rows), [])

    def test_no_departments(self):
        rows = roster([[1, 'A', 10, 1]], [])
        self.assertEqual(self.agree(rows), [])

    def test_random_tables(self):
        rng = random.Random(1840)
        for trial in range(400):
            department_count = rng.randint(0, 4)
            departments = [[index + 1, f'd{index + 1}'] for index in range(department_count)]
            employees = []
            for employee_id in range(1, rng.randint(2, 14)):
                if department_count and rng.random() < 0.9:
                    department_id = rng.randint(1, department_count)
                else:
                    department_id = department_count + rng.randint(1, 3)  # dangling
                employees.append([employee_id, f'e{employee_id}',
                                  rng.randrange(1, 5) * 1000, department_id])
            rows = {'Employee': employees, 'Department': departments}
            with self.subTest(trial=trial, departments=department_count):
                self.agree(rows)


if __name__ == '__main__':
    unittest.main()
