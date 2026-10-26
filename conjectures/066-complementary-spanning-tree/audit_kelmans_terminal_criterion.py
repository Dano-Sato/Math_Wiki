"""Cross-check the local distance criterion for Kelmans terminal graphs.

Exhausts NetworkX's graph atlas for orders 4 through 7. This is a finite
implementation check, not a classification theorem for arbitrary order.
"""
import json
from pathlib import Path

import networkx as nx
from networkx.generators.atlas import graph_atlas_g


def kelmans(graph, beneficiary, co_beneficiary):
    result = graph.copy()
    for neighbor in list(graph[co_beneficiary]):
        if neighbor != beneficiary and not graph.has_edge(beneficiary, neighbor):
            result.remove_edge(co_beneficiary, neighbor)
            result.add_edge(beneficiary, neighbor)
    return result


def connected_pair(graph):
    return nx.is_connected(graph) and nx.is_connected(nx.complement(graph))


def terminal_by_direct_definition(graph):
    potential = sum(degree * degree for _, degree in graph.degree())
    for beneficiary in graph:
        for co_beneficiary in graph:
            if beneficiary == co_beneficiary:
                continue
            transformed = kelmans(graph, beneficiary, co_beneficiary)
            new_potential = sum(degree * degree for _, degree in transformed.degree())
            if new_potential > potential and connected_pair(transformed):
                return False
    return True


def terminal_by_distance_criterion(graph):
    complement = nx.complement(graph)
    for u in graph:
        for v in graph:
            if u >= v:
                continue
            neighbors_u = set(graph[u]) - {v}
            neighbors_v = set(graph[v]) - {u}
            comparable = neighbors_u <= neighbors_v or neighbors_v <= neighbors_u
            if comparable:
                continue
            if (nx.shortest_path_length(graph, u, v) <= 2
                    and nx.shortest_path_length(complement, u, v) <= 2):
                return False
    return True


result = {"method": "Compare direct admissible Kelmans moves with the derived distance criterion on graph-atlas isomorphism representatives.",
          "orders": {}}
atlas = graph_atlas_g()
for order in range(4, 8):
    graphs = [graph for graph in atlas
              if graph.number_of_nodes() == order and connected_pair(graph)]
    direct = {nx.to_graph6_bytes(graph, header=False).decode().strip()
              for graph in graphs if terminal_by_direct_definition(graph)}
    criterion = {nx.to_graph6_bytes(graph, header=False).decode().strip()
                 for graph in graphs if terminal_by_distance_criterion(graph)}
    if direct != criterion:
        raise AssertionError({"order": order, "direct_only": sorted(direct - criterion),
                              "criterion_only": sorted(criterion - direct)})
    result["orders"][str(order)] = {
        "connected_complementary_isomorphism_classes": len(graphs),
        "terminal_classes": len(direct),
        "graph6_sets_equal": True,
    }

result["limitations"] = [
    "Graph atlas covers these orders only.",
    "The cross-check validates the implementation of the criterion, not its general mathematical proof.",
]
Path(__file__).with_name("kelmans_terminal_criterion_audit.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
