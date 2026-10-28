"""Finite candidate screening for 019; integer counts, not a general proof.

Enumerates every forward-edge DAG for n <= 6 and deduplicates closures.
Every finite poset admits a topological labeling, so this covers every
poset up to isomorphism in that range (with labeled duplicates retained).
For n = 7..12, samples forward-edge DAGs with a fixed seed.
"""

import itertools
import json
import random
from pathlib import Path


def closure(n, edges):
    successors = [0] * n
    for x, y in edges:
        successors[x] |= 1 << y
    for x in range(n - 1, -1, -1):
        for y in range(x + 1, n):
            if successors[x] >> y & 1:
                successors[x] |= successors[y]
    predecessors = [0] * n
    for x in range(n):
        for y in range(n):
            if successors[x] >> y & 1:
                predecessors[y] |= 1 << x
    return tuple(predecessors)


def exact_counts(pred):
    n = len(pred)
    size = 1 << n
    full = size - 1
    forward = [0] * size
    forward[0] = 1
    for mask in range(size):
        if not forward[mask]:
            continue
        for x in range(n):
            bit = 1 << x
            if not mask & bit and not pred[x] & ~mask:
                forward[mask | bit] += forward[mask]
    backward = [0] * size
    backward[full] = 1
    for mask in range(full - 1, -1, -1):
        if forward[mask]:
            backward[mask] = sum(
                backward[mask | (1 << x)]
                for x in range(n)
                if not mask & (1 << x) and not pred[x] & ~mask
            )
    total = forward[full]
    assert total == backward[0] and total > 0
    before = [[0] * n for _ in range(n)]
    for mask in range(size):
        if not forward[mask]:
            continue
        for x in range(n):
            bit = 1 << x
            if mask & bit or pred[x] & ~mask:
                continue
            contribution = forward[mask] * backward[mask | bit]
            remaining = full ^ (mask | bit)
            while remaining:
                ybit = remaining & -remaining
                y = ybit.bit_length() - 1
                before[x][y] += contribution
                remaining ^= ybit
    for x in range(n):
        for y in range(x + 1, n):
            assert before[x][y] + before[y][x] == total
    balanced = sum(
        total <= 3 * before[x][y] <= 2 * total
        for x in range(n) for y in range(x + 1, n)
    )
    comparable = list(pred)
    for y in range(n):
        for x in range(n):
            if pred[y] >> x & 1:
                comparable[x] |= 1 << y
    widths = [0] * size
    for mask in range(1, size):
        bit = mask & -mask
        x = bit.bit_length() - 1
        rest = mask ^ bit
        widths[mask] = max(widths[rest], 1 + widths[rest & ~comparable[x]])
    return widths[full], balanced, total, before


def brute_counts(pred):
    """Independent enumeration of permutations to check the counting DP."""
    n = len(pred)
    before = [[0] * n for _ in range(n)]
    total = 0
    width = 0
    for mask in range(1 << n):
        if all(not pred[x] & mask for x in range(n) if mask >> x & 1):
            width = max(width, mask.bit_count())
    for order in itertools.permutations(range(n)):
        prefix = 0
        for x in order:
            if pred[x] & ~prefix:
                break
            prefix |= 1 << x
        else:
            total += 1
            for i, x in enumerate(order):
                for y in order[i + 1:]:
                    before[x][y] += 1
    return width, total, before


def main():
    seed = 20261028
    rng = random.Random(seed)
    rows = []
    failures = []
    cross_checks = 0
    for n in range(2, 13):
        pairs = list(itertools.combinations(range(n), 2))
        if n <= 6:
            cases = {
                closure(n, (edge for i, edge in enumerate(pairs) if mask >> i & 1))
                for mask in range(1 << len(pairs))
            }
            scope = "all posets up to topological relabeling; duplicates by isomorphism remain"
        else:
            cases = set()
            for attempt in range(120):
                probability = (0.08, 0.15, 0.25, 0.4, 0.65)[attempt % 5]
                cases.add(closure(n, (edge for edge in pairs if rng.random() < probability)))
            scope = "120 seeded forward-DAG samples, deduplicated; not uniform over posets"
        row = {"n": n, "scope": scope, "distinct_cases": len(cases),
               "width_at_least_3_cases": 0, "failures": 0,
               "min_slack_width_at_least_3": None, "tight_witness": None}
        for case_index, pred in enumerate(sorted(cases)):
            width, balanced, total, before = exact_counts(pred)
            if n <= 6 and case_index < 8:
                brute_width, brute_total, brute_before = brute_counts(pred)
                assert (width, total, before) == (brute_width, brute_total, brute_before)
                cross_checks += 1
            slack = balanced - width + 1
            if width >= 3:
                row["width_at_least_3_cases"] += 1
                old = row["min_slack_width_at_least_3"]
                if old is None or slack < old:
                    row["min_slack_width_at_least_3"] = slack
                    row["tight_witness"] = {"predecessor_masks": pred,
                                            "width": width, "balanced_pairs": balanced,
                                            "linear_extensions": total}
            if slack < 0:
                if n <= 8:
                    brute_width, brute_total, brute_before = brute_counts(pred)
                    assert (width, total, before) == (brute_width, brute_total, brute_before)
                    cross_checks += 1
                row["failures"] += 1
                failures.append({"n": n, "predecessor_masks": pred,
                                 "width": width, "balanced_pairs": balanced,
                                 "linear_extensions": total})
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    result = {"date": "2026-10-28", "conjecture": "019 v0.1", "seed": seed,
              "arithmetic": "exact Python integers; probability thresholds by cross multiplication",
              "independent_permutation_cross_checks": cross_checks,
              "rows": rows, "counterexamples": failures,
              "limitation": "Finite verification only. Does not prove 019 or 1/3-2/3 conjecture."}
    destination = Path(__file__).with_name("screen_exact_2026-10-28.json")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved", destination, flush=True)


if __name__ == "__main__":
    main()
