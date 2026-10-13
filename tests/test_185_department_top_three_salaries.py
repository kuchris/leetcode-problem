"""Tests for 185. Department Top Three Salaries.

Oracles:
  - ``COUNT_DISTINCT_ORACLE``: counts, for each employee, how many distinct
    salaries in the same department are strictly larger. Fewer than three of
    those means the salary sits inside the top three. No window function and no
    rank, so it does not share the solution's mechanism.
  - ``python_oracle``: the same question answered with Python sets.

"Top three" counts distinct salary levels, not employees, so a salary shared by
several employees keeps all of them, and a department with fewer than three
distinct salaries reports everyone. Both are asserted directly, because RANK
instead of DENSE_RANK would fail exactly those two cases.
"""

import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'department-top-three-salaries'
SOLUTION = load_sql('185-department-top-three-salaries.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: a salary is in the top three distinct salaries of its
# department when fewer than three distinct salaries there are strictly larger.
COUNT_DISTINCT_ORACLE = """
SELECT department.name AS "Department",
       employee.name AS "Employee",
       employee.salary AS "Salary"
FROM Employee AS employee
INNER JOIN Department AS department ON department.id = employee.departmentId
WHERE (
    SELECT COUNT(DISTINCT higher.salary)
    FROM Employee AS higher
    WHERE higher.departmentId = employee.departmentId
      AND higher.salary > employee.salary
) < 3
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
    salaries = {}
    for _id, _name, salary, department_id in rows['Employee']:
        if department_id in names:
            salaries.setdefault(department_id, set()).add(salary)
    found = []
    for _id, name, salary, department_id in rows['Employee']:
        if department_id not in names:
            continue
        larger = {value for value in salaries[department_id] if value > salary}
        if len(larger) < 3:
            found.append((names[department_id], name, salary))
    return as_multiset(found)


def roster(employees, departments):
    return {'Employee': [list(row) for row in employees],
            'Department': [list(row) for row in departments]}


class DepartmentTopThreeSalariesTests(unittest.TestCase):
    def agree(self, rows):
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, COUNT_DISTINCT_ORACLE),
                         'solution and COUNT DISTINCT oracle disagree')
        self.assertEqual(result, python_oracle(rows), 'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        self.assertEqual(
            self.agree(EXAMPLE),
            as_multiset([
                ('IT', 'Max', 90000),
                ('IT', 'Joe', 85000),
                ('IT', 'Randy', 85000),
                ('IT', 'Will', 70000),
                ('Sales', 'Henry', 80000),
                ('Sales', 'Sam', 60000),
            ]),
        )

    def test_output_columns_are_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), COLUMNS)

    def test_a_department_with_two_distinct_salaries_reports_everyone(self):
        rows = roster([[1, 'A', 100, 1], [2, 'B', 90, 1], [3, 'C', 90, 1]], [[1, 'IT']])
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 100), ('IT', 'B', 90), ('IT', 'C', 90)]),
        )

    def test_exactly_three_distinct_salaries_report_everyone(self):
        rows = roster(
            [[1, 'A', 300, 1], [2, 'B', 200, 1], [3, 'C', 100, 1], [4, 'D', 100, 1]],
            [[1, 'IT']],
        )
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 300), ('IT', 'B', 200),
                         ('IT', 'C', 100), ('IT', 'D', 100)]),
        )

    def test_a_tie_on_the_highest_salary_does_not_consume_a_rank(self):
        # Salaries 100, 100, 90, 80, 70 hold four distinct levels, so the top
        # three are 100, 90 and 80 and both employees on 100 stay. RANK would
        # number these 1, 1, 3, 4, 5 and drop the employee on 80, which is the
        # concrete reason DENSE_RANK is the function used here.
        rows = roster(
            [[1, 'A', 100, 1], [2, 'B', 100, 1], [3, 'C', 90, 1],
             [4, 'D', 80, 1], [5, 'E', 70, 1]],
            [[1, 'IT']],
        )
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 100), ('IT', 'B', 100),
                         ('IT', 'C', 90), ('IT', 'D', 80)]),
        )

    def test_a_tie_at_the_third_level_keeps_every_tied_employee(self):
        # Distinct salaries 100, 90, 80, 70: the top three are 100/90/80, so both
        # employees on 80 stay and the one on 70 goes.
        rows = roster(
            [[1, 'A', 100, 1], [2, 'B', 90, 1], [3, 'C', 80, 1],
             [4, 'D', 80, 1], [5, 'E', 70, 1]],
            [[1, 'IT']],
        )
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 100), ('IT', 'B', 90),
                         ('IT', 'C', 80), ('IT', 'D', 80)]),
        )

    def test_only_the_top_three_distinct_salaries_survive(self):
        rows = roster(
            [[1, 'A', 500, 1], [2, 'B', 400, 1], [3, 'C', 300, 1],
             [4, 'D', 200, 1], [5, 'E', 100, 1]],
            [[1, 'IT']],
        )
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 500), ('IT', 'B', 400), ('IT', 'C', 300)]),
        )

    def test_every_employee_tied_reports_all_of_them(self):
        rows = roster([[1, 'A', 50, 1], [2, 'B', 50, 1], [3, 'C', 50, 1]], [[1, 'IT']])
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'A', 50), ('IT', 'B', 50), ('IT', 'C', 50)]),
        )

    def test_departments_are_ranked_independently(self):
        rows = roster(
            [[1, 'A', 10, 1], [2, 'B', 20, 1], [3, 'C', 30, 1], [4, 'D', 40, 1],
             [5, 'E', 5, 2]],
            [[1, 'IT'], [2, 'Sales']],
        )
        self.assertEqual(
            self.agree(rows),
            as_multiset([('IT', 'B', 20), ('IT', 'C', 30), ('IT', 'D', 40),
                         ('Sales', 'E', 5)]),
        )

    def test_a_department_without_employees_is_not_reported(self):
        rows = roster([[1, 'A', 10, 1]], [[1, 'IT'], [2, 'Empty']])
        self.assertEqual(self.agree(rows), [('IT', 'A', 10)])

    def test_an_employee_outside_every_department_is_not_reported(self):
        rows = roster([[1, 'A', 10, 7], [2, 'B', 20, 7]], [[1, 'IT']])
        self.assertEqual(self.agree(rows), [])

    def test_empty_employee_table(self):
        self.assertEqual(self.agree(roster([], [[1, 'IT']])), [])

    def test_no_departments(self):
        self.assertEqual(self.agree(roster([[1, 'A', 10, 1]], [])), [])

    def test_random_tables_with_few_distinct_salaries(self):
        # Four distinct salaries per department, so the "more than three distinct
        # salaries" boundary and its ties are hit constantly.
        rng = random.Random(1850)
        for trial in range(400):
            department_count = rng.randint(0, 4)
            departments = [[index + 1, f'd{index + 1}'] for index in range(department_count)]
            employees = []
            for employee_id in range(1, rng.randint(2, 16)):
                if department_count and rng.random() < 0.9:
                    department_id = rng.randint(1, department_count)
                else:
                    department_id = department_count + rng.randint(1, 3)  # dangling
                employees.append([employee_id, f'e{employee_id}',
                                  rng.randrange(1, 5) * 1000, department_id])
            rows = {'Employee': employees, 'Department': departments}
            with self.subTest(trial=trial, departments=department_count):
                self.agree(rows)

    def test_random_tables_wider_salary_range(self):
        rng = random.Random(1851)
        for trial in range(200):
            department_count = rng.randint(1, 3)
            departments = [[index + 1, f'd{index + 1}'] for index in range(department_count)]
            employees = []
            for employee_id in range(1, rng.randint(2, 20)):
                department_id = rng.randint(1, department_count)
                employees.append([employee_id, f'e{employee_id}',
                                  rng.randrange(1, 11) * 1000, department_id])
            rows = {'Employee': employees, 'Department': departments}
            with self.subTest(trial=trial, departments=department_count):
                self.agree(rows)


if __name__ == '__main__':
    unittest.main()
