"""Exact finite checks for leaf-count log-concavity of spanning trees.

For n <= 6 this checks every connected labeled simple graph. For larger n it
checks seeded random graphs, counting their spanning trees exactly via Prüfer
codes. This is finite evidence only, not a proof.
"""
from __future__ import annotations

import itertools
import json
import random
from pathlib import Path


def spanning_tree_masks(n: int) -> list[tuple[int, int]]:
    """Return (edge-mask, leaf-count) for every labeled tree on [n]."""
    out = []
    for code in itertools.product(range(n), repeat=n - 2):
        degree = [1] * n
        for v in code:
            degree[v] += 1
        edges = []
        for v in code:
            leaf = next(i for i, d in enumerate(degree) if d == 1)
            edges.append((leaf, v))
            degree[leaf] -= 1
            degree[v] -= 1
        edges.append(tuple(i for i, d in enumerate(degree) if d == 1))
        mask = 0
        degree = [0] * n
        for u, v in edges:
            a, b = sorted((u, v))
            mask |= 1 << (a * n + b)
            degree[u] += 1
            degree[v] += 1
        out.append((mask, sum(d == 1 for d in degree)))
    return out


def connected(n: int, mask: int) -> bool:
    seen = 1
    while True:
        expanded = seen
        for u in range(n):
            if seen >> u & 1:
                for v in range(n):
                    if u != v and mask >> (min(u, v) * n + max(u, v)) & 1:
                        expanded |= 1 << v
        if expanded == seen:
            return seen == (1 << n) - 1
        seen = expanded


def coefficients(n: int, graph_mask: int,
                 trees: list[tuple[int, int]]) -> list[int]:
    counts = [0] * (n + 1)
    for tree_mask, leaves in trees:
        if tree_mask & graph_mask == tree_mask:
            counts[leaves] += 1
    return counts


def log_concavity_failure(counts: list[int]) -> list[int]:
    return [k for k in range(1, len(counts) - 1)
            if counts[k] ** 2 < counts[k - 1] * counts[k + 1]]


def exhaustive(n: int) -> dict:
    trees = spanning_tree_masks(n)
    m = n * (n - 1) // 2
    pairs = list(itertools.combinations(range(n), 2))
    checked = 0
    for graph_bits in range(1 << m):
        if graph_bits.bit_count() < n - 1:
            continue
        graph_mask = sum(1 << (u * n + v)
                         for i, (u, v) in enumerate(pairs)
                         if graph_bits >> i & 1)
        if not connected(n, graph_mask):
            continue
        checked += 1
        counts = coefficients(n, graph_mask, trees)
        bad = log_concavity_failure(counts)
        if bad:
            return {"n": n, "checked_connected_graphs": checked,
                    "counterexample_graph_bits": graph_bits,
                    "leaf_counts": counts, "failed_indices": bad}
    return {"n": n, "checked_connected_graphs": checked,
            "spanning_trees_per_graph_universe": len(trees),
            "counterexample": None}


def random_sample(n: int, samples: int, seed: int) -> dict:
    trees = spanning_tree_masks(n)
    pairs = list(itertools.combinations(range(n), 2))
    rng = random.Random(seed)
    checked = 0
    densities = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for _ in range(samples):
        p = rng.choice(densities)
        graph_mask = 0
        for u, v in pairs:
            if rng.random() < p:
                graph_mask |= 1 << (u * n + v)
        if not connected(n, graph_mask):
            continue
        checked += 1
        counts = coefficients(n, graph_mask, trees)
        bad = log_concavity_failure(counts)
        if bad:
            return {"n": n, "generated_graphs": samples,
                    "checked_connected_graphs": checked, "seed": seed,
                    "counterexample_graph_mask": graph_mask,
                    "leaf_counts": counts, "failed_indices": bad}
    return {"n": n, "generated_graphs": samples,
            "checked_connected_graphs": checked, "seed": seed,
            "spanning_trees_per_graph_universe": len(trees),
            "counterexample": None}


def main() -> None:
    result = {
        "method": "exact Prüfer-code enumeration and exact integer inequalities",
        "exhaustive": [exhaustive(n) for n in range(2, 7)],
        "random_samples": [random_sample(7, 1000, 20261024),
                           random_sample(8, 200, 20261025)],
        "warning": "Finite checks do not imply the conjecture for all graphs.",
    }
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
