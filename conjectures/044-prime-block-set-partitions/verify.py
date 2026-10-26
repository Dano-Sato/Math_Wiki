"""Exact finite verification for conjecture 044.

Counts set partitions by the number of blocks whose sizes are prime.
The recurrence partitions according to the block containing element 1.
"""

from __future__ import annotations

import json
from math import comb
from pathlib import Path


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def coefficients(max_n: int) -> list[list[int]]:
    # a[n][k] = number of partitions of [n] with k prime-size blocks.
    a = [[0] * (max_n // 2 + 2) for _ in range(max_n + 1)]
    a[0][0] = 1
    for n in range(1, max_n + 1):
        for block_size in range(1, n + 1):
            prime_block = is_prime(block_size)
            choices = comb(n - 1, block_size - 1)
            for k in range(n // 2 + 1):
                old_k = k - 1 if prime_block else k
                if old_k >= 0:
                    a[n][k] += choices * a[n - block_size][old_k]
    return a


def main() -> None:
    max_n = 100
    a = coefficients(max_n)
    checked = 0
    first_failure = None
    rows = []
    for n in range(1, max_n + 1):
        seq = a[n][: n // 2 + 1]
        for k in range(1, len(seq) - 1):
            checked += 1
            if seq[k] * seq[k] < seq[k - 1] * seq[k + 1]:
                first_failure = {"n": n, "k": k, "triple": seq[k - 1 : k + 2]}
                break
        rows.append({"n": n, "coefficients": seq})
        if first_failure:
            break
    result = {
        "conjecture": "044",
        "range": [1, max_n],
        "method": "exact integer recurrence by the block containing element 1",
        "log_concavity_inequalities_checked": checked,
        "all_checked_log_concave": first_failure is None,
        "first_failure": first_failure,
        "rows": rows,
    }
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
