"""Exact counts of partitions by number of distinct part sizes."""

from __future__ import annotations

import json
from pathlib import Path


def counts_by_support_size(max_n: int) -> list[list[int]]:
    """Return rows a[n][k] for n <= max_n using exact integer arithmetic."""
    dp = [[0] * (max_n + 1) for _ in range(max_n + 1)]
    dp[0][0] = 1
    for part_size in range(1, max_n + 1):
        updated = [row[:] for row in dp]
        # A partition counted in the new table either omits this size, or
        # uses it positively. For each residue modulo part_size, maintain
        # the sum over all possible positive multiplicities from the old
        # table, where only smaller part sizes have been processed.
        max_distinct = int((2 * max_n) ** 0.5) + 2
        for residue in range(part_size):
            for distinct_count in range(max_distinct):
                positive_multiplicity_sum = 0
                for total in range(residue, max_n + 1, part_size):
                    if total >= residue + part_size:
                        positive_multiplicity_sum += dp[total - part_size][distinct_count]
                    if positive_multiplicity_sum:
                        updated[total][distinct_count + 1] += positive_multiplicity_sum
        dp = updated
    return dp


def support_limit(n: int) -> int:
    """Largest k with 1 + ... + k <= n."""
    k = 0
    while (k + 1) * (k + 2) // 2 <= n:
        k += 1
    return k


def log_concavity_failures(rows: list[list[int]]) -> list[dict[str, object]]:
    failures = []
    for n in range(1, len(rows)):
        top = support_limit(n)
        for k in range(2, top):
            left = rows[n][k] ** 2
            right = rows[n][k - 1] * rows[n][k + 1]
            if left < right:
                failures.append({"n": n, "k": k, "left": left, "right": right})
    return failures


def ordinary_partition_counts(max_n: int) -> list[int]:
    """Return p(n) for n <= max_n by the standard parts DP."""
    counts = [0] * (max_n + 1)
    counts[0] = 1
    for part_size in range(1, max_n + 1):
        for total in range(part_size, max_n + 1):
            counts[total] += counts[total - part_size]
    return counts


def main() -> None:
    max_n = 1000
    rows = counts_by_support_size(max_n)
    failures = log_concavity_failures(rows)
    partition_counts = ordinary_partition_counts(max_n)
    two_color_counts = [
        sum(partition_counts[i] * partition_counts[n - i] for i in range(n + 1))
        for n in range(max_n + 1)
    ]
    extreme_formula_matches = all(
        rows[n][support_limit(n)]
        == two_color_counts[n - support_limit(n) * (support_limit(n) + 1) // 2]
        for n in range(1, max_n + 1)
    )
    examples = {str(n): rows[n][1 : support_limit(n) + 1] for n in (10, 100, 1000)}
    output = {
        "max_n": max_n,
        "arithmetic": "exact integers",
        "checked_internal_inequalities": sum(max(0, support_limit(n) - 2) for n in range(1, max_n + 1)),
        "failure_count": len(failures),
        "first_failures": failures[:10],
        "briand_extreme_coefficient_formula_matches": extreme_formula_matches,
        "briand_formula_checked_n": max_n,
        "sample_rows_k_from_1": examples,
    }
    target = Path(__file__).with_name("experiment.json")
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
