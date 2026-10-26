"""Exact modular evidence for conjecture 083.

Counts n <= X for which n!+1 has a prime divisor r <= C*n.
Every prime divisor of n!+1 is greater than n, so checking these r is
equivalent to checking whether the least prime factor is <= C*n.
"""

from __future__ import annotations

import json
from math import isqrt, log
from pathlib import Path


X = 20_000
THRESHOLDS = [(11, 10), (5, 4), (3, 2), (2, 1)]


def prime_sieve(limit: int) -> bytearray:
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[:2] = b"\x00\x00"
    for p in range(2, isqrt(limit) + 1):
        if is_prime[p]:
            start = p * p
            count = (limit - start) // p + 1
            is_prime[start : limit + 1 : p] = b"\x00" * count
    return is_prime


def main() -> None:
    is_prime = prime_sieve(2 * X)
    least_factor: list[int | None] = [None] * (X + 1)

    # For each prime r, update n! mod r for 1 <= n < r.
    # If it equals -1, then r divides n!+1.
    for r in range(3, 2 * X + 1):
        if not is_prime[r]:
            continue
        factorial_mod = 1
        for n in range(1, min(X, r - 1) + 1):
            factorial_mod = factorial_mod * n % r
            if factorial_mod == r - 1 and r <= 2 * n and least_factor[n] is None:
                least_factor[n] = r

    wilson_count = sum(1 for n in range(2, X + 1) if is_prime[n + 1])
    rows = []
    for numerator, denominator in THRESHOLDS:
        count = sum(
            1
            for n in range(2, X + 1)
            if least_factor[n] is not None
            and least_factor[n] * denominator <= numerator * n
        )
        rows.append(
            {
                "C": f"{numerator}/{denominator}",
                "count": count,
                "normalized_by_X_over_log_X": count * log(X) / X,
                "predicted_constant": 1 + log(numerator / denominator),
            }
        )

    result = {
        "X_inclusive": X,
        "threshold_counts": rows,
        "wilson_forced_inputs_n_plus_1_prime": wilson_count,
        "method": "For every prime r <= 2X, exact recurrence for n! modulo r; mark n when n! = -1 (mod r).",
        "scope_note": "Exact finite modular check only; it provides no asymptotic proof.",
    }
    Path(__file__).with_name("verification.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
