#!/usr/bin/env python3
"""Exhaustively check connected domination unimodality for labelled graphs n <= 6."""

from itertools import combinations
import json
from pathlib import Path


def is_connected_subset(mask: int, adjacency: list[int]) -> bool:
    seed = mask & -mask
    reached = seed
    frontier = seed
    while frontier:
        newly_reached = 0
        bits = frontier
        while bits:
            bit = bits & -bits
            vertex = bit.bit_length() - 1
            newly_reached |= adjacency[vertex] & mask & ~reached
            bits ^= bit
        frontier = newly_reached
        reached |= newly_reached
    return reached == mask


def is_unimodal(sequence: list[int]) -> bool:
    descending = False
    for left, right in zip(sequence, sequence[1:]):
        if right < left:
            descending = True
        elif descending and right > left:
            return False
    return True


def check_order(n: int) -> tuple[int, dict | None]:
    edges = list(combinations(range(n), 2))
    connected_graphs = 0
    for edge_mask in range(1 << len(edges)):
        adjacency = [0] * n
        for index, (u, v) in enumerate(edges):
            if edge_mask >> index & 1:
                adjacency[u] |= 1 << v
                adjacency[v] |= 1 << u

        if not is_connected_subset((1 << n) - 1, adjacency):
            continue

        counts = [0] * (n + 1)
        for subset in range(1, 1 << n):
            if not is_connected_subset(subset, adjacency):
                continue
            dominated = subset
            bits = subset
            while bits:
                bit = bits & -bits
                dominated |= adjacency[bit.bit_length() - 1]
                bits ^= bit
            if dominated == (1 << n) - 1:
                counts[subset.bit_count()] += 1

        sequence = counts[1:]
        if not is_unimodal(sequence):
            return connected_graphs, {
                "n": n,
                "edge_mask": edge_mask,
                "coefficients": sequence,
            }
        connected_graphs += 1
    return connected_graphs, None


def main() -> None:
    by_order = {}
    counterexample = None
    for n in range(1, 7):
        count, counterexample = check_order(n)
        by_order[str(n)] = count
        if counterexample is not None:
            break

    result = {
        "claim": "connected domination coefficient sequence is unimodal",
        "scope": "all labelled simple connected graphs of each tested order",
        "orders_tested": list(map(int, by_order)),
        "connected_graphs_by_order": by_order,
        "total_connected_graphs": sum(by_order.values()),
        "counterexample": counterexample,
        "method": "direct subset enumeration with exact integer counts",
        "is_proof": False,
    }
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
