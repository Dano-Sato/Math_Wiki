"""Exact checks accompanying 037 v0.2, using only the Python standard library.

Bell's triangle computes b_n in O(N^2) integer additions, rather than repeated
large binomial sums. Small-range checks use both block-size and block-count
recurrences, and actual set partitions. No finite check proves unimodality.
"""
from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path
from time import perf_counter


def bell_triangle_no_singletons(max_n: int) -> list[int]:
    """Use B_n = b_n + b_{n+1}; B_n is the first entry of Bell triangle row n."""
    b = [1]
    triangle = [1]
    for n in range(max_n):
        b.append(triangle[0] - b[-1])
        if n + 1 < max_n:
            following = [triangle[-1]]
            for value in triangle:
                following.append(following[-1] + value)
            triangle = following
    return b


def block_size_counts(max_n: int) -> list[int]:
    b = [1] + [0] * max_n
    for n in range(2, max_n + 1):
        b[n] = sum(comb(n - 1, j - 1) * b[n - j] for j in range(2, n + 1))
    return b


def block_count_rows(max_n: int) -> list[list[int]]:
    """S(n,j)=j*S(n-1,j)+(n-1)*S(n-2,j-1), for nonsingleton blocks."""
    rows = [[1]]
    if max_n:
        rows.append([0, 0])
    for n in range(2, max_n + 1):
        prev, older = rows[-1], rows[-2]
        rows.append([
            j * (prev[j] if j < len(prev) else 0)
            + (n - 1) * (older[j - 1] if 1 <= j <= len(older) else 0)
            for j in range(n + 1)
        ])
    return rows


def singleton_histogram(n: int) -> list[int]:
    """Enumerate actual set partitions via restricted growth strings (n >= 1)."""
    histogram = [0] * (n + 1)

    def visit(sizes: list[int], remaining: int) -> None:
        if not remaining:
            histogram[sizes.count(1)] += 1
            return
        for j in range(len(sizes)):
            sizes[j] += 1
            visit(sizes, remaining - 1)
            sizes[j] -= 1
        sizes.append(1)
        visit(sizes, remaining - 1)
        sizes.pop()

    visit([], n)
    return histogram


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=2000)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("review_2026-10-24.json"))
    args = parser.parse_args()
    if args.max_n < 8:
        parser.error("--max-n must be at least 8")
    started = perf_counter()
    b = bell_triangle_no_singletons(args.max_n)

    independent_n = min(80, args.max_n)
    sizes = block_size_counts(independent_n)
    blocks = block_count_rows(independent_n)
    require(b[:independent_n + 1] == sizes, "Block-size recurrence disagrees")
    require(b[:independent_n + 1] == list(map(sum, blocks)),
            "Block-count recurrence disagrees")
    for n in range(1, 9):
        actual = singleton_histogram(n)
        expected = [comb(n, k) * b[n - k] for k in range(n + 1)]
        require(actual == expected, f"Set partition enumeration disagrees: n={n}")

    for m in range(4, args.max_n + 1):
        require(b[m] >= 2 * b[m - 1] + m - 2, f"Growth bound fails: m={m}")

    # All comparisons below are exact integer cross products, without division.
    threshold_failures, old_ratio_failures = [], []
    for m in range(4, args.max_n):
        if (m + 1) * b[m] ** 2 + b[m] * b[m + 1] < m * b[m - 1] * b[m + 1]:
            threshold_failures.append(m)
        if (m + 1) * b[m] ** 2 < m * b[m - 1] * b[m + 1]:
            old_ratio_failures.append(m)

    first_nonunimodal = None
    tail_edges = 0
    examples = {}
    for n in range(2, args.max_n + 1):
        decreasing = False
        modes = []
        for k in range(n - 2):
            m = n - k
            difference = m * b[m - 1] - (k + 1) * b[m]
            if difference < 0:
                decreasing = True
            elif difference > 0 and decreasing and first_nonunimodal is None:
                first_nonunimodal = {"n": n, "increasing_edge_after_decrease": k}
            if n >= 5 and 3 * k + 2 >= n:
                tail_edges += 1
                require(difference <= 0, f"Tail increases: n={n}, k={k}")
                if n >= 6:
                    require(difference < 0, f"Strict tail fails: n={n}, k={k}")
        if n <= 10 or n in (100, 1000, args.max_n):
            # The adjacent comparison uses no binomial coefficients; a small
            # list of modes is obtained by the same exact comparison.
            for k in range(n - 1):
                left_ok = k == 0 or (n - k + 1) * b[n - k] >= k * b[n - k + 1]
                right_ok = k == n - 2 or (n - k) * b[n - k - 1] <= (k + 1) * b[n - k]
                if left_ok and right_ok:
                    modes.append(k)
            example = {"local_maxima": modes, "tail_starts_at": n // 3}
            # ceil((n-2)/3) equals floor(n/3), for integer n.
            if n <= 10:
                example["row"] = [comb(n, k) * b[n - k] for k in range(n - 1)]
            examples[str(n)] = example

    for n in range(4, args.max_n + 1):
        gap = 4 * comb(n, 4) * comb(n, 2) - comb(n, 3) ** 2
        require(gap > 0, f"Log-concavity obstruction fails: n={n}")
        require(36 * gap == n * n * (n - 1) ** 2 * (n - 2) * (2 * n - 7),
                f"Gap identity fails: n={n}")

    output = {
        "conjecture": "037", "version": "0.2", "max_n": args.max_n,
        "method": "Bell triangle integer additions; b[n+1]=B[n]-b[n]",
        "independent_recurrence_max_n": independent_n,
        "actual_set_partition_enumeration_max_n": 8,
        "growth_bound": {"range": [4, args.max_n], "failures": []},
        "threshold_monotonicity": {"range": [4, args.max_n - 1],
                                   "failures": threshold_failures},
        "old_q_monotonicity": {"range": [4, args.max_n - 1],
                               "failures": old_ratio_failures},
        "unimodality": {"range": [2, args.max_n],
                        "first_failure": first_nonunimodal},
        "decreasing_tail": {"range": [5, args.max_n], "checked_edges": tail_edges,
                            "strict_for_n_at_least": 6, "failures": []},
        "log_concavity_obstruction": {"range": [4, args.max_n], "failures": []},
        "examples": examples,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "scope": "Finite checks only. Universal growth/tail/obstruction proofs are in conjectures.md; full unimodality and threshold monotonicity remain unproved.",
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in (
        "max_n", "independent_recurrence_max_n", "threshold_monotonicity",
        "old_q_monotonicity", "unimodality", "decreasing_tail", "elapsed_seconds")},
        ensure_ascii=False))


if __name__ == "__main__":
    main()
