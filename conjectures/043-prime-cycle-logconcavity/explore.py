"""Exact checks for conjecture 043.

Run: python explore.py [N]

The recurrence counts permutations by the number of cycles whose lengths are
prime. All arithmetic is integral; the finite verification is not a proof.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def prime_sieve(limit: int) -> list[bool]:
    is_prime = [True] * (limit + 1)
    if limit >= 0:
        is_prime[0] = False
    if limit >= 1:
        is_prime[1] = False
    for p in range(2, math.isqrt(limit) + 1):
        if is_prime[p]:
            for q in range(p * p, limit + 1, p):
                is_prime[q] = False
    return is_prime


def count_rows(limit: int) -> list[list[int]]:
    is_prime = prime_sieve(limit)
    rows = [[1]]
    for n in range(1, limit + 1):
        row = [0] * (n + 1)
        for cycle_length in range(1, n + 1):
            # Choose the cycle containing 1, then permute its remaining labels.
            factor = math.factorial(n - 1) // math.factorial(n - cycle_length)
            marked = int(is_prime[cycle_length])
            for k, count in enumerate(rows[n - cycle_length]):
                row[k + marked] += factor * count
        rows.append(row)
    return rows


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    rows = count_rows(limit)
    bad = []
    checked = 0
    inequalities = 0
    for n in range(1, limit + 1):
        row = rows[n]
        while row and row[-1] == 0:
            row.pop()
        checked += 1
        if sum(row) != math.factorial(n):
            raise AssertionError(f"coefficient sum mismatch at n={n}")
        if n >= 2:
            for k in range(1, len(row) - 1):
                inequalities += 1
                gap = row[k] * row[k] - row[k - 1] * row[k + 1]
                if gap <= 0:
                    bad.append({"n": n, "k": k, "gap": str(gap), "coefficients": row})

    payload = {
        "conjecture": "043 v0.1",
        "range": [1, limit],
        "method": "exact integer recurrence; coefficient sums checked against n!; adjacent log-concavity differences checked as integers",
        "coefficient_rows_checked": checked,
        "strict_log_concavity_inequalities_checked": inequalities,
        "nonpositive_gaps": bad,
        "selected_rows": {str(n): rows[n] for n in range(1, min(limit, 25) + 1)},
        "caveat": "Finite verification is not a proof.",
    }
    out = Path(__file__).with_name("experiment.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("range", "coefficient_rows_checked", "strict_log_concavity_inequalities_checked", "nonpositive_gaps")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
