"""Exact finite check of the k=4 inequality for group orders 30 through 34."""

from __future__ import annotations

import json
import math
from pathlib import Path

from check_k3_k4_small import (
    elements,
)

TYPES = [
    (30,), (31,),
    (2, 2, 2, 2, 2), (2, 2, 2, 4), (2, 2, 8), (2, 16), (32,),
    (33,), (34,),
]

def count_free_through_five(mods: tuple[int, ...]) -> dict[int, int]:
    all_elements = elements(mods)
    element_index = {element: i for i, element in enumerate(all_elements)}
    size = len(all_elements)
    addition = [
        [
            element_index[tuple((a + b) % m for a, b, m in zip(x, y, mods))]
            for y in all_elements
        ]
        for x in all_elements
    ]
    nonzero = [i for i, element in enumerate(all_elements) if any(element)]
    inverse = [
        element_index[tuple((-v) % m for v, m in zip(element, mods))]
        for element in all_elements
    ]
    counts = [0] * 6
    counts[0] = 1

    def translate(subset_sums: int, x: int) -> int:
        translated = 0
        remaining = subset_sums
        while remaining:
            bit = remaining & -remaining
            total = bit.bit_length() - 1
            translated |= 1 << addition[x][total]
            remaining ^= bit
        return translated

    def extend(start: int, k: int, subset_sums: int) -> None:
        if k == 5:
            return
        for position in range(start, len(nonzero)):
            x = nonzero[position]
            if (subset_sums >> inverse[x]) & 1:
                continue
            next_sums = subset_sums | translate(subset_sums, x)
            next_k = k + 1
            counts[next_k] += 1
            extend(position + 1, next_k, next_sums)

    extend(0, 0, 1)
    return {k: counts[k] for k in (3, 4, 5)}


def main() -> None:
    records = []
    for mods in TYPES:
        order = math.prod(mods)
        counts = count_free_through_five(mods)
        margin = counts[4] ** 2 - counts[3] * counts[5]
        assert margin >= 0, (mods, margin)
        records.append({
            "invariant_factors": list(mods),
            "group_order": order,
            "z3": counts[3],
            "z4": counts[4],
            "z5": counts[5],
            "k4_margin": margin,
        })

    found = [(record["group_order"], tuple(record["invariant_factors"])) for record in records]
    assert len(found) == len(TYPES) and set(found) == {
        (math.prod(mods), mods) for mods in TYPES
    }, found
    result = {
        "group_orders_checked": [30, 31, 32, 33, 34],
        "isomorphism_types_checked": len(records),
        "all_k4_inequalities_passed": True,
        "groups": records,
        "scope": "Exact enumeration of 3-, 4-, and 5-element subsets for all finite abelian groups of orders 30 through 34.",
    }
    output = Path(__file__).with_name("k4-orders-30-34-experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "isomorphism_types_checked": len(records),
        "all_k4_inequalities_passed": True,
        "minimum_k4_margin": min(record["k4_margin"] for record in records),
        "output": output.name,
    }, indent=2))


if __name__ == "__main__":
    main()
