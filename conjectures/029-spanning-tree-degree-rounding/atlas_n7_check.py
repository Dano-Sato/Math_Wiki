"""Exhaustively check the floor/ceiling conjecture on unlabeled 7-vertex graphs.

NetworkX's graph atlas contains one representative of every isomorphism class
of simple graphs through seven vertices. For each connected 7-vertex graph,
this script enumerates every spanning tree and checks the exact degree bounds.
"""

from __future__ import annotations

import json

import networkx as nx


def check_graph(graph: nx.Graph) -> tuple[int, bool]:
    vertices = list(graph.nodes())
    degree_sums = [0] * len(vertices)
    tree_count = 0
    tree_degrees: list[list[int]] = []

    for tree in nx.SpanningTreeIterator(graph):
        degrees = [tree.degree(vertex) for vertex in vertices]
        tree_degrees.append(degrees)
        tree_count += 1
        for index, degree in enumerate(degrees):
            degree_sums[index] += degree

    lower = [degree_sum // tree_count for degree_sum in degree_sums]
    upper = [(degree_sum + tree_count - 1) // tree_count for degree_sum in degree_sums]
    has_witness = any(
        all(lower[i] <= degrees[i] <= upper[i] for i in range(len(vertices)))
        for degrees in tree_degrees
    )
    return tree_count, has_witness


def main() -> None:
    checked = 0
    total_spanning_trees = 0
    counterexamples = []

    for graph in nx.graph_atlas_g():
        if len(graph) != 7 or not nx.is_connected(graph):
            continue
        checked += 1
        tree_count, has_witness = check_graph(graph)
        total_spanning_trees += tree_count
        if not has_witness:
            counterexamples.append(
                {
                    "edges": sorted([list(edge) for edge in graph.edges()]),
                    "spanning_trees": tree_count,
                }
            )

    print(
        json.dumps(
            {
                "vertices": 7,
                "connected_unlabeled_graphs_checked": checked,
                "spanning_trees_enumerated": total_spanning_trees,
                "counterexamples": counterexamples,
                "all_passed": not counterexamples,
                "scope_note": "Finite check over NetworkX graph atlas representatives only.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
