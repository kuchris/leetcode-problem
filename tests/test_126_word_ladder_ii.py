"""Tests for 126. Word Ladder II.

`oracle_paths` is built by hand instead of reusing the solution's search:

  - adjacency comes from comparing every pair of words directly (Hamming
    distance 1), never from wildcard buckets;
  - distances come from a plain queue BFS;
  - the shortest sequences are enumerated *forwards* from beginWord along edges
    that increase the distance by exactly one, not backwards from endWord along
    the parent links the solution records.

`hypercube_words` / `isolated_fillers` build the constraint-sized case: 32 cube
words over {a, b}^5 plus fillers that are provably isolated, so the answer is
every monotone flip order, and its size is the multinomial 5! / (1! ... 1!) = 120
-- a number obtained without any search at all.
"""

import collections
import itertools
import math
import random
import unittest

from _loader import load_solution

Solution = load_solution('126-word-ladder-ii.py').Solution


def differ_by_one(a: str, b: str) -> bool:
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def adjacency_by_pairs(words) -> dict:
    adjacency = {word: [] for word in words}
    ordered = sorted(words)
    for index, first in enumerate(ordered):
        for second in ordered[index + 1:]:
            if differ_by_one(first, second):
                adjacency[first].append(second)
                adjacency[second].append(first)
    return adjacency


def oracle_paths(begin: str, end: str, word_list) -> list:
    """All shortest sequences, via pairwise adjacency + BFS + forward DFS."""
    words = set(word_list) | {begin}
    if end not in words:
        return []

    adjacency = adjacency_by_pairs(words)
    distance = {begin: 0}
    queue = collections.deque([begin])
    while queue:
        word = queue.popleft()
        for neighbour in adjacency[word]:
            if neighbour not in distance:
                distance[neighbour] = distance[word] + 1
                queue.append(neighbour)

    if end not in distance:
        return []

    paths = []
    path = [begin]

    def walk(word: str) -> None:
        if word == end:
            paths.append(list(path))
            return
        for neighbour in adjacency[word]:
            if distance.get(neighbour) == distance[word] + 1:
                path.append(neighbour)
                walk(neighbour)
                path.pop()

    walk(begin)
    return sorted(paths)


def cube_words(length: int = 5) -> list:
    return [''.join(bits) for bits in itertools.product('ab', repeat=length)]


def isolated_fillers(count: int, length: int = 5) -> list:
    """Length-5 words at Hamming distance >= 2 from everything else we use.

    Positions 0 and 1 are 'z', so every filler differs from every cube word in
    two positions. Between fillers the trailing letter is a checksum, so two
    fillers that differ in exactly one digit still differ in the checksum.
    """
    assert length == 5
    fillers = []
    for first in range(25):
        for second in range(25):
            if len(fillers) == count:
                return fillers
            fillers.append('zz' + chr(97 + first) + chr(97 + second) + chr(97 + (first + second) % 25))
    return fillers


class WordLadderTwoTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findLadders

    def test_official_examples(self):
        self.assertEqual(
            self.solve('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']),
            [['hit', 'hot', 'dot', 'dog', 'cog'], ['hit', 'hot', 'lot', 'log', 'cog']],
        )
        self.assertEqual(self.solve('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log']), [])

    def test_end_word_missing_from_word_list(self):
        self.assertEqual(self.solve('a', 'c', ['b']), [])
        self.assertEqual(self.solve('hit', 'cog', []), [])

    def test_direct_neighbour(self):
        self.assertEqual(self.solve('a', 'c', ['c']), [['a', 'c']])
        self.assertEqual(self.solve('hit', 'hot', ['hot']), [['hit', 'hot']])

    def test_begin_word_may_appear_in_word_list(self):
        self.assertEqual(
            self.solve('hit', 'cog', ['hit', 'hot', 'dot', 'dog', 'cog']),
            [['hit', 'hot', 'dot', 'dog', 'cog']],
        )
        self.assertEqual(self.solve('aa', 'ba', ['aa', 'ba']), [['aa', 'ba']])
        self.assertEqual(self.solve('aa', 'bb', ['aa', 'bb']), [])  # two positions differ
        for begin, end, word_list in (('aa', 'ba', ['aa', 'ba']), ('aa', 'bb', ['aa', 'bb'])):
            with self.subTest(begin=begin, end=end):
                self.assertEqual(self.solve(begin, end, word_list), oracle_paths(begin, end, word_list))
        self.assertEqual(
            self.solve('aa', 'bb', ['aa', 'ab', 'bb']),
            oracle_paths('aa', 'bb', ['aa', 'ab', 'bb']),
        )

    def test_end_word_present_but_unreachable(self):
        self.assertEqual(self.solve('aa', 'bb', ['bb', 'cc']), [])
        self.assertEqual(self.solve('aa', 'bb', ['bb', 'cc', 'dd']), [])

    def test_single_letter_words(self):
        # With words of length 1 any two different words differ in their only
        # position, so endWord is always a direct neighbour of beginWord.
        self.assertEqual(self.solve('a', 'd', ['b', 'c', 'd']), [['a', 'd']])
        self.assertEqual(self.solve('a', 'c', ['a', 'b', 'c']), [['a', 'c']])
        self.assertEqual(self.solve('a', 'd', ['b', 'c']), [])
        for word_list in (['b', 'c', 'd'], ['a', 'b', 'c'], ['d'], ['z']):
            with self.subTest(word_list=word_list):
                self.assertEqual(self.solve('a', 'd', word_list), oracle_paths('a', 'd', word_list))

    def test_hypercube_of_size_three(self):
        # Every monotone flip order is a shortest sequence: 3! = 6 paths of four
        # words, which the oracle must reproduce exactly.
        cube = cube_words(3)
        word_list = [word for word in cube if word != 'aaa']
        result = self.solve('aaa', 'bbb', word_list)
        self.assertEqual(len(result), math.factorial(3))
        self.assertEqual(result, oracle_paths('aaa', 'bbb', word_list))
        self.assertTrue(all(len(path) == 4 for path in result))

    def test_exhaustive_small_universe(self):
        universe = ['aa', 'ab', 'ba', 'bb', 'ac', 'cc']
        begins = ['aa', 'ac', 'zz']
        for size in range(len(universe) + 1):
            for subset in itertools.combinations(universe, size):
                for begin in begins:
                    for end in universe + ['zz']:
                        if begin == end:
                            continue
                        with self.subTest(begin=begin, end=end, words=list(subset)):
                            self.assertEqual(self.solve(begin, end, list(subset)), oracle_paths(begin, end, list(subset)))

    def test_randomised_small_graphs(self):
        rng = random.Random(1260)
        for _ in range(400):
            length = rng.randint(1, 3)
            universe = [''.join(chars) for chars in itertools.product('abc', repeat=length)]
            begin = rng.choice(universe)
            end = rng.choice([w for w in universe if w != begin])
            candidates = [w for w in universe if w != begin]
            word_list = rng.sample(candidates, rng.randint(0, len(candidates)))
            with self.subTest(begin=begin, end=end, words=word_list):
                self.assertEqual(self.solve(begin, end, word_list), oracle_paths(begin, end, word_list))

    def test_randomised_begin_word_inside_list(self):
        rng = random.Random(1261)
        for _ in range(200):
            length = rng.randint(2, 3)
            universe = [''.join(chars) for chars in itertools.product('ab', repeat=length)]
            begin = rng.choice(universe)
            end = rng.choice([w for w in universe if w != begin])
            extra = rng.sample([w for w in universe if w not in (begin, end)], rng.randint(0, len(universe) - 2))
            word_list = [begin] + extra + [end]
            with self.subTest(begin=begin, end=end, words=word_list):
                self.assertEqual(self.solve(begin, end, word_list), oracle_paths(begin, end, word_list))

    def test_randomised_larger_graphs(self):
        rng = random.Random(1262)
        for _ in range(40):
            universe = [''.join(chars) for chars in itertools.product('abcd', repeat=4)]
            begin = rng.choice(universe)
            end = rng.choice([w for w in universe if w != begin])
            word_list = rng.sample([w for w in universe if w != begin], 30)
            if end not in word_list:
                word_list.append(end)
            with self.subTest(begin=begin, end=end):
                self.assertEqual(self.solve(begin, end, word_list), oracle_paths(begin, end, word_list))

    def test_constraint_sized_hypercube_fixture_is_sound(self):
        # The 500-word fixture below relies on the fillers being isolated; check
        # that claim directly instead of trusting it.
        cube = cube_words(5)
        fillers = isolated_fillers(500 - len(cube))
        self.assertEqual(len(cube) + len(fillers), 500)
        self.assertEqual(len(set(cube + fillers)), 500)
        for filler in fillers:
            self.assertNotIn(filler, cube)
            for word in cube:
                self.assertFalse(differ_by_one(filler, word))
        for index, filler in enumerate(fillers):
            for other in fillers[index + 1:]:
                self.assertFalse(differ_by_one(filler, other))

    def test_constraint_sized_hypercube(self):
        # 500 words, word length 5, and every monotone flip order is a shortest
        # sequence: 5! = 120 sequences of 6 words each (720 words, well under the
        # 10^5 bound on the total answer).
        cube = cube_words(5)
        word_list = cube + isolated_fillers(500 - len(cube))
        self.assertEqual(len(word_list), 500)

        result = self.solve('aaaaa', 'bbbbb', word_list)

        self.assertEqual(len(result), math.factorial(5))
        self.assertEqual(sorted(result), oracle_paths('aaaaa', 'bbbbb', word_list))
        allowed = set(word_list)
        for path in result:
            with self.subTest(path=path):
                self.assertEqual(path[0], 'aaaaa')
                self.assertEqual(path[-1], 'bbbbb')
                self.assertEqual(len(path), 6)
                self.assertTrue(set(path) <= allowed)
                self.assertTrue(all(differ_by_one(a, b) for a, b in zip(path, path[1:])))
                self.assertEqual(len(set(path)), 6)
        self.assertEqual(len({tuple(path) for path in result}), 120)

    def test_constraint_sized_no_path(self):
        cube = cube_words(5)
        fillers = isolated_fillers(500 - len(cube) - 1)
        # endWord is in the list but isolated, so no sequence exists.
        unreachable = isolated_fillers(500 - len(cube))[-1]
        word_list = cube + fillers + [unreachable]
        self.assertEqual(len(word_list), 500)
        self.assertNotIn(unreachable, cube)
        self.assertEqual(self.solve('aaaaa', unreachable, word_list), [])

    def test_constraint_sized_long_chain(self):
        # One chain of 126 words, built by bumping a single position at a time:
        # consecutive words stay at distance 1 and the words are distinct because
        # each step is lexicographically larger than the previous one. A position
        # is bumped at most 25 times (a -> z), so 5 positions allow 125 steps.
        length = 5
        word = ['a'] * length
        chain = [''.join(word)]
        for step in range(125):
            position = step % length
            word[position] = chr(ord(word[position]) + 1)
            chain.append(''.join(word))
        self.assertEqual(len(chain), 126)
        self.assertEqual(len(set(chain)), 126)
        self.assertTrue(all(differ_by_one(a, b) for a, b in zip(chain, chain[1:])))

        word_list = chain[1:]
        result = self.solve(chain[0], chain[-1], word_list)
        self.assertEqual(result, oracle_paths(chain[0], chain[-1], word_list))
        self.assertIn(chain, result)


if __name__ == '__main__':
    unittest.main()
