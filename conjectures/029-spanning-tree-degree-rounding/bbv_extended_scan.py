"""Inspect UST mean-degree thresholds in the BBV nontraceable family.

This is a numerical experiment; it does not prove the general conjecture.
"""

import argparse
import itertools
import json
import math

import networkx as nx

from claude_ust_lib import mu, window_tree


def graph(ell: int) -> nx.Graph:
    m = 2 * ell + 3
    base_edges = [
        ("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"),
        ("t", "a"), ("t", "b"), ("w", "d"), ("w", "c"),
        ("u", "a"), ("u", "d"), ("v", "b"), ("v", "c"),
    ]
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from(((i, a), (i, b)) for a, b in base_edges)
    ends = [(i, side) for i in range(m) for side in ("u", "v")]
    g.add_edges_from(itertools.combinations(ends, 2))
    hubs = [("T", i) for i in range(ell)]
    g.add_edges_from(itertools.combinations(hubs, 2))
    g.add_edges_from((h, v) for h in hubs for v in list(g) if v not in hubs)
    return nx.convert_node_labels_to_integers(g, label_attribute="orig")


def scan(ell: int, feasible: bool) -> dict:
    g = graph(ell)
    means = mu(g)
    roles: dict[str, list[float]] = {}
    for v, attrs in g.nodes(data=True):
        orig = attrs["orig"]
        role = "T" if orig[0] == "T" else orig[1]
        roles.setdefault(role, []).append(float(means[v]))
    result = {
        "ell": ell,
        "m": 2 * ell + 3,
        "vertices": len(g),
        "edges": g.number_of_edges(),
        "roles": {
            role: {"min": min(vals), "max": max(vals)}
            for role, vals in sorted(roles.items())
        },
        "near_integer_distance": min(abs(x - round(x)) for x in means.values()),
    }
    if feasible:
        result["rounding_feasibility"] = window_tree(g, means)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ells", nargs="*", type=int, default=[8, 10, 12, 16])
    parser.add_argument("--feasible", action="store_true")
    args = parser.parse_args()
    for ell in args.ells:
        print(json.dumps(scan(ell, args.feasible), ensure_ascii=False), flush=True)
