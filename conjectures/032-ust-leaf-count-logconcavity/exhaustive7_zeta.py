"""Exhaustively test every labeled graph on 7 vertices via subset zeta transform.

For each leaf count k, store each labeled tree's edge mask in an array. The
subset zeta transform then gives, for every graph edge mask G, the number of
trees with k leaves whose edges are contained in G. Disconnected graphs have
all-zero profiles and do not affect the conjecture.
Requires NumPy for vectorized exact int64 additions.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np


def edge_index(n: int, u: int, v: int) -> int:
    if u > v:
        u, v = v, u
    return u * (2 * n - u - 1) // 2 + (v - u - 1)


def main() -> None:
    n = 7
    edges = list(itertools.combinations(range(n), 2))
    m = len(edges)
    universe = 1 << m
    profiles = np.zeros((n + 1, universe), dtype=np.int64)

    tree_count = 0
    for code in itertools.product(range(n), repeat=n - 2):
        degree = [1] * n
        for v in code:
            degree[v] += 1
        tree_edges = []
        for v in code:
            leaf = next(i for i, d in enumerate(degree) if d == 1)
            tree_edges.append((leaf, v))
            degree[leaf] -= 1
            degree[v] -= 1
        tree_edges.append(tuple(i for i, d in enumerate(degree) if d == 1))
        mask = 0
        degree = [0] * n
        for u, v in tree_edges:
            mask |= 1 << edge_index(n, u, v)
            degree[u] += 1
            degree[v] += 1
        profiles[sum(d == 1 for d in degree), mask] += 1
        tree_count += 1

    for bit in range(m):
        stride = 1 << bit
        blocks = profiles.reshape(n + 1, -1, 2 * stride)
        blocks[:, :, stride:] += blocks[:, :, :stride]

    checked_all_graph_masks = 0
    for k in range(2, n - 1):
        bad = np.flatnonzero(profiles[k] ** 2 < profiles[k - 1] * profiles[k + 1])
        checked_all_graph_masks += universe
        if bad.size:
            mask = int(bad[0])
            result = {
                "n": n,
                "all_labeled_graph_masks": universe,
                "trees_enumerated": tree_count,
                "counterexample_edge_mask": mask,
                "counterexample_edges": [list(e) for i, e in enumerate(edges)
                                         if mask >> i & 1],
                "leaf_coefficients": [int(profiles[j, mask]) for j in range(n + 1)],
                "failed_index": k,
                "all_graph_masks_checked_per_inequality": universe,
            }
            break
    else:
        result = {
            "n": n,
            "all_labeled_graph_masks": universe,
            "trees_enumerated": tree_count,
            "inequality_indices_checked": list(range(2, n - 1)),
            "all_graph_masks_checked_per_inequality": universe,
            "counterexample": None,
            "method": "exact Prüfer enumeration + subset zeta transform; integer arithmetic",
        }
    Path(__file__).with_name("exhaustive7_experiment.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
