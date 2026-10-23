"""Exhaustively test leaf counts and root-excluded leaf counts on 7 vertices.

For each tree, store both its total leaf count and its leaf count excluding
root 0. The subset zeta transform then gives both distributions for every
graph edge mask. A failure in the root-excluded distribution yields an
ordinary counterexample by attaching a new pendant vertex at root 0.
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
    profiles = np.zeros((2, n + 1, universe), dtype=np.int64)

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
        leaves = sum(d == 1 for d in degree)
        profiles[0, leaves, mask] += 1
        profiles[1, leaves - int(degree[0] == 1), mask] += 1
        tree_count += 1

    for bit in range(m):
        stride = 1 << bit
        blocks = profiles.reshape(2, n + 1, -1, 2 * stride)
        blocks[:, :, :, stride:] += blocks[:, :, :, :stride]

    root_failure = None
    for k in range(2, n - 1):
        bad = np.flatnonzero(profiles[0, k] ** 2 < profiles[0, k - 1] * profiles[0, k + 1])
        if bad.size:
            mask = int(bad[0])
            result = {
                "n": n,
                "all_labeled_graph_masks": universe,
                "trees_enumerated": tree_count,
                "counterexample_edge_mask": mask,
                "counterexample_edges": [list(e) for i, e in enumerate(edges)
                                         if mask >> i & 1],
                "leaf_coefficients": [int(profiles[0, j, mask]) for j in range(n + 1)],
                "failed_index": k,
                "all_graph_masks_checked_per_inequality": universe,
            }
            break
    else:
        result = {"counterexample": None}

    for k in range(1, n - 1):
        bad = np.flatnonzero(profiles[1, k] ** 2 < profiles[1, k - 1] * profiles[1, k + 1])
        if bad.size:
            mask = int(bad[0])
            root_failure = {
                "n": n,
                "root": 0,
                "counterexample_edge_mask": mask,
                "counterexample_edges": [list(e) for i, e in enumerate(edges)
                                         if mask >> i & 1],
                "root_excluded_leaf_coefficients": [
                    int(profiles[1, j, mask]) for j in range(n + 1)],
                "failed_index": k,
                "pendant_extension_edges": [
                    *[list(e) for i, e in enumerate(edges) if mask >> i & 1], [0, n]],
                "extended_graph_leaf_coefficients": [
                    0, *[int(profiles[1, j, mask]) for j in range(n + 1)]],
            }
            break

    result.update({
        "n": n,
        "all_labeled_graph_masks": universe,
        "trees_enumerated": tree_count,
        "inequality_indices_checked": list(range(2, n - 1)),
        "all_graph_masks_checked_per_inequality": universe,
        "root_excluded_inequality_indices_checked": list(range(1, n - 1)),
        "root_excluded_counterexample": root_failure,
        "method": "exact Prüfer enumeration + subset zeta transform; integer arithmetic",
        "scope": "Every labeled graph on 7 vertices; a root-excluded failure extends to a graph on 8 vertices by adding one pendant vertex.",
    })
    Path(__file__).with_name("exhaustive7_experiment.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
