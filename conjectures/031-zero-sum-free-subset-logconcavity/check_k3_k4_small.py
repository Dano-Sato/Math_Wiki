"""Targeted exact checks of the k=3 and k=4 inequalities through order 29.

    Unlike explore.py, this enumerates only 2- through 5-element subsets, which makes
the finite range useful as the small-order complement to a general bound.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


def invariant_factor_types(max_order: int) -> list[tuple[int, ...]]:
    found: set[tuple[int, ...]] = set()
    for length in range(1, max_order.bit_length() + 1):
        for mods in itertools.product(range(2, max_order + 1), repeat=length):
            if math.prod(mods) <= max_order and all(
                mods[i + 1] % mods[i] == 0 for i in range(length - 1)
            ):
                found.add(mods)
    return sorted(found, key=lambda mods: (math.prod(mods), mods))


def elements(mods: tuple[int, ...]) -> list[tuple[int, ...]]:
    return list(itertools.product(*(range(m) for m in mods)))


def add(a: tuple[int, ...], b: tuple[int, ...], mods: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((x + y) % m for x, y, m in zip(a, b, mods))


def zero_sum_free(subset: tuple[tuple[int, ...], ...], mods: tuple[int, ...]) -> bool:
    zero = (0,) * len(mods)
    sums = {zero}
    for x in subset:
        inverse = tuple((-v) % m for v, m in zip(x, mods))
        if inverse in sums:
            return False
        old_sums = tuple(sums)
        sums.update(add(s, x, mods) for s in old_sums)
    return True


def main() -> None:
    max_order = 29
    records = []
    for mods in invariant_factor_types(max_order):
        nonzero = [x for x in elements(mods) if any(x)]
        z2 = sum(zero_sum_free(s, mods) for s in itertools.combinations(nonzero, 2))
        z3 = sum(zero_sum_free(s, mods) for s in itertools.combinations(nonzero, 3))
        z4 = sum(zero_sum_free(s, mods) for s in itertools.combinations(nonzero, 4))
        z5 = sum(zero_sum_free(s, mods) for s in itertools.combinations(nonzero, 5))
        m = len(nonzero)
        tau = sum(all((2 * x) % mod == 0 for x, mod in zip(a, mods))
                   for a in nonzero)
        z2_formula = (m * m - 2 * m + tau) // 2
        if z2 != z2_formula:
            raise AssertionError(f"z2 formula mismatch for invariant factors {mods}")
        records.append({
            "invariant_factors": list(mods),
            "group_order": math.prod(mods),
            "z2": z2,
            "z3": z3,
            "z4": z4,
            "z5": z5,
            "k3_margin": z3 * z3 - z2 * z4,
            "k4_margin": z4 * z4 - z3 * z5,
        })

    result = {
        "max_group_order": max_order,
        "isomorphism_types_checked": len(records),
        "subset_sizes_enumerated": [2, 3, 4, 5],
        "all_k3_inequalities_passed": all(r["k3_margin"] >= 0 for r in records),
        "minimum_k3_margin": min(r["k3_margin"] for r in records),
        "all_k4_inequalities_passed": all(r["k4_margin"] >= 0 for r in records),
        "minimum_k4_margin": min(r["k4_margin"] for r in records),
        "groups": records,
        "scope": "Exact enumeration of 3- and 4-element subsets for every nontrivial finite abelian group of order at most 29.",
    }
    output = Path(__file__).with_name("k3-small-experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "max_group_order", "isomorphism_types_checked",
        "all_k3_inequalities_passed", "minimum_k3_margin",
        "all_k4_inequalities_passed", "minimum_k4_margin",
    )}, indent=2))


if __name__ == "__main__":
    main()
