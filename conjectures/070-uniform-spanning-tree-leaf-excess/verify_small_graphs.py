"""Exact verification of Conjecture 070 for all connected labeled graphs n<=6.

Enumerate labeled spanning trees by Prüfer codes. Every graph containing a
given tree is obtained by adding an arbitrary subset of the remaining edges,
so accumulating over these supergraphs counts every connected graph exactly.
The conjectured inequality is checked with integer arithmetic.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path


def connected_graph_counts(n: int) -> dict[str, int | bool]:
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edge_index = [[-1] * n for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        edge_index[u][v] = edge_index[v][u] = i

    graph_count = 1 << len(edges)
    all_edges = graph_count - 1
    tree_counts = [0] * graph_count
    leaf_totals = [0] * graph_count

    for code in itertools.product(range(n), repeat=max(0, n - 2)):
        degrees = [1] * n
        for vertex in code:
            degrees[vertex] += 1

        tree_mask = 0
        for vertex in code:
            leaf = next(i for i, degree in enumerate(degrees) if degree == 1)
            tree_mask |= 1 << edge_index[leaf][vertex]
            degrees[leaf] -= 1
            degrees[vertex] -= 1
        remaining = [i for i, degree in enumerate(degrees) if degree == 1]
        tree_mask |= 1 << edge_index[remaining[0]][remaining[1]]
        leaves = sum(1 for degree in [1 + code.count(i) for i in range(n)] if degree == 1)

        optional_edges = all_edges ^ tree_mask
        added = optional_edges
        while True:
            graph_mask = tree_mask | added
            tree_counts[graph_mask] += 1
            leaf_totals[graph_mask] += leaves
            if added == 0:
                break
            added = (added - 1) & optional_edges

    connected = 0
    minimum_slack: int | None = None
    equality_graphs = 0
    for mask, tau in enumerate(tree_counts):
        if tau == 0:
            continue
        edge_count = mask.bit_count()
        excess = max(0, edge_count - n)
        slack = 2 * n * leaf_totals[mask] - (4 * n + excess) * tau
        connected += 1
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
        equality_graphs += slack == 0

    return {
        "vertices": n,
        "connected_labeled_graphs_checked": connected,
        "all_inequalities_passed": minimum_slack is not None and minimum_slack >= 0,
        "minimum_integer_slack": minimum_slack,
        "equality_labeled_graphs": equality_graphs,
    }


def main() -> None:
    result = {
        "conjecture": "070",
        "verification": "exact Prüfer-code and supergraph-mask enumeration",
        "scope": "all connected labeled simple graphs with 2 through 6 vertices",
        "orders": [connected_graph_counts(n) for n in range(2, 7)],
        "general_proof": False,
    }
    path = Path(__file__).with_name("experiment.json")
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
