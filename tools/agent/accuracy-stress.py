"""Stress the accuracy of the exponentiation variants against a 60-digit truth.

The failing judge case is a base extremely close to -1 with a huge exponent.
Repeated squaring stores the base as a float near 1, which destroys the relative
precision of (1 - base); the error is then amplified by the exponent. This
script measures the worst absolute error of each candidate over that regime.
"""
from decimal import Decimal, getcontext
import math
import random

getcontext().prec = 60


def truth(x: float, n: int) -> Decimal:
    """Exact value of x**n at 60 digits, via the exact binary expansion of x."""
    base = Decimal(x)
    exponent = abs(n)
    result = Decimal(1)
    while exponent:
        if exponent & 1:
            result *= base
        base *= base
        exponent >>= 1
    if n < 0:
        result = Decimal(1) / result
    return result


def invert_first(x: float, n: int) -> float:
    if n < 0:
        x = 1.0 / x
        n = -n
    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result


def invert_last(x: float, n: int) -> float:
    exponent = -n if n < 0 else n
    result = 1.0
    base = x
    while exponent:
        if exponent & 1:
            result *= base
        base *= base
        exponent >>= 1
    return 1.0 / result if n < 0 else result


def log_domain(x: float, n: int) -> float:
    """Work in the log domain: ln|x**n| = n * ln|x|, computed with log1p."""
    magnitude = math.exp(n * math.log1p(abs(x) - 1.0))
    if x < 0 and n % 2:
        return -magnitude
    return magnitude


def hybrid(x: float, n: int, threshold: float = 1e-3) -> float:
    """Exponentiation by squaring, with the log domain used near +-1."""
    if abs(abs(x) - 1.0) < threshold:
        return log_domain(x, n)
    exponent = -n if n < 0 else n
    result = 1.0
    base = x
    while exponent:
        if exponent & 1:
            result *= base
        base *= base
        exponent >>= 1
    return 1.0 / result if n < 0 else result


def worst(candidate, cases) -> tuple[float, tuple]:
    worst_error = 0.0
    worst_case = None
    for x, n in cases:
        expected = truth(x, n)
        got = candidate(x, n)
        error = abs(Decimal(got) - expected)
        if error > worst_error:
            worst_error = error
            worst_case = (x, n)
    return worst_error, worst_case


def build_cases():
    rng = random.Random(50)
    candidates = []

    # Bases hugging +1 and -1, which is the regime that breaks squaring.
    for delta in (1e-4, 1e-6, 1e-7, 3e-9, 1e-9, 5e-10, 1e-12, 1e-15):
        for sign in (1.0, -1.0):
            for exponent in (10 ** 9, 2 ** 31 - 1, 2 ** 31, 1669585506, 123456789, 999):
                candidates.append((sign * (1.0 - delta), exponent))
                candidates.append((sign * (1.0 - delta), -exponent))

    # The exact case the judge rejected.
    candidates.append((-0.9999999968539456, -1669585506))

    # Ordinary values.
    for _ in range(600):
        x = rng.uniform(-100, 100)
        if abs(x) < 1e-6:
            continue
        n = rng.choice([rng.randint(-1000, 1000), rng.randint(-(2 ** 31), 2 ** 31 - 1)])
        candidates.append((x, n))

    # The problem guarantees -10^4 <= x**n <= 10^4, i.e. |n * ln|x|| <= ln(1e4).
    # Anything outside that range is not a legal input, and skipping it also
    # keeps the Decimal oracle from overflowing.
    limit = math.log(10 ** 4)
    return [
        (x, n) for x, n in candidates
        if abs(n * math.log(abs(x))) <= limit
    ]


cases = build_cases()
print(f'cases: {len(cases)}   (judge tolerance is 1e-5 absolute)\n')

for name, candidate in (('invert_first', invert_first),
                        ('invert_last', invert_last),
                        ('log_domain', log_domain),
                        ('hybrid 1e-3', hybrid),
                        ('hybrid 1e-6', lambda x, n: hybrid(x, n, 1e-6)),
                        ('hybrid 1e-2', lambda x, n: hybrid(x, n, 1e-2))):
    error, case = worst(candidate, cases)
    verdict = 'PASS' if error < Decimal('1e-5') else 'FAIL'
    print(f'{name:<14} worst abs error = {float(error):.3e}   {verdict}')
    print(f'{"":<14} worst case: x={case[0]!r}, n={case[1]}')
