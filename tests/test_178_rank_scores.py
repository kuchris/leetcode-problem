"""Tests for 178. Rank Scores.

Two oracles, neither of which uses a window function:

  - `oracle_correlated`: rank = 1 + the number of distinct strictly higher scores,
    as a correlated subquery per row;
  - `oracle_self_join`: the same count built with a self-join plus GROUP BY, i.e.
    an aggregate rather than a correlated lookup.

`RANK()` is checked explicitly as the wrong answer: on [5, 5, 3] it returns
1, 1, 3 (a hole) while DENSE_RANK -- and the statement -- require 1, 1, 2.

The official example is hand-transcribed from the statement, in the order the
statement fixes:

    | score | rank |        (4.00, 1) (4.00, 1) (3.85, 2)
    | 4.00  | 1    |        (3.65, 3) (3.65, 3) (3.50, 4)
    | 3.85  | 2    |
    | 3.65  | 3    |
    | 3.50  | 4    |

`score` is declared DECIMAL(3, 2), so every generated value stays within
[-9.99, 9.99] and carries two decimals.
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
SLUG = 'rank-scores'
SCHEMA = META[SLUG]['databaseSchema']
QUERY = load_sql('178-rank-scores.sql')

ROW_ORDER = {'Scores': ['id', 'score']}

OFFICIAL = [
    (4.00, 1), (4.00, 1), (3.85, 2),
    (3.65, 3), (3.65, 3), (3.50, 4),
]


def example_cases():
    raw = META[SLUG]['exampleTestcases'] or ''
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def rows_in_schema_order(table, row_order, table_rows):
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


def oracle_correlated(connection):
    """Rank = 1 + distinct higher scores, as a correlated subquery."""
    return query(connection, '''
        SELECT s.score,
               (SELECT COUNT(DISTINCT s2.score) FROM Scores AS s2 WHERE s2.score > s.score) + 1 AS rank
        FROM Scores AS s
        ORDER BY s.score DESC
    ''')


def oracle_self_join(connection):
    """Rank = 1 + distinct higher scores, via a self-join and GROUP BY."""
    return query(connection, '''
        SELECT s.score, COUNT(DISTINCT h.score) + 1 AS rank
        FROM Scores AS s
        LEFT JOIN Scores AS h ON h.score > s.score
        GROUP BY s.id, s.score
        ORDER BY s.score DESC
    ''')


def oracle_rank_function(connection):
    """The wrong function for this problem, kept to pin the difference."""
    return query(connection, '''
        SELECT score, RANK() OVER (ORDER BY score DESC) AS rank
        FROM Scores
        ORDER BY score DESC
    ''')


def dense_rank_reference(scores):
    """Closed form: 1 + number of distinct scores strictly greater."""
    return [(score, 1 + len({other for other in scores if other > score})) for score in scores]


class RankScoresTests(unittest.TestCase):
    def scores_rows(self, scores):
        return {'Scores': [(index + 1, score) for index, score in enumerate(scores)]}

    def assert_matches_oracles(self, scores):
        rows = self.scores_rows(scores)
        with connection_for(rows) as connection:
            result = query(connection, QUERY)
            self.assertEqual(result, oracle_correlated(connection), f'scores={scores}')
            self.assertEqual(result, oracle_self_join(connection), f'scores={scores}')
        return result

    def test_official_example(self):
        with connection_for_case(example_cases()[0]) as connection:
            self.assertEqual(query(connection, QUERY), OFFICIAL)

    def test_official_example_headers(self):
        with connection_for_case(example_cases()[0]) as connection:
            cursor = connection.execute(QUERY)
            try:
                self.assertEqual([description[0] for description in cursor.description], ['score', 'rank'])
            finally:
                cursor.close()

    def test_official_example_against_both_oracles(self):
        with connection_for_case(example_cases()[0]) as connection:
            result = query(connection, QUERY)
            self.assertEqual(result, OFFICIAL)
            self.assertEqual(result, oracle_correlated(connection))
            self.assertEqual(result, oracle_self_join(connection))

    def test_result_is_ordered_by_score_descending(self):
        # The statement fixes the order, so the ordered list is compared, not a
        # multiset.
        result = self.assert_matches_oracles([3.5, 3.65, 4.0, 3.85, 4.0, 3.65])
        scores = [score for score, _ in result]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result, OFFICIAL)

    def test_single_row(self):
        self.assertEqual(self.assert_matches_oracles([7.25]), [(7.25, 1)])

    def test_all_scores_equal(self):
        result = self.assert_matches_oracles([2.5] * 6)
        self.assertEqual(result, [(2.5, 1)] * 6)
        # With no higher score anywhere, RANK and DENSE_RANK agree.
        with connection_for(self.scores_rows([2.5] * 6)) as connection:
            self.assertEqual(oracle_rank_function(connection), [(2.5, 1)] * 6)

    def test_ties_do_not_leave_holes(self):
        # This is the whole trap: RANK() answers 1, 1, 3 here.
        result = self.assert_matches_oracles([5.0, 5.0, 3.0])
        self.assertEqual(result, [(5.0, 1), (5.0, 1), (3.0, 2)])
        with connection_for(self.scores_rows([5.0, 5.0, 3.0])) as connection:
            self.assertEqual(oracle_rank_function(connection), [(5.0, 1), (5.0, 1), (3.0, 3)])

    def test_several_tie_groups(self):
        scores = [5.0, 5.0, 5.0, 3.0, 3.0, 1.0]
        self.assertEqual(self.assert_matches_oracles(scores), dense_rank_reference(scores))
        self.assertEqual([rank for _, rank in self.assert_matches_oracles(scores)], [1, 1, 1, 2, 2, 3])

    def test_distinct_scores(self):
        scores = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(self.assert_matches_oracles(scores), [(4.0, 1), (3.0, 2), (2.0, 3), (1.0, 4)])

    def test_negative_and_zero_scores(self):
        scores = [-9.99, 0.0, 9.99, -0.01]
        self.assertEqual(self.assert_matches_oracles(scores), dense_rank_reference(sorted(scores, reverse=True)))

    def test_two_decimal_places_are_preserved(self):
        scores = [3.50, 3.65, 4.00, 3.85, 4.00, 3.65]
        result = self.assert_matches_oracles(scores)
        self.assertEqual(result, OFFICIAL)
        self.assertEqual([score for score, _ in result],
                         [4.00, 4.00, 3.85, 3.65, 3.65, 3.50])

    def test_every_row_appears_exactly_once(self):
        scores = [1.11, 1.11, 2.22, 3.33, 2.22, 4.44, 4.44, 0.0]
        result = self.assert_matches_oracles(scores)
        self.assertEqual(len(result), len(scores))
        self.assertEqual(sorted(score for score, _ in result), sorted(scores))

    def test_ranks_are_contiguous_from_one(self):
        scores = [1.0, 2.0, 2.0, 3.0, 5.0, 5.0, 5.0, 8.0]
        ranks = sorted({rank for _, rank in self.assert_matches_oracles(scores)})
        self.assertEqual(ranks, list(range(1, len(set(scores)) + 1)))

    def test_randomised_databases(self):
        rng = random.Random(1780)
        for case in range(300):
            size = rng.randint(1, 12)
            # DECIMAL(3, 2): two decimals inside [-9.99, 9.99].
            scores = [rng.randint(-999, 999) / 100 for _ in range(size)]
            with self.subTest(case=case, scores=scores):
                self.assertEqual(self.assert_matches_oracles(scores),
                                 dense_rank_reference(sorted(scores, reverse=True)))

    def test_randomised_heavy_ties(self):
        rng = random.Random(1781)
        for case in range(150):
            scores = [rng.choice([1.0, 2.0, 2.5, 3.0]) for _ in range(rng.randint(1, 30))]
            with self.subTest(case=case):
                self.assertEqual(self.assert_matches_oracles(scores),
                                 dense_rank_reference(sorted(scores, reverse=True)))

    def test_constraint_sized(self):
        # The statement sets no row bound; 2000 rows over 20 distinct scores is a
        # deliberately large, tie-heavy case.
        rng = random.Random(1782)
        scores = [rng.randint(-999, 999) / 100 for _ in range(2000)]
        result = self.assert_matches_oracles(scores)
        self.assertEqual(len(result), 2000)
        self.assertEqual(result, dense_rank_reference(sorted(scores, reverse=True)))
        self.assertEqual(max(rank for _, rank in result), len(set(scores)))

        all_equal = [1.23] * 2000
        self.assertEqual(self.assert_matches_oracles(all_equal), [(1.23, 1)] * 2000)

    def test_file_contains_one_statement_and_orders(self):
        source = (SOLUTIONS / '178-rank-scores.sql').read_text(encoding='utf-8')
        body = '\n'.join(
            line for line in source.splitlines() if not line.strip().startswith('--')
        ).strip()
        self.assertTrue(body.upper().startswith('SELECT'))
        self.assertTrue(body.endswith(';'))
        self.assertEqual(body.count(';'), 1)
        self.assertIn('ORDER BY', body.upper(), 'the statement fixes the output order')


if __name__ == '__main__':
    unittest.main()
