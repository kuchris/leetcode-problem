"""Tests for 127. Word Ladder.

Two independent oracles, neither of which uses wildcard buckets:

  - `floyd_warshall_length` builds the full pairwise adjacency matrix and then
    reads the answer off an all-pairs shortest-path DP -- there is no search at
    all;
  - `bfs_length` builds the same adjacency by direct pairwise comparison and runs
    a plain queue BFS over it.

`big_fixture` builds the constraint-sized case: all 1024 words of {a, b}^10 (a
10-dimensional hypercube, where the graph distance is the Hamming distance) plus
3976 fillers that are provably isolated, so the answer is the Hamming distance
between the two words plus one -- a closed form that involves no search.
"""

import collections
import itertools
import random
import string
import unittest

from _loader import load_solution

Solution = load_solution('127-word-ladder.py').Solution


def differ_by_one(a: str, b: str) -> bool:
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def adjacency_by_pairs(words) -> dict:
    adjacency = {word: [] for word in words}
    ordered = sorted(words)
    for index, first in enumerate(ordered):
        for second in ordered[index + 1:]:
            if differ_by_one(first, second):
                adjacency[first].append(second)
                adjacency[second].append(first)
    return adjacency


def bfs_length(begin: str, end: str, word_list) -> int:
    words = set(word_list) | {begin}
    if end not in words:
        return 0

    adjacency = adjacency_by_pairs(words)
    distance = {begin: 0}
    queue = collections.deque([begin])
    while queue:
        word = queue.popleft()
        for neighbour in adjacency[word]:
            if neighbour not in distance:
                distance[neighbour] = distance[word] + 1
                queue.append(neighbour)

    return 0 if end not in distance else distance[end] + 1


def floyd_warshall_length(begin: str, end: str, word_list) -> int:
    nodes = sorted(set(word_list) | {begin})
    if end not in nodes:
        return 0

    count = len(nodes)
    index = {word: position for position, word in enumerate(nodes)}
    infinity = float('inf')
    distance = [[infinity] * count for _ in range(count)]
    for position in range(count):
        distance[position][position] = 0
    for first in range(count):
        for second in range(first + 1, count):
            if differ_by_one(nodes[first], nodes[second]):
                distance[first][second] = distance[second][first] = 1

    for middle in range(count):
        middle_row = distance[middle]
        for first in range(count):
            through = distance[first][middle]
            if through == infinity:
                continue
            first_row = distance[first]
            for second in range(count):
                if through + middle_row[second] < first_row[second]:
                    first_row[second] = through + middle_row[second]

    best = distance[index[begin]][index[end]]
    return 0 if best == infinity else int(best) + 1


def cube_words(length: int = 10) -> list:
    return [''.join(bits) for bits in itertools.product('ab', repeat=length)]


def isolated_fillers(count: int, length: int = 10) -> list:
    """Length-10 words at Hamming distance >= 2 from the cube and from each other.

    Positions 0 and 1 are 'c', so a filler differs from every {a, b} word in two
    positions. The remaining eight letters are seven base-25 digits of the filler
    index plus a checksum letter, so two different fillers either differ in two
    digits or differ in one digit and in the checksum -- never in exactly one
    position. Isolated words can never shorten a path.
    """
    assert length == 10
    fillers = []
    for number in range(count):
        value = number
        digits = []
        for _ in range(7):
            digits.append(value % 25)
            value //= 25
        assert value == 0
        checksum = sum(digits) % 25
        fillers.append('cc' + ''.join(chr(97 + digit) for digit in digits) + chr(97 + checksum))
    return fillers


def big_fixture() -> list:
    return cube_words(10) + isolated_fillers(5000 - 1024)


class WordLadderTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().ladderLength

    def test_official_examples(self):
        self.assertEqual(self.solve('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']), 5)
        self.assertEqual(self.solve('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log']), 0)

    def test_end_word_missing_from_word_list(self):
        self.assertEqual(self.solve('a', 'c', ['b']), 0)
        self.assertEqual(self.solve('hit', 'cog', []), 0)

    def test_direct_neighbour(self):
        self.assertEqual(self.solve('a', 'c', ['c']), 2)
        self.assertEqual(self.solve('hit', 'hot', ['hot']), 2)
        self.assertEqual(self.solve('aa', 'ba', ['ba']), 2)
        self.assertEqual(self.solve('aa', 'bb', ['bb']), 0)  # two positions differ

    def test_begin_word_may_appear_in_word_list(self):
        self.assertEqual(self.solve('hit', 'cog', ['hit', 'hot', 'dot', 'dog', 'cog']), 5)
        self.assertEqual(self.solve('aa', 'ab', ['aa', 'ab']), 2)

    def test_begin_word_never_blocks_its_own_reuse(self):
        # beginWord is in the list but also a legal intermediate.
        self.assertEqual(self.solve('aa', 'bb', ['aa', 'ab', 'bb']), 3)
        self.assertEqual(self.solve('aa', 'bb', ['ab', 'aa', 'bb']), 3)

    def test_end_word_present_but_unreachable(self):
        self.assertEqual(self.solve('aa', 'bb', ['bb', 'cc']), 0)
        self.assertEqual(self.solve('aa', 'cc', ['bb', 'cc', 'dd']), 0)

    def test_single_letter_words(self):
        # Length 1: every pair of different words is adjacent.
        self.assertEqual(self.solve('a', 'd', ['b', 'c', 'd']), 2)
        self.assertEqual(self.solve('a', 'd', ['b', 'c']), 0)

    def test_exhaustive_small_universe(self):
        universe = ['aa', 'ab', 'ba', 'bb', 'ac', 'cc']
        for size in range(len(universe) + 1):
            for subset in itertools.combinations(universe, size):
                for begin in ('aa', 'ac', 'zz'):
                    for end in universe + ['zz']:
                        if begin == end:
                            continue
                        with self.subTest(begin=begin, end=end, words=list(subset)):
                            self.assertEqual(
                                self.solve(begin, end, list(subset)),
                                floyd_warshall_length(begin, end, list(subset)),
                            )

    def test_exhaustive_length_three_universe(self):
        universe = [''.join(chars) for chars in itertools.product('ab', repeat=3)]
        rng = random.Random(1270)
        for begin in ('aaa', 'bbb', 'aab'):
            for end in universe:
                if begin == end:
                    continue
                for _ in range(6):
                    subset = rng.sample([w for w in universe if w != end], rng.randint(0, 6)) + [end]
                    with self.subTest(begin=begin, end=end, words=subset):
                        self.assertEqual(
                            self.solve(begin, end, subset),
                            floyd_warshall_length(begin, end, subset),
                        )

    def test_randomised_against_both_oracles(self):
        rng = random.Random(1271)
        for _ in range(400):
            length = rng.randint(1, 4)
            alphabet = 'abc'[: rng.randint(2, 3)]
            universe = [''.join(chars) for chars in itertools.product(alphabet, repeat=length)]
            begin = rng.choice(universe)
            end = rng.choice([w for w in universe if w != begin])
            candidates = [w for w in universe if w != begin]
            word_list = rng.sample(candidates, rng.randint(0, len(candidates)))
            with self.subTest(begin=begin, end=end, words=word_list):
                expected = floyd_warshall_length(begin, end, word_list)
                self.assertEqual(self.solve(begin, end, word_list), expected)
                self.assertEqual(expected, bfs_length(begin, end, word_list))

    def test_randomised_medium_graphs(self):
        rng = random.Random(1272)
        universe = [''.join(chars) for chars in itertools.product('abcd', repeat=5)]
        for _ in range(30):
            begin = rng.choice(universe)
            end = rng.choice([w for w in universe if w != begin])
            word_list = rng.sample([w for w in universe if w != begin], 200)
            if end not in word_list:
                word_list.append(end)
            with self.subTest(begin=begin, end=end):
                self.assertEqual(self.solve(begin, end, word_list), bfs_length(begin, end, word_list))

    def test_constraint_sized_fixture_is_sound(self):
        words = big_fixture()
        self.assertEqual(len(words), 5000)
        self.assertEqual(len(set(words)), 5000)
        for word in words:
            self.assertEqual(len(word), 10)
            self.assertTrue(set(word) <= set(string.ascii_lowercase))

        cube = words[:1024]
        fillers = words[1024:]
        self.assertTrue(all(set(word) <= {'a', 'b'} for word in cube))
        # Every filler starts 'cc', so no cube word can be one letter away.
        self.assertTrue(all(filler[:2] == 'cc' for filler in fillers))
        for filler in rng_sample(fillers, 60):
            for word in rng_sample(cube, 60):
                self.assertGreaterEqual(hamming(filler, word), 2)
        for filler in rng_sample(fillers, 60):
            for other in rng_sample(fillers, 60):
                if filler != other:
                    self.assertGreaterEqual(hamming(filler, other), 2)

    def test_constraint_sized_hypercube(self):
        # Graph distance in {a, b}^10 is the Hamming distance, so the answer is
        # hamming + 1 = 11 words. Nothing else can shorten it: every filler is at
        # distance >= 2 from both endpoints and from every cube word.
        words = big_fixture()
        self.assertEqual(hamming('a' * 10, 'b' * 10), 10)
        self.assertEqual(self.solve('a' * 10, 'b' * 10, words), 11)

    def test_constraint_sized_hypercube_with_begin_outside_the_list(self):
        # beginWord is not in wordList but is one flip away from the cube.
        begin = 'c' + 'a' * 9
        words = big_fixture()
        self.assertNotIn(begin, words)
        self.assertEqual(hamming(begin, 'b' * 10), 10)
        self.assertEqual(self.solve(begin, 'b' * 10, words), 11)

    def test_constraint_sized_no_path(self):
        words = big_fixture()
        unreachable = words[-1]  # an isolated filler
        self.assertTrue(unreachable.startswith('cc'))
        self.assertEqual(self.solve('a' * 10, unreachable, words), 0)

    def test_constraint_sized_all_fillers(self):
        # 5000 mutually isolated words: nothing is reachable, not even one step.
        words = isolated_fillers(5000)
        self.assertEqual(len(set(words)), 5000)
        self.assertEqual(self.solve(words[0], words[1], words), 0)

    def test_constraint_sized_long_chain(self):
        # 251 words in one chain, built by bumping a single position at a time:
        # consecutive words stay at distance 1 and the words are distinct because
        # each step is lexicographically larger. 10 positions allow 250 steps.
        length = 10
        word = ['a'] * length
        chain = [''.join(word)]
        for step in range(250):
            position = step % length
            word[position] = chr(ord(word[position]) + 1)
            chain.append(''.join(word))
        self.assertEqual(len(chain), 251)
        self.assertEqual(len(set(chain)), 251)
        self.assertTrue(all(differ_by_one(a, b) for a, b in zip(chain, chain[1:])))

        word_list = chain[1:]
        expected = bfs_length(chain[0], chain[-1], word_list)
        self.assertEqual(self.solve(chain[0], chain[-1], word_list), expected)
        self.assertLessEqual(expected, 251)


def rng_sample(values, count):
    """Deterministic sample of ``values`` (list) of at most ``count`` items."""
    if len(values) <= count:
        return list(values)
    step = len(values) // count
    return values[::step][:count]


if __name__ == '__main__':
    unittest.main()
