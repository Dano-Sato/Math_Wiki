"""Exact finite scan for conjecture 072: N/2 ± t^2 are both prime."""

import json
from math import isqrt
from pathlib import Path


LIMIT = 1_000_000


def prime_table(limit):
    prime = bytearray(b"\x01") * (limit + 1)
    prime[0:2] = b"\x00\x00"
    for p in range(2, isqrt(limit) + 1):
        if prime[p]:
            prime[p * p : limit + 1 : p] = b"\x00" * ((limit - p * p) // p + 1)
    return prime


def main():
    prime = prime_table(LIMIT)
    tested = 0
    represented = 0
    first_failures = []
    last_failures = []
    checkpoints = {}

    for n in range(6, LIMIT + 1, 2):
        tested += 1
        middle = n // 2
        # M ± t² must be odd, so t and M have opposite parity.
        first_t = 1 if middle % 2 == 0 else 2
        witness = None
        for t in range(first_t, isqrt(middle - 2) + 1, 2):
            left = middle - t * t
            right = middle + t * t
            if prime[left] and prime[right]:
                witness = t
                break
        if witness is not None:
            represented += 1
            if n in (100, 1_000, 10_000, 100_000, 1_000_000):
                checkpoints[str(n)] = {"t": witness, "primes": [middle - witness**2, middle + witness**2]}
        else:
            if len(first_failures) < 30:
                first_failures.append(n)
            last_failures.append(n)
            if len(last_failures) > 30:
                last_failures.pop(0)

    result = {
        "method": "exact sieve plus exhaustive t search; no floating-point arithmetic",
        "limit": LIMIT,
        "even_N_tested": tested,
        "represented": represented,
        "not_represented": tested - represented,
        "represented_fraction": represented / tested,
        "first_30_failures": first_failures,
        "last_30_failures": last_failures,
        "checkpoint_witnesses": checkpoints,
        "scope": "Finite verification only; it does not establish that failures eventually stop.",
    }
    Path(__file__).with_name("verification.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
