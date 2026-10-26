"""Exact finite verification for conjecture 047.

Counts k-subsets of AG(d,q) by the dimension of their affine span.
The spanning-subset counts are obtained by triangular inversion over flats.
"""

from __future__ import annotations

import json
from itertools import combinations, product
from math import comb
from pathlib import Path


def gaussian_binomials(d: int, q: int) -> list[list[int]]:
    g = [[0] * (d + 1) for _ in range(d + 1)]
    g[0][0] = 1
    for n in range(1, d + 1):
        g[n][0] = g[n][n] = 1
        for r in range(1, n):
            g[n][r] = g[n - 1][r] + q ** (n - r) * g[n - 1][r - 1]
    return g


def affine_flat_count(d: int, r: int, q: int, g: list[list[int]]) -> int:
    return q ** (d - r) * g[d][r]


def rank_counts(d: int, q: int, k: int) -> list[int]:
    g = gaussian_binomials(d, q)
    spanning = []
    for r in range(d + 1):
        total = comb(q**r, k) if k <= q**r else 0
        for j in range(r):
            total -= affine_flat_count(r, j, q, g) * spanning[j]
        spanning.append(total)
    return [affine_flat_count(d, r, q, g) * spanning[r] for r in range(d + 1)]


def rank_of_points(points: tuple[tuple[int, ...], ...], q: int) -> int:
    if len(points) <= 1:
        return 0
    rows = [[(x - y) % q for x, y in zip(points[i], points[0])] for i in range(1, len(points))]
    rank = 0
    col = 0
    while rank < len(rows) and col < len(points[0]):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] % q), None)
        if pivot is None:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, q)
        rows[rank] = [(v * inv) % q for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                scale = rows[i][col]
                rows[i] = [(a - scale * b) % q for a, b in zip(rows[i], rows[rank])]
        rank += 1
        col += 1
    return rank


def brute_counts(d: int, q: int, k: int) -> list[int]:
    points = list(product(range(q), repeat=d))
    counts = [0] * (d + 1)
    for chosen in combinations(points, k):
        counts[rank_of_points(chosen, q)] += 1
    return counts


def feasible_support(d: int, q: int, k: int) -> tuple[int, int]:
    if k == 1:
        return (0, 0)
    return max(1, (k - 1).bit_length() if q == 2 else _ceil_log_base(k, q)), min(d, k - 1)


def _ceil_log_base(k: int, q: int) -> int:
    r, power = 0, 1
    while power < k:
        r += 1
        power *= q
    return r


def main() -> None:
    brute_cases = []
    for q, d in ((2, 1), (2, 2), (3, 1), (3, 2)):
        for k in range(1, min(q**d, 8) + 1):
            exact = rank_counts(d, q, k)
            brute = brute_counts(d, q, k)
            if exact != brute:
                raise AssertionError((q, d, k, exact, brute))
            brute_cases.append({"q": q, "d": d, "k": k, "matched": True})

    configurations = ((2, 14, 100), (3, 10, 100), (4, 8, 100), (5, 7, 100))
    tested = 0
    equalities = 0
    first_failure = None
    checked_parameters = 0
    for q, max_d, max_k in configurations:
        for d in range(1, max_d + 1):
            for k in range(1, min(q**d, max_k) + 1):
                counts = rank_counts(d, q, k)
                lo, hi = feasible_support(d, q, k)
                support = counts[lo : hi + 1]
                checked_parameters += 1
                for i in range(1, len(support) - 1):
                    tested += 1
                    delta = support[i] ** 2 - support[i - 1] * support[i + 1]
                    if delta == 0:
                        equalities += 1
                    if delta <= 0 and first_failure is None:
                        first_failure = {
                            "q": q,
                            "d": d,
                            "k": k,
                            "r": lo + i,
                            "difference": str(delta),
                        }

    result = {
        "conjecture": "047",
        "method": "exact triangular recurrence over affine flats",
        "brute_force_cross_checks": brute_cases,
        "configurations": [
            {"q": q, "max_d": d, "max_k": k} for q, d, k in configurations
        ],
        "parameter_cases_checked": checked_parameters,
        "strict_log_concavity_inequalities_checked": tested,
        "equalities": equalities,
        "all_checked_inequalities_strict": first_failure is None,
        "first_failure_or_equality": first_failure,
    }
    Path(__file__).with_name("experiment.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
