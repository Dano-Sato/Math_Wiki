"""Exact finite checks for conjecture 049; requires NetworkX 3.x.

Counts nonempty connected vertex sets and computes their lower median size.
All outputs are finite checks, not a proof of the conjecture.
"""

from math import gcd

import networkx as nx
from networkx.algorithms import isomorphism


def connected_set_counts(graph):
    n = graph.number_of_nodes()
    counts = [0] * n
    vertices = list(graph.nodes())
    for mask in range(1, 1 << n):
        chosen = [vertices[i] for i in range(n) if mask & (1 << i)]
        if len(chosen) == 1 or nx.is_connected(graph.subgraph(chosen)):
            counts[len(chosen) - 1] += 1
    return counts


def lower_median(counts):
    total = sum(counts)
    cumulative = 0
    for size, count in enumerate(counts, start=1):
        cumulative += count
        if 2 * cumulative >= total:
            return size
    raise ValueError("The connected-set list must be nonempty.")


def is_vertex_transitive(graph):
    matcher = isomorphism.GraphMatcher(graph, graph)
    root = next(iter(graph))
    return {mapping[root] for mapping in matcher.isomorphisms_iter()} == set(graph)


def check(graph, label):
    if not nx.is_connected(graph) or not is_vertex_transitive(graph):
        raise ValueError(f"{label} must be connected and vertex-transitive.")
    counts = connected_set_counts(graph)
    median = lower_median(counts)
    return label, graph.number_of_nodes(), counts, median


def atlas_examples():
    checked = []
    for graph in nx.graph_atlas_g():
        if (graph.number_of_nodes() > 0 and nx.is_connected(graph)
                and is_vertex_transitive(graph)):
            counts = connected_set_counts(graph)
            checked.append((graph.number_of_nodes(), counts,
                            lower_median(counts)))
    return checked


def circulant_graph(n, steps):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for vertex in range(n):
        for step in steps:
            graph.add_edge(vertex, (vertex + step) % n)
    return graph


def circulant_examples():
    checked = []
    for n in range(3, 13):
        representatives = list(range(1, (n + 1) // 2 + 1))
        for mask in range(1, 1 << len(representatives)):
            steps = {representatives[i] for i in range(len(representatives))
                     if mask & (1 << i)}
            if any(n - step in steps for step in steps if 2 * step != n):
                continue
            if gcd(n, *steps) != 1:
                continue
            graph = circulant_graph(n, steps)
            counts = connected_set_counts(graph)
            checked.append((n, sorted(steps), counts,
                            lower_median(counts)))
    return checked


def named_examples():
    graphs = [
        ("Q3", nx.hypercube_graph(3)),
        ("Q4", nx.hypercube_graph(4)),
        ("Petersen", nx.petersen_graph()),
        ("K4,4", nx.complete_bipartite_graph(4, 4)),
        ("L(K4)", nx.line_graph(nx.complete_graph(4))),
    ]
    return [check(graph, label) for label, graph in graphs]


def summarize(label, examples, order_index=0):
    failures = [(example, example[-1]) for example in examples
                if example[-1] < (example[order_index] + 1) // 2]
    print(f"{label}: checked={len(examples)}, failures={len(failures)}")
    for failure in failures[:5]:
        print("  counterexample:", failure)


if __name__ == "__main__":
    print("NetworkX", nx.__version__)
    atlas = atlas_examples()
    circulants = circulant_examples()
    named = named_examples()
    summarize("atlas", atlas)
    summarize("circulants", circulants)
    summarize("named", named, order_index=1)
