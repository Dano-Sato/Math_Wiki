"""Finite exploration of spectral-radius monotonic tails under uniform subdivision."""

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np


MAX_ORDER = 6
MAX_STRETCH = 16
TOLERANCE = 1e-9


def uniform_stretch(graph: nx.Graph, length: int) -> nx.Graph:
    """Replace every edge by a path of the requested length."""
    stretched = nx.Graph()
    stretched.add_nodes_from(("v", vertex) for vertex in graph.nodes())
    for edge_index, (u, v) in enumerate(graph.edges()):
        path = [("v", u)]
        path.extend(("i", edge_index, j) for j in range(1, length))
        path.append(("v", v))
        stretched.add_edges_from(zip(path, path[1:]))
    return stretched


def spectral_radius(graph: nx.Graph) -> float:
    adjacency = nx.to_numpy_array(graph, dtype=float)
    return float(np.linalg.eigvalsh(adjacency)[-1])


def monotone_tail_index(values: list[float]) -> tuple[int, str] | None:
    """Return the first index of a monotone tail with at least three samples."""
    for start in range(max(0, len(values) - 2)):
        tail = values[start:]
        nondecreasing = all(
            tail[i + 1] >= tail[i] - TOLERANCE for i in range(len(tail) - 1)
        )
        nonincreasing = all(
            tail[i + 1] <= tail[i] + TOLERANCE for i in range(len(tail) - 1)
        )
        if nondecreasing or nonincreasing:
            if nondecreasing and nonincreasing:
                direction = "constant"
            elif nondecreasing:
                direction = "nondecreasing"
            else:
                direction = "nonincreasing"
            return start, direction
    return None


counts_by_order: dict[int, int] = defaultdict(int)
max_tail_position = 0
observed_graphs = 0
all_passed = True
sample_nonmonotone = None

for graph in nx.graph_atlas_g():
    order = graph.number_of_nodes()
    if order < 2 or order > MAX_ORDER or not nx.is_connected(graph):
        continue

    values = [
        spectral_radius(uniform_stretch(graph, length))
        for length in range(1, MAX_STRETCH + 1)
    ]
    observed_graphs += 1
    counts_by_order[order] += 1

    if sample_nonmonotone is None and any(
        values[i + 1] < values[i] - TOLERANCE
        and values[i + 2] > values[i + 1] + TOLERANCE
        for i in range(len(values) - 2)
    ):
        sample_nonmonotone = {
            "order": order,
            "edges": sorted([list(edge) for edge in graph.edges()]),
            "rho_t_for_t_1_through_8": values[:8],
        }

    for parity in (0, 1):
        parity_values = [
            values[length - 1]
            for length in range(1, MAX_STRETCH + 1)
            if length % 2 == parity
        ]
        result = monotone_tail_index(parity_values)
        if result is None:
            all_passed = False
        else:
            max_tail_position = max(max_tail_position, result[0])

payload = {
    "method": "NetworkX graph atlas, all non-isomorphic connected simple graphs of orders 2 through 6; dense symmetric adjacency eigensolver",
    "orders_checked": dict(sorted((str(k), v) for k, v in counts_by_order.items())),
    "graphs_checked": observed_graphs,
    "max_edge_path_length": MAX_STRETCH,
    "parity_tail_rule": "each finite parity sequence must have a monotone tail of at least three values",
    "floating_point_tolerance": TOLERANCE,
    "all_graphs_passed_finite_tail_check": all_passed,
    "largest_observed_tail_start_index_within_parity_sequence": max_tail_position,
    "example_of_nonmonotonicity_across_all_t": sample_nonmonotone,
    "interpretation": "finite numerical evidence only; it does not prove eventual monotonicity for any graph"
}

Path(__file__).with_name("experiment.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(payload, indent=2))

