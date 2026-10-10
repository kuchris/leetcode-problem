"""Tests for 150. Evaluate Reverse Polish Notation.

Oracles:
  - ``expression_tree_value``: parses the tokens into an expression *tree* and
    evaluates it recursively — different control flow from the single-pass value
    stack under test.
  - ``random_expression``: generates random expression trees, emits their
    postorder as the token list and returns the value computed on the way up, so
    input and expectation come from one source. It tracks a magnitude bound per
    subtree and only applies an operator whose result provably fits in 32 bits,
    which keeps every generated case inside the statement's guarantee.
  - Division in both oracles goes through ``math.trunc(Fraction(a, b))``: exact
    rationals truncated toward zero, never ``/`` and never ``//`` (which floors,
    the classic wrong answer for -7 / 2).

Exhaustive sweep: every structurally valid, division-by-zero-free sequence of 3
and of 5 tokens over a small alphabet. Constraint-sized cases use the full 10^4
token budget, including a right-leaning chain that would overflow a recursive
evaluator's stack.
"""

import itertools
import math
import random
import unittest
from fractions import Fraction

from _loader import load_solution

Solution = load_solution('150-evaluate-reverse-polish-notation.py').Solution

OPERATORS = ('+', '-', '*', '/')
MAX_LEAF = 200
INT32_MAX = 2 ** 31 - 1
MAX_TOKENS = 10 ** 4


def combine(operator: str, left: int, right: int) -> int:
    """Exact evaluation of one operator, with truncation toward zero."""
    if operator == '+':
        return left + right
    if operator == '-':
        return left - right
    if operator == '*':
        return left * right
    return math.trunc(Fraction(left, right))


def expression_tree_value(tokens) -> int:
    """Parse to an expression tree, then evaluate it recursively."""
    stack = []
    for token in tokens:
        if token in OPERATORS:
            right = stack.pop()
            left = stack.pop()
            stack.append((token, left, right))
        else:
            stack.append(int(token))
    if len(stack) != 1:
        raise AssertionError(f'tokens are not one expression: {tokens}')

    def evaluate(node):
        if isinstance(node, int):
            return node
        operator, left, right = node
        return combine(operator, evaluate(left), evaluate(right))

    return evaluate(stack[0])


def expression_tree_value_iterative(tokens) -> int:
    """Same parse, but evaluated with an explicit post-order stack.

    Used for the 10^4-token cases: a 5000-deep right spine would overflow the
    recursive oracle's Python call stack, exactly as it would a recursive
    submission.
    """
    stack = []
    for token in tokens:
        if token in OPERATORS:
            right = stack.pop()
            left = stack.pop()
            stack.append((token, left, right))
        else:
            stack.append(int(token))
    if len(stack) != 1:
        raise AssertionError(f'tokens are not one expression: {tokens}')

    order = []
    pending = [stack[0]]
    while pending:
        node = pending.pop()
        order.append(node)
        if not isinstance(node, int):
            pending.append(node[1])
            pending.append(node[2])

    values = {}
    for node in reversed(order):          # children always come first
        if isinstance(node, int):
            values[id(node)] = node
        else:
            operator, left, right = node
            values[id(node)] = combine(operator, values[id(left)], values[id(right)])
    return values[id(stack[0])]


def random_expression(rng, leaves, budget=INT32_MAX, operators=OPERATORS):
    """A random expression with `leaves` leaves; returns (tokens, value, bound).

    ``bound`` is the exact magnitude of the subtree's value, so an operator is
    only used when its result certainly fits the statement's 32-bit guarantee.
    The tree is balanced above 64 leaves, which keeps the generator's own
    recursion shallow.
    """
    if leaves <= 1:
        value = rng.randint(-min(MAX_LEAF, budget), min(MAX_LEAF, budget))
        return [str(value)], value, abs(value)

    split = rng.randint(1, leaves - 1) if leaves <= 64 else leaves // 2
    left_tokens, left_value, left_bound = random_expression(rng, split, budget, operators)
    right_tokens, right_value, right_bound = random_expression(
        rng, leaves - split, budget, operators
    )

    choices = []
    if '+' in operators and left_bound + right_bound <= budget:
        total = left_value + right_value
        choices.append(('+', total, abs(total)))
    if '-' in operators and left_bound + right_bound <= budget:
        difference = left_value - right_value
        choices.append(('-', difference, abs(difference)))
    if '*' in operators and left_bound * right_bound <= budget:
        product = left_value * right_value
        choices.append(('*', product, abs(product)))
    if '/' in operators and right_value != 0:
        # |left / right| <= |left| because |right| >= 1.
        choices.append(('/', combine('/', left_value, right_value), left_bound))

    if not choices:
        # Unreachable for the operator sets used here (a zero right operand
        # always leaves '*', and a non-zero one always leaves '/'), but keep
        # the function total.
        value = rng.randint(-9, 9)
        return [str(value)], value, abs(value)

    operator, value, bound = rng.choice(choices)
    return left_tokens + right_tokens + [operator], value, bound


def valid_rpn_sequences(alphabet, length):
    """Every token sequence that is one complete, structurally valid expression."""
    for tokens in itertools.product(alphabet, repeat=length):
        depth = 0
        for token in tokens:
            if token in OPERATORS:
                if depth < 2:
                    depth = -1
                    break
                depth -= 1
            else:
                depth += 1
        if depth == 1:
            yield tokens


class EvaluateReversePolishNotationTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().evalRPN

    def check(self, tokens):
        expected = expression_tree_value(tokens)
        self.assertEqual(self.solve(list(tokens)), expected)
        return expected

    def test_official_examples(self):
        self.assertEqual(self.solve(["2", "1", "+", "3", "*"]), 9)
        self.assertEqual(self.solve(["4", "13", "5", "/", "+"]), 6)
        self.assertEqual(
            self.solve(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]),
            22,
        )
        self.check(["2", "1", "+", "3", "*"])
        self.check(["4", "13", "5", "/", "+"])
        self.check(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])

    def test_single_operand(self):
        for token in ("0", "7", "-200", "200"):
            with self.subTest(token=token):
                self.assertEqual(self.solve([token]), int(token))

    def test_division_truncates_toward_zero(self):
        # Python's // would answer -4 where the statement wants -3.
        self.assertEqual(self.solve(["7", "-2", "/"]), -3)
        self.assertEqual(self.solve(["-7", "2", "/"]), -3)
        self.assertEqual(self.solve(["7", "2", "/"]), 3)
        self.assertEqual(self.solve(["-7", "-2", "/"]), 3)
        self.assertEqual(self.solve(["1", "2", "/"]), 0)
        self.assertEqual(self.solve(["-1", "2", "/"]), 0)
        self.assertEqual(-7 // 2, -4)                      # the trap
        self.assertEqual(math.trunc(Fraction(-7, 2)), -3)  # the required answer
        self.check(["7", "-2", "/"])
        self.check(["-7", "2", "/"])

    def test_division_inside_a_larger_expression(self):
        # (10 * (6 / ((9 + 3) * -11))) + 17 + 5 == 22, because 6 / -132 == 0.
        self.assertEqual(
            self.solve(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]),
            22,
        )
        self.assertEqual(self.solve(["-5", "3", "/", "4", "+"]), 3)
        self.assertEqual(self.solve(["6", "-132", "/"]), 0)
        self.check(["-5", "3", "/", "4", "+"])

    def test_exhaustive_three_token_expressions(self):
        alphabet = ('-7', '-2', '0', '3', '5', '+', '-', '*', '/')
        checked = 0
        for tokens in valid_rpn_sequences(alphabet, 3):
            try:
                expected = expression_tree_value(tokens)
            except ZeroDivisionError:
                continue      # the statement excludes division by zero
            with self.subTest(tokens=tokens):
                self.assertEqual(self.solve(list(tokens)), expected)
            checked += 1
        # 5 * 5 * 4 = 100 operator placements, minus the 0-divisor ones.
        self.assertGreaterEqual(checked, 90)

    def test_exhaustive_five_token_expressions(self):
        alphabet = ('-7', '-2', '0', '3', '+', '-', '*', '/')
        checked = 0
        for tokens in valid_rpn_sequences(alphabet, 5):
            try:
                expected = expression_tree_value(tokens)
            except ZeroDivisionError:
                continue
            with self.subTest(tokens=tokens):
                self.assertEqual(self.solve(list(tokens)), expected)
            checked += 1
        self.assertGreater(checked, 500)

    def test_random_expressions_against_the_tree_oracle(self):
        rng = random.Random(1500)
        for case in range(500):
            leaves = rng.randint(1, 40)
            tokens, expected, _ = random_expression(rng, leaves)
            with self.subTest(case=case, tokens=tokens[:8]):
                self.assertEqual(len(tokens), 2 * leaves - 1)
                self.assertLessEqual(abs(expected), INT32_MAX)
                self.assertEqual(self.solve(tokens), expected)
                self.assertEqual(expression_tree_value(tokens), expected)

    def test_random_division_heavy_expressions(self):
        # Only '/' and '-', so the truncation rule is exercised at every node.
        rng = random.Random(1501)
        for case in range(300):
            leaves = rng.randint(2, 12)
            tokens, expected, _ = random_expression(
                rng, leaves, operators=('/', '-')
            )
            with self.subTest(case=case, tokens=tokens[:8]):
                self.assertEqual(self.solve(tokens), expected)
                self.assertEqual(self.solve(tokens), expression_tree_value(tokens))

    def test_random_expression_values_are_never_floats(self):
        rng = random.Random(1502)
        for _ in range(200):
            tokens, expected, _ = random_expression(rng, rng.randint(1, 12))
            result = self.solve(tokens)
            self.assertIsInstance(result, int)
            self.assertNotIsInstance(result, bool)
            self.assertEqual(result, expected)

    def test_thirty_two_bit_boundaries(self):
        # 2^30, negated, then doubled: -2^31 exactly, no intermediate outside
        # the signed 32-bit range.
        smallest = ["2"] * 30 + ["*"] * 29 + ["-1", "*", "2", "*"]
        self.assertEqual(self.solve(smallest), -(2 ** 31))
        self.assertEqual(expression_tree_value(smallest), -(2 ** 31))

        # 2^30 + (2^30 - 1) == 2^31 - 1 exactly.
        power = ["2"] * 30 + ["*"] * 29
        largest = power + power + ["1", "-", "+"]
        self.assertEqual(self.solve(largest), INT32_MAX)
        self.assertEqual(expression_tree_value(largest), INT32_MAX)

    def test_constraint_sized_chain(self):
        # 4999 ones added left to right: 9999 tokens in one deep right spine.
        tokens = ["1"] + ["1", "+"] * 4999
        self.assertEqual(len(tokens), MAX_TOKENS - 1)
        self.assertEqual(self.solve(tokens), 5000)
        self.assertEqual(expression_tree_value_iterative(tokens), 5000)

        # A chain alternating +1 and -1 leaves, with a known running total.
        tokens = ["200"]
        expected = 200
        for index in range(1, 5000):
            if index % 2:
                tokens += ["1", "+"]
                expected += 1
            else:
                tokens += ["1", "-"]
                expected -= 1
        self.assertEqual(len(tokens), 9999)
        self.assertEqual(self.solve(tokens), expected)
        self.assertEqual(expression_tree_value_iterative(tokens), expected)

    def test_constraint_sized_random_tree(self):
        rng = random.Random(1503)
        tokens, expected, _ = random_expression(rng, 5000)
        self.assertEqual(len(tokens), 9999)
        self.assertLessEqual(len(tokens), MAX_TOKENS)
        self.assertEqual(self.solve(tokens), expected)
        self.assertEqual(expression_tree_value_iterative(tokens), expected)


if __name__ == '__main__':
    unittest.main()
