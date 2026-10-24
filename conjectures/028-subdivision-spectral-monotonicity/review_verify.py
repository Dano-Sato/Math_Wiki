"""Check the algebra used in the v0.2 proof; these checks are not the proof.

Run from the repository root:
    python conjectures/028-subdivision-spectral-monotonicity/review_verify.py
Requires SymPy, NetworkX and NumPy, as does the existing exploration environment.
"""

import json
from pathlib import Path

import networkx as nx
import numpy as np
import sympy as sp


def stretch(graph, length):
    result = nx.Graph()
    result.add_nodes_from(graph.nodes())
    next_vertex = graph.number_of_nodes()
    for u, v in graph.edges():
        path = [u, *range(next_vertex, next_vertex + length - 1), v]
        next_vertex += length - 1
        result.add_edges_from(zip(path, path[1:]))
    return result


def path_polynomial(length, variable):
    """h_0=0, h_1=1, h_(t+1)=variable*h_t-h_(t-1)."""
    previous, current = sp.Integer(0), sp.Integer(1)
    if length == 0:
        return previous
    for _ in range(1, length):
        previous, current = current, sp.expand(variable * current - previous)
    return current


def exact_checks():
    lam, q, z, degree = sp.symbols("lambda q z d")
    identity_checks = 0
    for length in range(1, 9):
        ht = path_polynomial(length, lam).subs(lam, q + 1 / q)
        hp = path_polynomial(length - 1, lam).subs(lam, q + 1 / q)
        factor = (q - 1 / q) * q ** (1 - length)
        expected_diagonal = q**2 + 1 - degree + z**2 * ((degree - 1) * q**2 - 1)
        expected_off_diagonal = -(q**2 - 1) * z
        assert sp.cancel(
            factor * ((q + 1 / q) * ht - degree * hp)
            - expected_diagonal.subs(z, q ** (-length))
        ) == 0
        assert sp.cancel(-factor - expected_off_diagonal.subs(z, q ** (-length))) == 0
        identity_checks += 2

    triangle_leaf = nx.Graph([(0, 1), (1, 2), (2, 0), (0, 3)])
    examples = {
        "isolated_vertex": nx.empty_graph(1),
        "edge": nx.path_graph(2),
        "path_4": nx.path_graph(4),
        "cycle_3": nx.cycle_graph(3),
        "star_3": nx.star_graph(3),
        "triangle_leaf": triangle_leaf,
        "complete_4": nx.complete_graph(4),
    }
    charpoly_checks = 0
    for graph in examples.values():
        adjacency = sp.Matrix(nx.to_numpy_array(graph, dtype=int))
        degrees = sp.diag(*[graph.degree(v) for v in graph.nodes()])
        n, m = graph.number_of_nodes(), graph.number_of_edges()
        for length in range(1, 6):
            ht = path_polynomial(length, lam)
            hp = path_polynomial(length - 1, lam)
            reduced = lam * ht * sp.eye(n) - hp * degrees - adjacency
            subdivided_adjacency = sp.Matrix(nx.to_numpy_array(stretch(graph, length), dtype=int))
            actual = subdivided_adjacency.charpoly(lam).as_expr()
            # Avoid negative powers when m<n.
            left = actual * ht ** max(n - m, 0)
            right = reduced.det() * ht ** max(m - n, 0)
            assert sp.expand(left - right) == 0
            charpoly_checks += 1

    adjacency = sp.Matrix(nx.to_numpy_array(triangle_leaf, dtype=int))
    diagonal = sp.diag(*[
        q**2 + 1 - triangle_leaf.degree(v)
        + z**2 * ((triangle_leaf.degree(v) - 1) * q**2 - 1)
        for v in triangle_leaf.nodes()
    ])
    polynomial = sp.factor((diagonal - (q**2 - 1) * z * adjacency).det())
    # Unique maximum-degree vertex: the branch at sqrt(2) is analytic.
    assert sp.simplify(polynomial.subs({q: sp.sqrt(2), z: 0})) == 0
    assert sp.simplify(sp.diff(polynomial, q).subs({q: sp.sqrt(2), z: 0})) != 0
    assert sp.simplify(sp.diff(polynomial, z).subs({q: sp.sqrt(2), z: 0})) == 0
    c = sp.symbols("c")
    leading_equation = sp.expand(polynomial.subs(q, sp.sqrt(2) + c * z**2)).coeff(z, 2)
    leading_coefficient = sp.solve(leading_equation, c)[0]
    assert sp.simplify(leading_coefficient + 1 / (4 * sp.sqrt(2))) == 0
    return {
        "symbolic_path_identities": identity_checks,
        "exact_characteristic_polynomial_checks": charpoly_checks,
        "example_names": list(examples),
        "lengths_for_exact_charpoly_checks": [1, 5],
        "triangle_leaf_polynomial_P_q_z": str(polynomial),
        "triangle_leaf_simple_root_and_zero_linear_term_checked": True,
        "triangle_leaf_branch_q_minus_sqrt2_leading_coefficient_of_z_squared": str(leading_coefficient),
        "triangle_leaf_rho_minus_3_over_sqrt2_asymptotic": "-1/(8*sqrt(2)) * 2**(-t)",
    }


def numerical_checks():
    cases = 0
    eigenpairs_checked = 0
    largest_residual = 0.0
    triangle_leaf_values = []
    triangle_leaf = nx.Graph([(0, 1), (1, 2), (2, 0), (0, 3)])
    for graph in nx.graph_atlas_g():
        n = graph.number_of_nodes()
        if not 2 <= n <= 6 or not nx.is_connected(graph):
            continue
        adjacency = nx.to_numpy_array(graph, dtype=float)
        degrees = np.array([graph.degree(v) for v in graph.nodes()])
        for length in range(1, 9):
            full = nx.to_numpy_array(stretch(graph, length), dtype=float)
            eigenvalues, eigenvectors = np.linalg.eigh(full)
            for index, value in enumerate(eigenvalues):
                if value <= 2 + 1e-7:
                    continue
                q = (value + np.sqrt(value * value - 4)) / 2
                z = q ** (-length)
                diagonal = q*q + 1 - degrees + z*z * ((degrees - 1)*q*q - 1)
                reduced = np.diag(diagonal) - (q*q - 1)*z*adjacency
                endpoint_vector = eigenvectors[:n, index]
                relative_residual = np.linalg.norm(reduced @ endpoint_vector) / (
                    np.linalg.norm(reduced) * np.linalg.norm(endpoint_vector)
                )
                largest_residual = max(largest_residual, float(relative_residual))
                eigenpairs_checked += 1
            cases += 1
    for length in range(1, 25):
        value = np.linalg.eigvalsh(nx.to_numpy_array(stretch(triangle_leaf, length)))[-1]
        triangle_leaf_values.append(float(value))
    assert largest_residual < 1e-10
    return {
        "atlas_orders": [2, 6],
        "edge_lengths": [1, 8],
        "graph_length_cases": cases,
        "all_eigenpairs_above_2_checked": eigenpairs_checked,
        "maximum_relative_reduced_matrix_residual": largest_residual,
        "residual_threshold": 1e-10,
        "triangle_leaf_edges": sorted([list(e) for e in triangle_leaf.edges()]),
        "triangle_leaf_rho_t_1_through_24": triangle_leaf_values,
        "interpretation": "Floating-point checks of the reduction, not certificates of eventual monotonicity.",
    }


def main():
    result = {
        "date": "2026-10-24",
        "proof_version": "0.2",
        "exact": exact_checks(),
        "numerical": numerical_checks(),
        "scope": "The general theorem is proved in conjectures.md using convergence and Newton-Puiseux, not inferred from this finite computation.",
    }
    output = Path(__file__).with_name("review_2026-10-24.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
