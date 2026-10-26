"""Finite exploration of the dual average identity in L14.

This computes the original self-totient recurrence exactly using Möbius
inversion. The resulting averages are finite observations, not a proof
of either limiting statement.
"""

import argparse
import json
import math
from array import array
from pathlib import Path

from review_verify import factors, signed_divisors, sieve


def run(limit):
    if limit < 2:
        raise ValueError("limit must be at least 2")
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    counts[1] = 1
    sum_a = 1
    sum_abs_error = 0
    sum_b = 1.0  # phi(a_1) / a_1
    weighted_b = 0.0
    checkpoints = []
    next_power = 10

    for n in range(2, limit + 1):
        weighted_b += sum_b
        n_primes = factors(n, spf)
        value = sum(sign * counts[d]
                    for d, sign in signed_divisors(n_primes))
        if not 1 <= value < n:
            raise AssertionError((n, value))
        sum_a += value
        phi_n = n
        for prime in n_primes:
            phi_n = phi_n // prime * (prime - 1)
        sum_abs_error += abs(value - phi_n)
        primes = factors(value, spf)
        phi_over_value = math.prod(1.0 - 1.0 / p for p in primes)
        sum_b += phi_over_value
        for d, _ in signed_divisors(primes):
            counts[d] += 1

        if n == next_power or n == limit:
            checkpoints.append({
                "N": n,
                "mean_phi_a_over_a": sum_b / n,
                "sum_a_over_N_squared": sum_a / (n * n),
                "sum_abs_a_minus_phi_over_N_squared": sum_abs_error / (n * n),
                "dual_floor_error": sum_a - 1 - weighted_b,
            })
            next_power *= 10

    return {
        "limit": limit,
        "target_mean_phi_a_over_a": 6.0 / (math.pi ** 2),
        "target_sum_a_over_N_squared": 3.0 / (math.pi ** 2),
        "scope": "Finite recurrence computation; no asymptotic claim proved.",
        "checkpoints": checkpoints,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.limit)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
