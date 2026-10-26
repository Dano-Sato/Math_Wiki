"""Exact finite audit of product strictness under admissible Kelmans moves.

Uses the graph atlas for orders 4 through 7 and exact spanning-tree counts.
This does not prove strictness in general.
"""
import json
from pathlib import Path

import networkx as nx
from networkx.generators.atlas import graph_atlas_g

from claude_kelmans_audit import both_connected, kelmans, sq, tau, g6


result = {
    "method": "Enumerate all ordered Kelmans moves with strict degree-square increase that preserve connectivity of graph and complement; compute tree counts by exact Bareiss determinants.",
    "orders": {},
}
for order in range(4, 8):
    graphs = [graph for graph in graph_atlas_g()
              if graph.number_of_nodes() == order and both_connected(graph)]
    admissible_moves = 0
    graph_count_equal_moves = 0
    complement_count_equal_moves = 0
    both_equal_moves = 0
    samples = {"graph_count_equal": None, "complement_count_equal": None}
    for graph in graphs:
        graph_trees = tau(graph)
        complement = nx.complement(graph)
        complement_trees = tau(complement)
        for beneficiary in graph:
            for co_beneficiary in graph:
                if beneficiary == co_beneficiary:
                    continue
                transformed = kelmans(graph, beneficiary, co_beneficiary)
                if sq(transformed) <= sq(graph) or not both_connected(transformed):
                    continue
                admissible_moves += 1
                transformed_trees = tau(transformed)
                transformed_complement_trees = tau(nx.complement(transformed))
                graph_equal = transformed_trees == graph_trees
                complement_equal = transformed_complement_trees == complement_trees
                if transformed_trees * transformed_complement_trees > graph_trees * complement_trees:
                    raise AssertionError({"order": order, "graph6": g6(graph),
                                          "beneficiary": beneficiary,
                                          "co_beneficiary": co_beneficiary})
                if graph_equal:
                    graph_count_equal_moves += 1
                    if samples["graph_count_equal"] is None:
                        samples["graph_count_equal"] = {
                            "graph6": g6(graph), "beneficiary": beneficiary,
                            "co_beneficiary": co_beneficiary,
                        }
                if complement_equal:
                    complement_count_equal_moves += 1
                    if samples["complement_count_equal"] is None:
                        samples["complement_count_equal"] = {
                            "graph6": g6(graph), "beneficiary": beneficiary,
                            "co_beneficiary": co_beneficiary,
                        }
                if graph_equal and complement_equal:
                    both_equal_moves += 1
    result["orders"][str(order)] = {
        "connected_complementary_isomorphism_classes": len(graphs),
        "admissible_strict_potential_moves": admissible_moves,
        "graph_tree_count_equal_moves": graph_count_equal_moves,
        "complement_tree_count_equal_moves": complement_count_equal_moves,
        "both_tree_counts_equal_moves": both_equal_moves,
        "samples": samples,
    }

result["limitations"] = [
    "The enumeration covers graph-atlas representatives for orders 4 through 7 only.",
    "The standard Kelmans theorem gives nonincrease of each tree count; the finite audit does not prove that at least one count strictly decreases in every admissible move for arbitrary order.",
]
Path(__file__).with_name("kelmans_product_strictness_audit.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
