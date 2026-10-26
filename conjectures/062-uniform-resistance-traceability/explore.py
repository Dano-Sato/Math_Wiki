"""Preliminary checks for 062. Run with ``python explore.py``.

The T34 graph6 datum comes from Agrahari et al.'s companion repository:
https://github.com/Gyagr7/Effective-Resistance-Curvature-Graph-Properties/blob/main/examples.py
"""

from fractions import Fraction

import networkx as nx
import numpy as np
from sympy import Matrix


T34_GRAPH6 = (
    "aUYA@CPAG??A?A?B??o?O?C_?@G?@G???C??@??O??B???G???H???C_O?@G?"
    "?????C????O?O???Go??C?_????H???@@G"
)


def means_float(graph):
    laplacian = nx.laplacian_matrix(graph).toarray()
    pinv = np.linalg.pinv(laplacian)
    return {
        v: sum(pinv[v, v] + pinv[w, w] - 2 * pinv[v, w] for w in graph[v])
        for v in graph
    }


def has_hamilton_path(graph):
    vertices = list(graph)
    neighbors = [sum(1 << j for j, w in enumerate(vertices) if graph.has_edge(v, w))
                 for v in vertices]
    reachable = {1 << v: 1 << v for v in range(len(vertices))}
    for subset in range(1, 1 << len(vertices)):
        ends = reachable.get(subset, 0)
        for v in range(len(vertices)):
            if ends & (1 << v):
                available = neighbors[v] & ~subset
                while available:
                    bit = available & -available
                    reachable[subset | bit] = reachable.get(subset | bit, 0) | bit
                    available ^= bit
    return bool(reachable.get((1 << len(vertices)) - 1, 0))


def exact_means(graph):
    n = len(graph)
    reduced = Matrix(nx.laplacian_matrix(graph).toarray()[:n - 1, :n - 1].tolist())
    inverse = reduced.inv()

    def resistance(v, w):
        if v == n - 1:
            return inverse[w, w]
        if w == n - 1:
            return inverse[v, v]
        return inverse[v, v] + inverse[w, w] - 2 * inverse[v, w]

    means = {v: sum(resistance(v, w) for w in graph[v]) for v in graph}
    return means


def t34_exact_means():
    graph = nx.from_graph6_bytes(T34_GRAPH6.encode("ascii"))
    return graph, exact_means(graph)


def h_m_graph(m):
    """K_m on b_i together with the internally disjoint paths a-x_i-b_i."""
    graph = nx.complete_graph(m)
    b = list(range(m))
    a = m
    x = list(range(m + 1, 2 * m + 1))
    graph.add_edges_from((a, x_i) for x_i in x)
    graph.add_edges_from((x[i], b[i]) for i in range(m))
    return graph, a, b, x


if __name__ == "__main__":
    atlas = [g for g in nx.graph_atlas_g() if len(g) >= 2 and nx.is_connected(g)]
    antecedent = [g for g in atlas if max(means_float(g).values()) < 2 - 1e-9]
    violations = [g for g in antecedent if not has_hamilton_path(g)]
    print(f"atlas_connected_n2_to_7={len(atlas)} antecedent={len(antecedent)} violations={len(violations)}")
    graph, means = t34_exact_means()
    print(f"T34_n={len(graph)} edges={graph.number_of_edges()} max_mean={max(means.values())}")
    print("T34_vertices_attaining_max=", [v for v, x in means.items() if x == max(means.values())])
    for m in range(3, 9):
        graph, a, b, x = h_m_graph(m)
        means = exact_means(graph)
        predicted = {
            a: Fraction(m * (m + 2), 2 * m + 1),
            b[0]: Fraction(5 * m - 2, 2 * m + 1),
            x[0]: Fraction(2 * (m + 2), 2 * m + 1),
        }
        assert all(means[v] == value for v, value in predicted.items())
        print(f"H_{m}_mu_a={means[a]} mu_b={means[b[0]]} mu_x={means[x[0]]} "
              f"traceable={has_hamilton_path(graph)}")
