"""Exact finite check for Conjecture 031; no third-party dependencies."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


def invariant_factor_types(max_order: int) -> list[tuple[int, ...]]:
    """Canonical invariant-factor presentations of finite abelian groups."""
    found: set[tuple[int, ...]] = set()
    for length in range(1, max_order.bit_length() + 1):
        for mods in itertools.product(range(2, max_order + 1), repeat=length):
            order = math.prod(mods)
            if order > max_order:
                continue
            if all(mods[i + 1] % mods[i] == 0 for i in range(length - 1)):
                found.add(mods)
    return sorted(found, key=lambda mods: (math.prod(mods), mods))


def elements(mods: tuple[int, ...]) -> list[tuple[int, ...]]:
    return list(itertools.product(*(range(m) for m in mods)))


def add(a: tuple[int, ...], b: tuple[int, ...], mods: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((x + y) % m for x, y, m in zip(a, b, mods))


def zero_sum_free_counts(mods: tuple[int, ...]) -> tuple[list[int], int]:
    """Enumerate all subsets of A\{0}; return z_k and checked subset count."""
    zero = (0,) * len(mods)
    nonzero = [x for x in elements(mods) if x != zero]
    counts = [0] * (len(nonzero) + 1)

    for mask in range(1 << len(nonzero)):
        sums = {zero}  # sums of all subsets of the selected elements
        is_zero_sum_free = True
        for i, x in enumerate(nonzero):
            if not (mask >> i) & 1:
                continue
            old_sums = tuple(sums)
            inverse_x = tuple((-v) % m for v, m in zip(x, mods))
            if inverse_x in sums:
                is_zero_sum_free = False
                break
            sums.update(add(s, x, mods) for s in old_sums)
        if is_zero_sum_free:
            counts[mask.bit_count()] += 1
    return counts, 1 << len(nonzero)


def log_concavity_violations(counts: list[int]) -> list[dict[str, int]]:
    return [
        {"k": k, "left": counts[k] ** 2, "right": counts[k - 1] * counts[k + 1]}
        for k in range(1, len(counts) - 1)
        if counts[k] ** 2 < counts[k - 1] * counts[k + 1]
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-order", type=int, default=16)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("experiment.json"))
    args = parser.parse_args()

    records = []
    total_subsets = 0
    for mods in invariant_factor_types(args.max_order):
        counts, checked = zero_sum_free_counts(mods)
        violations = log_concavity_violations(counts)
        records.append({
            "invariant_factors": list(mods),
            "group_order": math.prod(mods),
            "zero_sum_free_subset_counts_by_size": counts,
            "log_concavity_violations": violations,
            "all_inequalities_passed": not violations,
            "subsets_checked": checked,
        })
        total_subsets += checked

    result = {
        "conjecture": "For every finite abelian group A, the number z_k(A) of k-element zero-sum-free subsets of A\\{0} is log-concave in k.",
        "method": "Exact enumeration of every subset of A\\{0}; incremental subset-sum sets; canonical invariant-factor types.",
        "max_group_order": args.max_order,
        "isomorphism_types_checked": len(records),
        "subsets_checked": total_subsets,
        "all_groups_passed": all(r["all_inequalities_passed"] for r in records),
        "groups": records,
        "interpretation": "Finite exact computation only; it proves no universal statement beyond the listed groups.",
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("max_group_order", "isomorphism_types_checked", "subsets_checked", "all_groups_passed")}, indent=2))


if __name__ == "__main__":
    main()
