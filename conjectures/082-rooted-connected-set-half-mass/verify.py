"""Exact finite checks for conjecture 082. Requires NetworkX."""

from __future__ import annotations

import json
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path

import networkx as nx


def local_counts(graph: nx.Graph) -> list[tuple[int, int]]:
    """Return (large, total) rooted-set counts for every vertex.

    A set is large when its order is at least ceil(|V|/2). Connectivity is
    checked by bit-mask flood fill on the induced subgraph.
    """
    nodes = sorted(graph.nodes())
    n = len(nodes)
    index = {v: i for i, v in enumerate(nodes)}
    neighbors = [0] * n
    for u, v in graph.edges():
        i, j = index[u], index[v]
        neighbors[i] |= 1 << j
        neighbors[j] |= 1 << i

    totals = [0] * n
    large_counts = [0] * n
    threshold = (n + 1) // 2

    for mask in range(1, 1 << n):
        reached = mask & -mask
        while True:
            expanded = reached
            frontier = reached
            while frontier:
                bit = frontier & -frontier
                i = bit.bit_length() - 1
                expanded |= neighbors[i] & mask
                frontier -= bit
            if expanded == reached:
                break
            reached = expanded
        if reached != mask:
            continue

        is_large = mask.bit_count() >= threshold
        vertices = mask
        while vertices:
            bit = vertices & -vertices
            i = bit.bit_length() - 1
            totals[i] += 1
            if is_large:
                large_counts[i] += 1
            vertices -= bit

    return list(zip(large_counts, totals))


def check_graph(graph: nx.Graph) -> tuple[bool, Fraction]:
    counts = local_counts(graph)
    ratios = [Fraction(large, total) for large, total in counts]
    return all(2 * large >= total for large, total in counts), min(ratios)


def main() -> None:
    atlas_counts: Counter[int] = Counter()
    atlas_vertices_checked = 0
    atlas_failures = 0
    atlas_min_ratio = Fraction(1, 1)

    for graph in nx.graph_atlas_g():
        n = graph.number_of_nodes()
        if n == 0 or not nx.is_connected(graph):
            continue
        atlas_counts[n] += 1
        atlas_vertices_checked += n
        passed, min_ratio = check_graph(graph)
        atlas_failures += not passed
        atlas_min_ratio = min(atlas_min_ratio, min_ratio)

    rng = random.Random(20261027)
    probabilities = [0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.85]
    random_graphs_checked = 0
    random_vertices_checked = 0
    random_failures = 0
    random_min_ratio = Fraction(1, 1)
    for n in range(8, 13):
        for _ in range(80):
            p = rng.choice(probabilities)
            graph = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
            if not nx.is_connected(graph):
                continue
            random_graphs_checked += 1
            random_vertices_checked += n
            passed, min_ratio = check_graph(graph)
            random_failures += not passed
            random_min_ratio = min(random_min_ratio, min_ratio)

    result = {
        "statement_scope": "all connected simple graphs and every root vertex",
        "threshold": "at least half of rooted connected vertex sets have size >= ceil(n/2)",
        "atlas": {
            "connected_graphs_by_order": dict(sorted(atlas_counts.items())),
            "graphs_checked": sum(atlas_counts.values()),
            "root_vertices_checked": atlas_vertices_checked,
            "failures": atlas_failures,
            "minimum_observed_large_fraction": str(atlas_min_ratio),
        },
        "random_sample": {
            "seed": 20261027,
            "orders": [8, 12],
            "attempts_per_order": 80,
            "connected_graphs_checked": random_graphs_checked,
            "root_vertices_checked": random_vertices_checked,
            "failures": random_failures,
            "minimum_observed_large_fraction": str(random_min_ratio),
        },
        "scope_warning": "These finite checks do not prove the universal conjecture.",
    }
    output = Path(__file__).with_name("verification.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
