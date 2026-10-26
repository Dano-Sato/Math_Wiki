"""Exact targeted search of the k=5 log-concavity inequality, orders 23--40.

Counts zero-sum-free subsets only through size 6, using a recursive subset-sum
bitset search. This is a finite exploratory computation, not a proof outside
the listed groups.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


def invariant_factor_types(max_order: int) -> list[tuple[int, ...]]:
    found: set[tuple[int, ...]] = set()

    def extend(prefix: tuple[int, ...], order: int) -> None:
        if prefix:
            found.add(prefix)
        first = prefix[-1] if prefix else 2
        for factor in range(first, max_order // order + 1):
            if prefix and factor % prefix[-1]:
                continue
            extend(prefix + (factor,), order * factor)

    extend((), 1)
    return sorted(found, key=lambda mods: (math.prod(mods), mods))


def group_counts(mods: tuple[int, ...], max_size: int = 6) -> list[int]:
    all_elements = list(itertools.product(*(range(m) for m in mods)))
    index = {x: i for i, x in enumerate(all_elements)}
    order = len(all_elements)
    zero = index[(0,) * len(mods)]
    nonzero = [i for i in range(order) if i != zero]
    inverse = [
        index[tuple((-v) % m for v, m in zip(x, mods))]
        for x in all_elements
    ]
    addition = [
        [index[tuple((a + b) % m for a, b, m in zip(x, y, mods))]
         for y in all_elements]
        for x in all_elements
    ]
    counts = [0] * (max_size + 1)
    counts[0] = 1

    def translate(subset_sums: int, x: int) -> int:
        translated = 0
        remaining = subset_sums
        while remaining:
            bit = remaining & -remaining
            translated |= 1 << addition[x][bit.bit_length() - 1]
            remaining ^= bit
        return translated

    def visit(start: int, size: int, subset_sums: int) -> None:
        if size == max_size:
            return
        for pos in range(start, len(nonzero)):
            x = nonzero[pos]
            if (subset_sums >> inverse[x]) & 1:
                continue
            next_sums = subset_sums | translate(subset_sums, x)
            next_size = size + 1
            counts[next_size] += 1
            visit(pos + 1, next_size, next_sums)

    visit(0, 0, 1 << zero)
    return counts


def main() -> None:
    records = []
    max_order = 40
    for mods in invariant_factor_types(max_order):
        order = math.prod(mods)
        if not 23 <= order <= max_order:
            continue
        counts = group_counts(mods)
        margin = counts[5] ** 2 - counts[4] * counts[6]
        records.append({
            "invariant_factors": list(mods),
            "group_order": order,
            "z4": counts[4],
            "z5": counts[5],
            "z6": counts[6],
            "k5_margin": margin,
        })

    result = {
        "conjecture": "031",
        "group_order_range": [23, max_order],
        "isomorphism_types_checked": len(records),
        "subset_sizes_counted": [0, 1, 2, 3, 4, 5, 6],
        "all_k5_inequalities_passed": all(r["k5_margin"] >= 0 for r in records),
        "minimum_k5_margin": min(r["k5_margin"] for r in records),
        "groups": records,
        "scope": f"Exact recursive subset-sum enumeration for every finite abelian group of order 23 through {max_order}; no claim outside this finite range.",
    }
    output = Path(__file__).with_name(f"k5-orders-23-{max_order}-experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "group_order_range", "isomorphism_types_checked",
        "all_k5_inequalities_passed", "minimum_k5_margin",
    )}, indent=2))


if __name__ == "__main__":
    main()
