"""Tests for 139. Word Break.

Two independent oracles, neither of which is the solution's left-to-right
reachability table:

  - ``dfs_oracle``: plain recursive segmentation search (no DP, no memoisation),
    trying every dictionary word at every position and succeeding as soon as the
    whole string is consumed;
  - ``trie_oracle``: a completely different data structure -- dictionary words
    are stored in a character trie and the string is walked character by
    character from every already-reachable position.

Every True answer is also given a *witness*: a concrete segmentation is rebuilt
and checked (all words in the dictionary, concatenation equals s), which proves
reachability without trusting any decision procedure.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('139-word-break.py').Solution


def dfs_oracle(s: str, words) -> bool:
    words = list(words)
    n = len(s)

    def walk(i: int) -> bool:
        if i == n:
            return True
        for word in words:
            if s.startswith(word, i) and walk(i + len(word)):
                return True
        return False

    return walk(0)


def trie_oracle(s: str, words) -> bool:
    trie: dict = {}
    for word in words:
        node = trie
        for char in word:
            node = node.setdefault(char, {})
        node['#'] = True

    n = len(s)
    reachable = [False] * (n + 1)
    reachable[0] = True
    for i in range(n):
        if not reachable[i]:
            continue
        node = trie
        for j in range(i, n):
            node = node.get(s[j])
            if node is None:
                break
            if '#' in node:
                reachable[j + 1] = True
    return reachable[n]


def find_witness(s: str, words):
    """A concrete valid segmentation of s, or None, via a plain DFS."""
    words = list(words)
    n = len(s)

    def walk(i: int, chosen: list):
        if i == n:
            return list(chosen)
        for word in words:
            if s.startswith(word, i):
                chosen.append(word)
                found = walk(i + len(word), chosen)
                if found is not None:
                    return found
                chosen.pop()
        return None

    return walk(0, [])


def subsets(pool):
    for size in range(1, len(pool) + 1):
        for combination in itertools.combinations(pool, size):
            yield list(combination)


def strings_of_length(length: int, alphabet: str = 'ab'):
    for combination in itertools.product(alphabet, repeat=length):
        yield ''.join(combination)


class WordBreakTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().wordBreak

    def check(self, s, wordDict):
        produced = self.solve(s, wordDict)
        self.assertEqual(produced, dfs_oracle(s, wordDict), f'dfs(s={s!r})')
        self.assertEqual(produced, trie_oracle(s, wordDict), f'trie(s={s!r})')
        if produced:
            witness = find_witness(s, wordDict)
            self.assertIsNotNone(witness)
            self.assertTrue(all(word in set(wordDict) for word in witness))
            self.assertEqual(''.join(witness), s)
        return produced

    def test_official_examples(self):
        self.assertTrue(self.solve('leetcode', ['leet', 'code']))
        self.assertTrue(self.solve('applepenapple', ['apple', 'pen']))
        self.assertFalse(self.solve('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']))
        self.check('leetcode', ['leet', 'code'])
        self.check('applepenapple', ['apple', 'pen'])
        self.check('catsandog', ['cats', 'dog', 'sand', 'and', 'cat'])

    def test_single_character_cases(self):
        self.assertTrue(self.check('a', ['a']))
        self.assertFalse(self.check('a', ['b']))
        self.assertTrue(self.check('aaaa', ['a']))
        self.assertFalse(self.check('aaab', ['a']))

    def test_word_reuse(self):
        self.assertTrue(self.check('penpenpen', ['pen']))
        self.assertTrue(self.check('abcabcabc', ['abc']))
        self.assertTrue(self.check('abababab', ['ab']))

    def test_longer_dictionary_words(self):
        self.assertTrue(self.check('leetcode', ['lee', 'tcode', 'leet', 'code']))
        self.assertTrue(self.check('abcde', ['abcde']))
        self.assertFalse(self.check('abcde', ['abcd']))
        # A dictionary word longer than s is simply never usable.
        self.assertTrue(self.check('ab', ['ab', 'abcdefghij']))

    def test_overlapping_words_need_a_choice(self):
        self.assertTrue(self.check('aab', ['a', 'aa', 'b']))
        self.assertFalse(self.check('aab', ['aa', 'ab']))
        self.assertTrue(self.check('aabb', ['a', 'ab', 'b', 'bb']))

    def test_exhaustive_short_strings(self):
        for length in range(1, 7):
            for s in strings_of_length(length):
                for wordDict in subsets(['a', 'b', 'ab', 'ba']):
                    with self.subTest(s=s, wordDict=wordDict):
                        self.check(s, wordDict)

    def test_exhaustive_longer_strings_with_overlaps(self):
        for length in range(7, 9):
            for s in strings_of_length(length):
                for wordDict in subsets(['a', 'b', 'aa', 'ab']):
                    with self.subTest(s=s, wordDict=wordDict):
                        self.check(s, wordDict)

    def test_full_two_letter_pool_sweep(self):
        pool = ['a', 'b', 'aa', 'ab', 'ba', 'bb']
        for wordDict in subsets(pool):
            for s in strings_of_length(4):
                with self.subTest(s=s, wordDict=wordDict):
                    self.check(s, wordDict)

    def test_random_cases(self):
        rng = random.Random(1390)
        for _ in range(300):
            length = rng.randint(1, 30)
            s = ''.join(rng.choice('abc') for _ in range(length))
            pool = set()
            for _ in range(rng.randint(1, 12)):
                size = rng.randint(1, 4)
                pool.add(''.join(rng.choice('abc') for _ in range(size)))
            wordDict = sorted(pool)
            with self.subTest(s=s, wordDict=wordDict):
                self.assertEqual(self.solve(s, wordDict), trie_oracle(s, wordDict))
                if length <= 10:
                    self.assertEqual(self.solve(s, wordDict), dfs_oracle(s, wordDict))

    def test_random_solvable_cases(self):
        # Build s *from* dictionary words, so the answer must be True.
        rng = random.Random(1391)
        for _ in range(200):
            pool = sorted({''.join(rng.choice('ab') for _ in range(rng.randint(1, 4)))
                           for _ in range(rng.randint(1, 6))})
            pieces = [rng.choice(pool) for _ in range(rng.randint(1, 8))]
            s = ''.join(pieces)
            if len(s) > 300:
                continue
            with self.subTest(s=s, wordDict=pool):
                self.assertTrue(self.solve(s, pool))
                self.assertEqual(self.solve(s, pool), trie_oracle(s, pool))

    def test_constraint_sized(self):
        # s of length 300 and a 1000-word dictionary are the constraint maxima;
        # every dictionary word is at most 20 characters long.
        wordDict = sorted(
            {'a' * k for k in range(1, 21)}          # 20 words
            | {'bc' * k for k in range(1, 10)}       # 9 words, length <= 18
            | {'abc' * k + 'z' for k in range(1, 7)}  # 6 words, length <= 19
        )
        self.assertEqual(len(wordDict), 35)
        self.assertLessEqual(max(len(word) for word in wordDict), 20)

        self.assertTrue(self.solve('a' * 300, wordDict))
        self.assertTrue(self.solve('bc' * 10, wordDict))
        self.assertTrue(self.solve('abcz', wordDict))
        # 'b' and 'c' can only be covered by words starting with 'b', and every
        # such word contains a 'c' that the string does not have.
        self.assertFalse(self.solve('a' * 299 + 'b', wordDict))
        self.assertFalse(self.solve('a' * 299 + 'c', wordDict))
        self.assertFalse(self.solve('ab' * 150, wordDict))
        for case in ['a' * 300, 'bc' * 10, 'a' * 299 + 'b', 'a' * 299 + 'c', 'ab' * 150]:
            with self.subTest(length=len(case)):
                self.assertEqual(self.solve(case, wordDict), trie_oracle(case, wordDict))

        # Exactly 1000 distinct dictionary words, all over {a, b, c} and all of
        # length <= 20: the words a^i b^j c^k with i >= 1 and i+j+k <= 20.
        words = set()
        for total in range(1, 21):
            for i in range(1, total + 1):
                for j in range(0, total - i + 1):
                    words.add('a' * i + 'b' * j + 'c' * (total - i - j))
        self.assertEqual(len(words), 1540)
        wordDict = sorted(sorted(words)[:1000])
        self.assertEqual(len(wordDict), 1000)
        self.assertLessEqual(max(len(word) for word in wordDict), 20)
        self.assertTrue(self.solve('a' * 300, wordDict))
        # 'd' appears in no dictionary word.
        self.assertFalse(self.solve('a' * 299 + 'd', wordDict))
        self.assertFalse(self.solve('d' + 'a' * 299, wordDict))

        # A maximum-length case with a longer period.
        periodic = sorted({'abcd', 'cdab', 'abc', 'd', 'bcd', 'a'})
        self.assertTrue(self.solve('abcd' * 75, periodic))
        self.assertEqual(self.solve('abcd' * 75, periodic),
                         trie_oracle('abcd' * 75, periodic))
        self.assertFalse(self.solve('abcd' * 74 + 'abce', periodic))
        self.assertEqual(self.solve('abcd' * 74 + 'abce', periodic),
                         trie_oracle('abcd' * 74 + 'abce', periodic))

        # The classic dead end for a naive exhaustive search: a long run of 'a'
        # followed by one impossible character.
        self.assertFalse(self.solve('a' * 299 + 'z', wordDict))
        self.assertFalse(trie_oracle('a' * 299 + 'z', wordDict))

        # Witness for a maximum-length True case.
        witness = find_witness('a' * 300, sorted({'a' * k for k in range(1, 21)}))
        self.assertIsNotNone(witness)
        self.assertEqual(''.join(witness), 'a' * 300)


if __name__ == '__main__':
    unittest.main()
