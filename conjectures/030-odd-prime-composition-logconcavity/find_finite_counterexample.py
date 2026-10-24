"""Exact targeted search for the first prime-input k=3 log-concavity failure.

For prime q, c(q,1)=1, so the asymptotic counterexample is witnessed as soon
as c(q,3)^2 < c(q,5). This computes only the k<=5 rows, using integer
convolution by the odd-prime indicator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def primes_upto(n: int) -> list[int]:
    sieve = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        sieve[0] = 0
    if n >= 1:
        sieve[1] = 0
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : n + 1 : p] = b"\x00" * (((n - start) // p) + 1)
    return [p for p in range(3, n + 1) if sieve[p]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10_000)
    args = parser.parse_args()
    limit = args.max_n
    primes = primes_upto(limit)

    # a[k][n] = [x^n] (sum_{odd prime p} x^p)^k
    rows = [[0] * (limit + 1) for _ in range(6)]
    rows[0][0] = 1
    for k in range(1, 6):
        prev, row = rows[k - 1], rows[k]
        for p in primes:
            for n in range(p, limit + 1):
                row[n] += prev[n - p]

    witness = None
    prime_inputs_checked = 0
    for q in primes:
        prime_inputs_checked += 1
        lhs = rows[3][q] ** 2
        rhs = rows[5][q]
        if lhs < rhs:
            witness = {
                "q": q,
                "c_q_1": 1,
                "c_q_3": str(rows[3][q]),
                "c_q_5": str(rows[5][q]),
                "lhs": str(lhs),
                "rhs": str(rhs),
                "gap": str(rhs - lhs),
            }
            break

    result = {
        "definition": "ordered compositions into odd prime parts",
        "max_n": limit,
        "method": "exact integer convolution dynamic program for k=0..5",
        "prime_inputs_checked": prime_inputs_checked,
        "first_counterexample": witness,
        "conclusion": "first finite prime-input k=3 failure found" if witness else "no failure in this finite range",
    }
    output = Path(__file__).with_name("finite-counterexample-search.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
