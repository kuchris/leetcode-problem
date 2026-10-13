"""Tests for 175. Combine Two Tables.

The oracle is a second query written a different way: an inner join UNION ALL an
anti-join (`NOT EXISTS`), which reproduces LEFT JOIN semantics without using a
LEFT JOIN. Because the statement's example has at most one address per person, a
third oracle of correlated scalar subqueries is also checked there -- it is not
valid once a person can have two addresses (PostgreSQL would raise "more than one
row returned by a subquery"), and the multi-address tests say so.

The official expected table is hand-transcribed from the statement:

    | firstName | lastName | city          | state    |
    | Allen     | Wang     | Null          | Null     |
    | Bob       | Alice    | New York City | New York |

HARNESS NOTE: `_sql.build` inserts each table's rows positionally in the *schema*
column order, while the judge's `exampleTestcases` rows follow the `headers`
order -- and for Person those differ (schema: personId, firstName, lastName;
headers: personId, lastName, firstName). Both helpers below permute the rows
first, so the databases in this file really are the statement's tables; without
that the built Person rows would have first and last names swapped.
(tests/_sql.py is not this solver's file to change; reported to the lead.)
"""

import contextlib
import json
import pathlib
import random
import unittest

from _sql import as_multiset, build, load_sql, query

META = json.loads(
    (pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'agent' / 'state' / 'sql-shell-meta.json')
    .read_text(encoding='utf-8')
)
SOLUTIONS = pathlib.Path(__file__).resolve().parents[1] / 'solutions'
SLUG = 'combine-two-tables'
SCHEMA = META[SLUG]['databaseSchema']
QUERY = load_sql('175-combine-two-tables.sql')

# The order this file's fixtures write rows in: the order the statement displays
# the tables and the judge's headers use, which is NOT the schema order (the
# schema lists Person as personId, firstName, lastName).
ROW_ORDER = {
    'Person': ['personId', 'lastName', 'firstName'],
    'Address': ['addressId', 'personId', 'city', 'state'],
}

PERSON_COLUMNS = ROW_ORDER['Person']
ADDRESS_COLUMNS = ROW_ORDER['Address']

OFFICIAL = [
    ('Allen', 'Wang', None, None),
    ('Bob', 'Alice', 'New York City', 'New York'),
]


def example_cases():
    """The judge's own example testcases, one JSON document per line."""
    raw = META[SLUG]['exampleTestcases'] or ''
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def rows_in_schema_order(table, row_order, table_rows):
    schema_columns = list(SCHEMA[table])
    indexes = [schema_columns.index(column) for column in row_order]
    return [[row[index] for index in indexes] for row in table_rows]


def normalise(rows):
    """Every table's rows in schema column order."""
    return {
        table: rows_in_schema_order(table, ROW_ORDER[table], table_rows)
        for table, table_rows in rows.items()
    }


def case_rows(case):
    """The judge's rows for one case, in schema column order."""
    return {
        table: rows_in_schema_order(table, case['headers'][table], table_rows)
        for table, table_rows in (case.get('rows') or {}).items()
    }


@contextlib.contextmanager
def connection_for(rows):
    """A closed-on-exit in-memory database built from statement-order rows."""
    connection = build(SCHEMA, normalise(rows))
    try:
        yield connection
    finally:
        connection.close()


@contextlib.contextmanager
def connection_for_case(case):
    connection = build(SCHEMA, case_rows(case))
    try:
        yield connection
    finally:
        connection.close()


def oracle_union_anti_join(connection):
    """LEFT JOIN rebuilt as matched rows UNION ALL unmatched persons."""
    return query(connection, '''
        SELECT p.firstName, p.lastName, a.city, a.state
        FROM Person AS p
        JOIN Address AS a ON a.personId = p.personId
        UNION ALL
        SELECT p.firstName, p.lastName, NULL, NULL
        FROM Person AS p
        WHERE NOT EXISTS (SELECT 1 FROM Address AS a WHERE a.personId = p.personId)
    ''')


def oracle_scalar_subqueries(connection):
    """Correlated lookups; only valid while a person has at most one address."""
    return query(connection, '''
        SELECT p.firstName, p.lastName,
               (SELECT a.city FROM Address AS a WHERE a.personId = p.personId) AS city,
               (SELECT a.state FROM Address AS a WHERE a.personId = p.personId) AS state
        FROM Person AS p
    ''')


def at_most_one_address_per_person(rows):
    person_index = ADDRESS_COLUMNS.index('personId')
    counts = {}
    for row in rows.get('Address', []):
        counts[row[person_index]] = counts.get(row[person_index], 0) + 1
    return all(count <= 1 for count in counts.values())


class CombineTwoTablesTests(unittest.TestCase):
    def assert_solution_matches_oracle(self, rows):
        with connection_for(rows) as connection:
            result = query(connection, QUERY)
            self.assertEqual(as_multiset(result), as_multiset(oracle_union_anti_join(connection)))
            if at_most_one_address_per_person(rows):
                self.assertEqual(as_multiset(result), as_multiset(oracle_scalar_subqueries(connection)))
        return result

    def test_official_example(self):
        with connection_for_case(example_cases()[0]) as connection:
            self.assertEqual(query(connection, QUERY), OFFICIAL)

    def test_official_example_headers(self):
        with connection_for_case(example_cases()[0]) as connection:
            cursor = connection.execute(QUERY)
            try:
                self.assertEqual(
                    [description[0] for description in cursor.description],
                    ['firstName', 'lastName', 'city', 'state'],
                )
            finally:
                cursor.close()

    def test_official_example_against_both_oracles(self):
        with connection_for_case(example_cases()[0]) as connection:
            result = query(connection, QUERY)
            self.assertEqual(as_multiset(result), as_multiset(OFFICIAL))
            self.assertEqual(as_multiset(result), as_multiset(oracle_union_anti_join(connection)))
            self.assertEqual(as_multiset(result), as_multiset(oracle_scalar_subqueries(connection)))

    def test_person_without_address_gets_nulls(self):
        rows = {'Person': [(1, 'Lone', 'Wolf')], 'Address': []}
        self.assertEqual(self.assert_solution_matches_oracle(rows), [('Wolf', 'Lone', None, None)])

    def test_person_with_two_addresses_yields_two_rows(self):
        rows = {
            'Person': [(1, 'Wang', 'Allen')],
            'Address': [(10, 1, 'New York City', 'New York'), (11, 1, 'Leetcode', 'California')],
        }
        result = self.assert_solution_matches_oracle(rows)
        self.assertFalse(at_most_one_address_per_person(rows))
        self.assertEqual(as_multiset(result), as_multiset([
            ('Allen', 'Wang', 'New York City', 'New York'),
            ('Allen', 'Wang', 'Leetcode', 'California'),
        ]))

    def test_address_without_person_is_not_reported(self):
        rows = {
            'Person': [(1, 'Wang', 'Allen')],
            'Address': [(10, 1, 'New York City', 'New York'), (11, 99, 'Nowhere', 'Nowhere')],
        }
        result = self.assert_solution_matches_oracle(rows)
        self.assertEqual(result, [('Allen', 'Wang', 'New York City', 'New York')])

    def test_empty_tables(self):
        self.assertEqual(self.assert_solution_matches_oracle({'Person': [], 'Address': []}), [])
        result = self.assert_solution_matches_oracle({'Person': [(1, 'Wang', 'Allen')], 'Address': []})
        self.assertEqual(result, [('Allen', 'Wang', None, None)])

    def test_matched_address_with_null_city_still_joins(self):
        rows = {'Person': [(1, 'Wang', 'Allen')], 'Address': [(10, 1, None, None)]}
        self.assertEqual(self.assert_solution_matches_oracle(rows), [('Allen', 'Wang', None, None)])

    def test_duplicate_persons_in_person_table(self):
        # personId is the primary key, so this cannot happen in valid data; the
        # join still has to behave, and the oracle is the arbiter.
        rows = {
            'Person': [(1, 'Wang', 'Allen'), (1, 'Wang', 'Allen')],
            'Address': [(10, 1, 'New York City', 'New York')],
        }
        result = self.assert_solution_matches_oracle(rows)
        self.assertEqual(len(result), 2)

    def test_multi_address_fan_out_at_scale(self):
        people = [(person, f'Last{person}', f'First{person}') for person in range(1, 201)]
        addresses = [
            (address_id, person_id, f'City{address_id}', f'State{address_id}')
            for address_id, person_id in enumerate(
                [person for person in range(1, 201) for _ in range(person % 3 + 1)], start=1
            )
        ]
        rows = {'Person': people, 'Address': addresses}
        result = self.assert_solution_matches_oracle(rows)
        self.assertFalse(at_most_one_address_per_person(rows))
        self.assertEqual(len(result), len(addresses))  # one row per address
        self.assertEqual(len({row[2] for row in result}), len({address[2] for address in addresses}))

    def test_randomised_databases(self):
        rng = random.Random(1750)
        for case in range(200):
            people = [(person, f'Last{person}', f'First{person}') for person in range(1, rng.randint(1, 8) + 1)]
            addresses = [
                (address_id, rng.randint(1, 10), f'City{address_id}', f'State{address_id}')
                for address_id in range(1, rng.randint(0, 8) + 1)
            ]
            with self.subTest(case=case):
                self.assert_solution_matches_oracle({'Person': people, 'Address': addresses})

    def test_constraint_sized(self):
        # The statement sets no row bound; 2000 persons and 3000 addresses is a
        # deliberately large case for both engines.
        rng = random.Random(1751)
        people = [(person, f'Last{person}', f'First{person}') for person in range(1, 2001)]
        addresses = [
            (address_id, rng.randint(1, 2000), f'City{address_id}', f'State{address_id}')
            for address_id in range(1, 3001)
        ]
        result = self.assert_solution_matches_oracle({'Person': people, 'Address': addresses})
        covered = {address[1] for address in addresses}
        persons_without_address = sum(1 for person in people if person[0] not in covered)
        self.assertEqual(len(result), len(addresses) + persons_without_address)
        self.assertEqual(sum(1 for row in result if row[2] is None), persons_without_address)

    def test_constraint_sized_every_person_has_an_address(self):
        rows = {
            'Person': [(index, f'Last{index}', f'First{index}') for index in range(1, 2001)],
            'Address': [(index, index, f'City{index}', f'State{index}') for index in range(1, 2001)],
        }
        with connection_for(rows) as connection:
            result = query(connection, QUERY)
            self.assertEqual(len(result), 2000)
            self.assertEqual(result[0], ('First1', 'Last1', 'City1', 'State1'))
            self.assertEqual(as_multiset(result), as_multiset(oracle_union_anti_join(connection)))

    def test_file_contains_one_statement(self):
        source = (SOLUTIONS / '175-combine-two-tables.sql').read_text(encoding='utf-8')
        body = '\n'.join(
            line for line in source.splitlines() if not line.strip().startswith('--')
        ).strip()
        self.assertTrue(body.upper().startswith('SELECT'))
        self.assertTrue(body.endswith(';'))
        self.assertEqual(body.count(';'), 1)


if __name__ == '__main__':
    unittest.main()
