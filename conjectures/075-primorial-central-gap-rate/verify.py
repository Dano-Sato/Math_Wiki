"""Exact meet-in-the-middle check for conjecture 075, k = 1,...,42.

All divisor candidates and square-root comparisons are exact integers. Logs are
computed only after the central pair is known, to report its normalized gap.
"""

from bisect import bisect_right
from math import isqrt, log, log1p
import json


def first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % p for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 1
    return primes


def subset_products(values: list[int]) -> list[int]:
    products = [1]
    for value in values:
        products += [product * value for product in products]
    return products


def central_pair(k: int) -> tuple[int, int]:
    primes = first_primes(k)
    primorial = 1
    for p in primes:
        primorial *= p

    midpoint_floor = isqrt(primorial)
    split = k // 2
    left_products = subset_products(primes[:split])
    right_products = sorted(subset_products(primes[split:]))

    below = 0
    above = primorial
    for left in left_products:
        index = bisect_right(right_products, midpoint_floor // left) - 1
        if index >= 0:
            candidate = left * right_products[index]
            if candidate > below:
                below = candidate

        next_index = index + 1
        if next_index < len(right_products):
            candidate = left * right_products[next_index]
            if candidate < above:
                above = candidate

    assert below * below < primorial < above * above
    return below, above


def main() -> None:
    rows = []
    for k in range(1, 43):
        below, above = central_pair(k)
        gap = log1p((above - below) / below)
        rows.append(
            {
                "k": k,
                "A": str(below),
                "B": str(above),
                "log_gap_approx": gap,
                "minus_log2_gap_over_k": -log(gap, 2) / k,
            }
        )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
