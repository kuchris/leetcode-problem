"""Tests for 183. Customers Who Never Order.

Oracles:
  - ``NOT_EXISTS_ORACLE``: keeps a customer when no order references them, which
    asks the question once per customer instead of joining and inspecting the
    joined rows.
  - ``python_oracle``: collects the ordering customer ids into a Python set.
  - ``NOT_IN_TRAP``: the NOT IN form, asserted to return nothing as soon as
    Orders holds a NULL customerId. That is the reason the solution joins instead
    of using NOT IN, and the test keeps the reason honest rather than asserted in
    a comment alone.
"""

import json
import random
import unittest
from pathlib import Path

from _sql import as_multiset, build, load_sql, query

SLUG = 'customers-who-never-order'
SOLUTION = load_sql('183-customers-who-never-order.sql')

STATE = Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json'
META = json.loads(STATE.read_text(encoding='utf-8'))[SLUG]
SCHEMA = META['databaseSchema']
EXAMPLE = json.loads(META['exampleTestcases'])['rows']

# Second implementation: ask the question per customer.
NOT_EXISTS_ORACLE = """
SELECT customer.name AS "Customers"
FROM Customers AS customer
WHERE NOT EXISTS (
    SELECT 1
    FROM Orders AS orders
    WHERE orders.customerId = customer.id
)
"""

# Deliberately the wrong tool: one NULL customerId makes "NOT IN" unknown for
# every customer, so this returns nothing at all.
NOT_IN_TRAP = """
SELECT customer.name AS "Customers"
FROM Customers AS customer
WHERE customer.id NOT IN (SELECT customerId FROM Orders)
"""

COLUMN = 'Customers'


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
    ordering = {order[1] for order in rows['Orders']}
    return as_multiset(
        [(customer[1],) for customer in rows['Customers'] if customer[0] not in ordering]
    )


class CustomersWhoNeverOrderTests(unittest.TestCase):
    def agree(self, rows):
        result = run(rows, SOLUTION)
        self.assertEqual(result, run(rows, NOT_EXISTS_ORACLE),
                         'solution and NOT EXISTS oracle disagree')
        self.assertEqual(result, python_oracle(rows), 'solution and Python oracle disagree')
        return result

    def test_official_example(self):
        self.assertEqual(self.agree(EXAMPLE), [('Henry',), ('Max',)])

    def test_output_column_is_named_as_in_the_statement(self):
        self.assertEqual(column_names(EXAMPLE, SOLUTION), [COLUMN])

    def test_a_customer_with_orders_is_excluded(self):
        rows = {'Customers': [[1, 'Joe']], 'Orders': [[1, 1]]}
        self.assertEqual(self.agree(rows), [])

    def test_several_orders_for_one_customer_still_exclude_them_once(self):
        rows = {'Customers': [[1, 'Joe'], [2, 'Ann']],
                'Orders': [[1, 1], [2, 1], [3, 1]]}
        self.assertEqual(self.agree(rows), [('Ann',)])

    def test_empty_orders_returns_every_customer(self):
        rows = {'Customers': [[1, 'Joe'], [2, 'Ann']], 'Orders': []}
        self.assertEqual(self.agree(rows), [('Ann',), ('Joe',)])

    def test_no_customers(self):
        rows = {'Customers': [], 'Orders': [[1, 1]]}
        self.assertEqual(self.agree(rows), [])

    def test_orders_referencing_unknown_customers_do_not_hide_anyone(self):
        rows = {'Customers': [[1, 'Joe'], [2, 'Ann']], 'Orders': [[1, 99]]}
        self.assertEqual(self.agree(rows), [('Ann',), ('Joe',)])

    def test_not_in_collapses_once_an_order_has_a_null_customer_id(self):
        rows = {'Customers': [[1, 'Joe'], [2, 'Henry']],
                'Orders': [[1, 1], [2, None]]}
        self.assertEqual(self.agree(rows), [('Henry',)])
        self.assertEqual(run(rows, NOT_IN_TRAP), [],
                         'NOT IN no longer shows the trap on this data')

    def test_random_tables(self):
        rng = random.Random(1830)
        for trial in range(400):
            customer_count = rng.randint(0, 10)
            customers = [[index + 1, f'c{index + 1}'] for index in range(customer_count)]
            orders = []
            for order_id in range(1, rng.randint(1, 14)):
                if customer_count and rng.random() < 0.85:
                    customer_id = rng.randint(1, customer_count)
                else:
                    customer_id = customer_count + rng.randint(1, 3)  # dangling
                orders.append([order_id, customer_id])
            rows = {'Customers': customers, 'Orders': orders}
            with self.subTest(trial=trial, customers=customer_count, orders=len(orders)):
                self.agree(rows)


if __name__ == '__main__':
    unittest.main()
