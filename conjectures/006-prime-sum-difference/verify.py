"""Exact finite matching certificates for conjecture 006, standard library only."""

import argparse
import json
from collections import deque
from itertools import permutations
from math import isqrt, log
from pathlib import Path


def sieve(limit):
    flags = bytearray(b"\1") * (limit + 1)
    flags[:2] = b"\0\0"
    for p in range(2, isqrt(limit) + 1):
        if flags[p]:
            flags[p * p::p] = b"\0" * ((limit - p * p) // p + 1)
    return flags


def trial_prime(value):
    return value >= 2 and all(value % d for d in range(2, isqrt(value) + 1))


def match(n, bound, primes, flags):
    adjacency = []
    for u in range(n):
        odd = 2 * u + 1
        neighbors = []
        for difference in primes:
            if difference > bound:
                break
            if difference == 2:
                continue
            for even in (odd - difference, odd + difference):
                if 2 <= even <= 2 * n and flags[odd + even]:
                    neighbors.append(even // 2 - 1)
        adjacency.append(sorted(neighbors))
    left = [-1] * n
    right = [-1] * n
    for root in sorted(range(n), key=lambda u: len(adjacency[u])):
        queue = deque([root])
        visited = {root}
        parent = [-1] * n
        free = -1
        while queue and free < 0:
            u = queue.popleft()
            for v in adjacency[u]:
                if parent[v] >= 0:
                    continue
                parent[v] = u
                if right[v] < 0:
                    free = v
                    break
                partner = right[v]
                if partner not in visited:
                    visited.add(partner)
                    queue.append(partner)
        if free < 0:
            neighbors = set().union(*(set(adjacency[u]) for u in visited))
            if len(neighbors) >= len(visited):
                raise AssertionError("Invalid Hall obstruction")
            return None, {
                "odd_subset": [2 * u + 1 for u in sorted(visited)],
                "even_neighbors": [2 * v + 2 for v in sorted(neighbors)],
            }
        while free >= 0:
            u = parent[free]
            old = left[u]
            left[u] = free
            right[free] = u
            free = old
    return [[2 * u + 1, 2 * left[u] + 2] for u in range(n)], None


def verify_certificate(n, pairs, bound):
    assert sorted(value for pair in pairs for value in pair) == list(range(1, 2 * n + 1))
    for x, y in pairs:
        assert trial_prime(x + y) and trial_prime(abs(x - y))
        assert abs(x - y) <= bound


def minimum_span(n, primes, flags):
    maximum = 2 * n - 1
    upper = min(3, maximum)
    while True:
        pairs, obstruction = match(n, upper, primes, flags)
        if pairs is not None:
            break
        if upper == maximum:
            return {"n": n, "exists": False, "full_graph_hall_obstruction": obstruction}
        upper = min(maximum, 2 * upper)
    low = 0
    while low + 1 < upper:
        middle = (low + upper) // 2
        candidate, _ = match(n, middle, primes, flags)
        if candidate is None:
            low = middle
        else:
            upper = middle
    pairs, _ = match(n, upper, primes, flags)
    _, obstruction = match(n, upper - 1, primes, flags)
    verify_certificate(n, pairs, upper)
    # Independently check the saved lower-bound obstruction by trial division.
    odd_subset = obstruction["odd_subset"]
    actual_neighbors = sorted({
        y for x in odd_subset for y in range(2, 2 * n + 1, 2)
        if abs(x - y) < upper and trial_prime(x + y) and trial_prime(abs(x - y))
    })
    assert actual_neighbors == obstruction["even_neighbors"]
    assert len(actual_neighbors) < len(odd_subset)
    return {
        "n": n, "exists": True, "minimum_span": upper,
        "span_over_log_squared": upper / log(n) ** 2 if n > 1 else None,
        "pairs": pairs,
        "lower_bound_hall_obstruction": obstruction,
    }


def literal_exists(n):
    odds = list(range(1, 2 * n, 2))
    for evens in permutations(range(2, 2 * n + 1, 2)):
        if all(trial_prime(x + y) and trial_prime(abs(x - y)) for x, y in zip(odds, evens)):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=500)
    parser.add_argument("--samples", type=int, nargs="*", default=[1000, 2000, 5000])
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("experiment.json"))
    args = parser.parse_args()
    if args.through < 8 or any(n < 1 for n in args.samples):
        parser.error("--through must be >=8; sample sizes must be positive")
    sizes = sorted(set(range(1, args.through + 1)) | set(args.samples))
    flags = sieve(4 * max(sizes))
    primes = [p for p in range(2, 2 * max(sizes)) if flags[p]]
    rows = []
    for n in sizes:
        row = minimum_span(n, primes, flags)
        if n <= 8:
            assert row["exists"] == literal_exists(n)
        rows.append(row)
    existing = [row for row in rows if row["exists"]]
    result = {
        "definition_version": "006-0.1", "date": "2026-10-24",
        "all_sizes_through": args.through, "additional_sizes": args.samples,
        "failed_sizes": [row["n"] for row in rows if not row["exists"]],
        "literal_permutation_comparison_through": 8,
        "all_saved_pairs_trial_division_checked": True,
        "all_minimum_span_lower_bounds_have_checked_Hall_certificates": True,
        "maximum_observed_span": max(row["minimum_span"] for row in existing),
        "scope": "Exact finite certificates only; no universal existence or asymptotic bound proved.",
        "rows": rows,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("failures:", result["failed_sizes"])
    for row in rows:
        if row["n"] in (4, 5, 10, 50, 100, 500, *args.samples):
            print({key: row[key] for key in ("n", "minimum_span", "span_over_log_squared")})


if __name__ == "__main__":
    main()
