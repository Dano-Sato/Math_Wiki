"""Exact finite check for conjecture 076: N = p + q^2 with p,q prime.

The check is finite evidence only. It does not establish the eventual claim.
"""

from __future__ import annotations

import json
from math import isqrt
from pathlib import Path


LIMIT = 1_000_000


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
    is_prime = prime_sieve(LIMIT)
    prime_roots = [q for q in range(2, isqrt(LIMIT) + 1) if is_prime[q]]
    eligible = 0
    represented = 0
    failures: list[int] = []
    samples: list[dict[str, int]] = []

    for n in range(4, LIMIT + 1, 2):
        if n % 3 == 1 or isqrt(n) ** 2 == n:
            continue
        eligible += 1
        witness = None
        for q in prime_roots:
            p = n - q * q
            if p < 2:
                break
            if is_prime[p]:
                witness = (p, q)
                break
        if witness is None:
            failures.append(n)
        else:
            represented += 1
            if len(samples) < 12:
                samples.append({"N": n, "p": witness[0], "q": witness[1]})

    result = {
        "claim": "For sufficiently large even N, if N is not a square and N != 1 (mod 3), then N = p + q^2 for primes p,q.",
        "limit_inclusive": LIMIT,
        "eligible_even_inputs": eligible,
        "represented_inputs": represented,
        "unrepresented_inputs": failures,
        "last_unrepresented_input": failures[-1] if failures else None,
        "sample_representations": samples,
        "method": "Exact Eratosthenes sieve and exhaustive prime-q search for every eligible even N in range.",
        "scope_note": "Finite verification only; does not prove the eventual conjecture.",
    }
    path = Path(__file__).with_name("verification.json")
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
