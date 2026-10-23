"""Exact leaf-count distribution for complete bipartite graphs K_{a,b}.

The degree-sequence formula uses the bipartite Prüfer code. The script checks
the resulting coefficients and log-concavity for 1 <= a <= b <= LIMIT.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

LIMIT = 40


def stirling_second(n: int) -> list[list[int]]:
    table = [[0] * (n + 1) for _ in range(n + 1)]
    table[0][0] = 1
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            table[i][j] = table[i - 1][j - 1] + j * table[i - 1][j]
    return table


def leaf_counts(a: int, b: int, stirling: list[list[int]]) -> list[int]:
    """Return a_k(K_{a,b}) using the bipartite Prüfer degree formula."""
    counts = [0] * (a + b + 1)
    for q_a in range(a + 1):
        if q_a > b - 1:
            continue
        weight_a = math.comb(a, q_a) * math.factorial(q_a) * stirling[b - 1][q_a]
        for q_b in range(b + 1):
            if q_b > a - 1:
                continue
            weight_b = math.comb(b, q_b) * math.factorial(q_b) * stirling[a - 1][q_b]
            leaves = a + b - q_a - q_b
            counts[leaves] += weight_a * weight_b
    return counts


def main() -> None:
    stirling = stirling_second(LIMIT)
    pairs_checked = 0
    tree_totals_checked = 0
    failures = []
    for a in range(1, LIMIT + 1):
        for b in range(a, LIMIT + 1):
            counts = leaf_counts(a, b, stirling)
            expected = a ** (b - 1) * b ** (a - 1)
            if sum(counts) != expected:
                raise AssertionError(f"spanning-tree total mismatch for K_{{{a},{b}}}")
            tree_totals_checked += 1
            first = next(i for i, value in enumerate(counts) if value)
            last = len(counts) - 1 - next(i for i, value in enumerate(reversed(counts)) if value)
            row = counts[first:last + 1]
            if any(row[i] ** 2 < row[i - 1] * row[i + 1]
                   for i in range(1, len(row) - 1)):
                failures.append({"a": a, "b": b, "coefficients": row})
            pairs_checked += 1

    payload = {
        "family": "complete bipartite graphs K_{a,b}",
        "side_sizes": [1, LIMIT],
        "unordered_parameter_pairs_checked": pairs_checked,
        "spanning_tree_totals_checked": tree_totals_checked,
        "log_concavity_failures": failures,
        "method": "exact integer degree-sequence formula from bipartite Prüfer codes",
        "scope": "Finite formula check; the class-wide proof is recorded in discussion.md.",
    }
    output = Path(__file__).with_name("bipartite_experiment.json")
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))


if __name__ == "__main__":
    main()
