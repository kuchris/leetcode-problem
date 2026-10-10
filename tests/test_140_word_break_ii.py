"""Tests for 140. Word Break II.

The primary oracle *enumerates* segmentations instead of deciding anything:
``enumeration_oracle`` recurses over the string, appending every dictionary word
that matches at the current position, and records each completed sentence. It has
no memo, no table and no reachability pruning, so it shares no mechanism with the
solution's memoised suffix enumeration.

A second, structurally different oracle confirms it on small inputs:
``cuts_oracle`` ignores words as the driver and instead enumerates every subset
of cut positions of s with itertools, keeping the subsets whose pieces are all
dictionary words.

Results are order-insensitive, so both sides are normalised by sorting, and every
returned sentence is additionally validated (words in the dictionary, joined text
equals s, no duplicates).
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('140-word-break-ii.py').Solution


def enumeration_oracle(s: str, wordDict) -> list[str]:
    words = list(wordDict)
    n = len(s)
    sentences: list[str] = []

    def walk(i: int, chosen: list):
        if i == n:
            sentences.append(' '.join(chosen))
            return
        for word in words:
            if s.startswith(word, i):
                chosen.append(word)
                walk(i + len(word), chosen)
                chosen.pop()

    walk(0, [])
    return sentences


def cuts_oracle(s: str, wordDict) -> list[str]:
    words = set(wordDict)
    n = len(s)
    sentences = []
    for size in range(n):
        for cuts in itertools.combinations(range(1, n), size):
            boundaries = (0, *cuts, n)
            pieces = [s[boundaries[k]:boundaries[k + 1]] for k in range(len(boundaries) - 1)]
            if all(piece in words for piece in pieces):
                sentences.append(' '.join(pieces))
    return sentences


def subsets(pool):
    for size in range(1, len(pool) + 1):
        for combination in itertools.combinations(pool, size):
            yield list(combination)


def strings_of_length(length: int, alphabet: str = 'ab'):
    for combination in itertools.product(alphabet, repeat=length):
        yield ''.join(combination)


class WordBreakIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().wordBreak

    def normalise(self, sentences):
        return sorted(sentences)

    def validate(self, s, wordDict, produced):
        words = set(wordDict)
        self.assertEqual(len(produced), len(set(produced)), 'duplicate sentences')
        for sentence in produced:
            pieces = sentence.split(' ')
            self.assertTrue(all(piece in words for piece in pieces),
                            f'not a dictionary segmentation: {sentence!r}')
            self.assertEqual(' '.join(pieces), sentence)
            self.assertEqual(''.join(pieces), s)
        self.assertEqual(self.normalise(produced), self.normalise(enumeration_oracle(s, wordDict)))
        return produced

    def check(self, s, wordDict, with_cuts=True):
        produced = self.solve(s, wordDict)
        self.validate(s, wordDict, produced)
        if with_cuts and len(s) <= 8:
            self.assertEqual(self.normalise(produced), self.normalise(cuts_oracle(s, wordDict)))
        return produced

    def test_official_examples(self):
        self.assertEqual(
            self.normalise(self.solve('catsanddog', ['cat', 'cats', 'and', 'sand', 'dog'])),
            self.normalise(['cats and dog', 'cat sand dog']),
        )
        self.assertEqual(
            self.normalise(self.solve('pineapplepenapple',
                                      ['apple', 'pen', 'applepen', 'pine', 'pineapple'])),
            self.normalise(['pine apple pen apple', 'pineapple pen apple',
                            'pine applepen apple']),
        )
        self.assertEqual(self.solve('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']), [])
        self.check('catsanddog', ['cat', 'cats', 'and', 'sand', 'dog'])
        self.check('pineapplepenapple',
                   ['apple', 'pen', 'applepen', 'pine', 'pineapple'])
        self.check('catsandog', ['cats', 'dog', 'sand', 'and', 'cat'])

    def test_single_characters(self):
        self.assertEqual(self.check('a', ['a']), ['a'])
        self.assertEqual(self.check('a', ['b']), [])
        self.assertEqual(self.check('a', ['a', 'b']), ['a'])

    def test_whole_string_is_a_word(self):
        self.assertEqual(self.check('abc', ['abc']), ['abc'])
        self.assertEqual(sorted(self.check('abc', ['abc', 'a', 'bc'])), ['a bc', 'abc'])

    def test_word_reuse(self):
        self.assertEqual(self.normalise(self.check('penpen', ['pen'])), ['pen pen'])
        self.assertEqual(self.normalise(self.solve('aaaa', ['a', 'aa'])),
                         self.normalise(['a a a a', 'a a aa', 'a aa a', 'aa a a', 'aa aa']))

    def test_no_segmentation(self):
        self.assertEqual(self.check('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']), [])
        self.assertEqual(self.check('a', ['aa']), [])
        self.assertEqual(self.check('abcde', ['ab', 'bc', 'cd']), [])

    def test_exhaustive_short_strings(self):
        for length in range(1, 7):
            for s in strings_of_length(length):
                for wordDict in subsets(['a', 'b', 'ab', 'ba']):
                    with self.subTest(s=s, wordDict=wordDict):
                        self.check(s, wordDict)

    def test_exhaustive_longer_strings(self):
        for length in range(7, 9):
            for s in strings_of_length(length):
                for wordDict in subsets(['a', 'ab', 'aa']):
                    with self.subTest(s=s, wordDict=wordDict):
                        self.check(s, wordDict, with_cuts=(length <= 8))

    def test_random_cases(self):
        rng = random.Random(1400)
        for _ in range(300):
            length = rng.randint(1, 12)
            s = ''.join(rng.choice('abc') for _ in range(length))
            pool = {''.join(rng.choice('abc') for _ in range(rng.randint(1, 4)))
                    for _ in range(rng.randint(1, 8))}
            wordDict = sorted(pool)
            with self.subTest(s=s, wordDict=wordDict):
                self.validate(s, wordDict, self.solve(s, wordDict))

    def test_random_solvable_cases(self):
        rng = random.Random(1401)
        for _ in range(200):
            pool = sorted({''.join(rng.choice('ab') for _ in range(rng.randint(1, 3)))
                           for _ in range(rng.randint(1, 5))})
            s = ''.join(rng.choice(pool) for _ in range(rng.randint(1, 5)))
            if len(s) > 20:
                continue
            with self.subTest(s=s, wordDict=pool):
                produced = self.check(s, pool)
                self.assertTrue(produced)  # true by construction
                self.assertEqual(self.normalise(produced),
                                 self.normalise(enumeration_oracle(s, pool)))

    def test_constraint_sized(self):
        # s.length <= 20 is the constraint maximum, and the statement guarantees
        # the total answer length stays within 10^5 -- each case below is checked
        # against that budget as well.
        cases = [
            ('a' * 20, ['aa', 'aaa']),
            ('a' * 20, ['aaaaa', 'aaa']),
            ('a' * 16, ['a', 'aa']),
            ('catsanddogcatsanddog',
             ['cat', 'cats', 'and', 'sand', 'dog', 'catsanddog', 'catsand']),
            ('a' * 20, ['b', 'bb']),
            ('pineapplepenapple', ['apple', 'pen', 'applepen', 'pine', 'pineapple']),
        ]
        for s, wordDict in cases:
            with self.subTest(s=s, wordDict=wordDict):
                self.assertLessEqual(len(s), 20)
                produced = self.check(s, wordDict, with_cuts=False)
                total = sum(len(sentence) for sentence in produced)
                self.assertLessEqual(total, 100_000, 'answer budget exceeded by the case')
                self.assertEqual(self.normalise(produced),
                                 self.normalise(enumeration_oracle(s, wordDict)))

        # A 1000-word dictionary against a 20-character string.
        pool = set()
        for index in range(26):
            letter = chr(97 + index)
            for length in range(1, 21):
                pool.add(letter * length)              # lengths 1..20
                if length <= 19:
                    pool.add(letter * length + 'q')    # lengths 2..20
                    pool.add(letter * length + 'z')    # lengths 2..20
        self.assertGreaterEqual(len(pool), 1000)
        self.assertLessEqual(max(len(word) for word in pool), 20)

        essential = {'cat', 'cats', 'and', 'sand', 'dog', 'catsanddog'}
        others = sorted(word for word in pool if word not in essential)
        wordDict = sorted(essential | set(others[:1000 - len(essential)]))
        self.assertEqual(len(wordDict), 1000)
        self.assertLessEqual(max(len(word) for word in wordDict), 20)

        s = 'catsanddogcatsanddog'
        produced = self.solve(s, wordDict)
        self.validate(s, wordDict, produced)
        self.assertTrue(produced)
        self.assertLessEqual(sum(len(sentence) for sentence in produced), 100_000)


if __name__ == '__main__':
    unittest.main()
