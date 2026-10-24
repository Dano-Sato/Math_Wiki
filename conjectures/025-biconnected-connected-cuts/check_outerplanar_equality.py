"""Exact finite checks for the equality classification in equality.md.

Outerplanarity is tested independently by planarity of the cone graph.
The equality certificate uses only endpoint-deletion connectivity.
"""
from __future__ import annotations

import itertools
import json
import random
from collections import Counter
from pathlib import Path

import networkx as nx


def connected(adjacency: list[int], subset: int) -> bool:
    if not subset:
        return False
    seen = subset & -subset
    frontier = seen
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        added = adjacency[vertex] & subset & ~seen
        seen |= added
        frontier |= added
    return seen == subset


def cycle_order(cycle: nx.Graph) -> list[int]:
    """Read a connected 2-regular graph as a cyclic ordering."""
    assert nx.is_connected(cycle)
    assert all(degree == 2 for _, degree in cycle.degree())
    first = min(cycle)
    order = [first]
    previous, current = first, min(cycle[first])
    while current != first:
        order.append(current)
        following = next(v for v in cycle[current] if v != previous)
        previous, current = current, following
    assert len(order) == len(cycle)
    return order


def crossing_pairs(graph: nx.Graph, order: list[int]) -> list[tuple]:
    position = {v: i for i, v in enumerate(order)}
    result = []
    for edge1, edge2 in itertools.combinations(graph.edges(), 2):
        if len(set(edge1) | set(edge2)) != 4:
            continue
        a, b = sorted(position[v] for v in edge1)
        x, y = sorted(position[v] for v in edge2)
        if (a < x < b < y) or (x < a < y < b):
            result.append((edge1, edge2))
    return result


def check_graph(graph: nx.Graph) -> dict:
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    assert nx.is_biconnected(graph)
    full = (1 << n) - 1
    adjacency = [sum(1 << w for w in graph[v]) for v in range(n)]
    connected_masks = [connected(adjacency, s) for s in range(full + 1)]
    actual = {s for s in range(1, full) if connected_masks[s] and connected_masks[full ^ s]}
    counts = Counter(s.bit_count() for s in actual)
    good_edges = [(u, v) for u, v in graph.edges() if connected_masks[full ^ (1 << u) ^ (1 << v)]]
    good_graph = nx.Graph()
    good_graph.add_nodes_from(graph)
    good_graph.add_edges_from(good_edges)
    assert len(good_edges) == counts[2]
    assert nx.is_biconnected(good_graph)
    cone = graph.copy()
    cone.add_edges_from((n, v) for v in graph)
    is_outerplanar = nx.check_planarity(cone)[0]
    assert (counts[2] == n) == is_outerplanar
    assert all(counts[k] >= n for k in range(1, n))
    assert all(counts[k] == n for k in range(1, n)) == is_outerplanar
    order = None
    if is_outerplanar:
        order = cycle_order(good_graph)
        assert not crossing_pairs(graph, order)
        intervals = {
            sum(1 << order[(start + offset) % n] for offset in range(k))
            for k in range(1, n)
            for start in range(n)
        }
        assert actual == intervals
        for root in graph:
            for k in range(1, n):
                assert sum(s.bit_count() == k and bool(s & (1 << root)) for s in actual) == k
        assert len(actual) // 2 == n * (n - 1) // 2
    else:
        assert counts[2] >= n + 1
    return {"n": n, "outerplanar": is_outerplanar, "b2": counts[2],
            "counts": [counts[k] for k in range(1, n)], "boundary_cycle": order}


def random_outerplanar(n: int, rng: random.Random) -> nx.Graph:
    graph = nx.cycle_graph(n)
    candidates = [(u, v) for u, v in itertools.combinations(range(n), 2) if not graph.has_edge(u, v)]
    rng.shuffle(candidates)
    for u, v in candidates:
        if rng.random() >= 0.65:
            continue
        graph.add_edge(u, v)
        if crossing_pairs(graph, list(range(n))):
            graph.remove_edge(u, v)
    return graph


def random_ear_graph(n: int, rng: random.Random) -> nx.Graph:
    graph = nx.cycle_graph(rng.randint(3, n))
    while len(graph) < n:
        u, v = rng.sample(list(graph), 2)
        r = rng.randint(1, min(3, n - len(graph)))
        interior = list(range(len(graph), len(graph) + r))
        nx.add_path(graph, [u, *interior, v])
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < 0.08:
            graph.add_edge(u, v)
    return graph


def main() -> None:
    seed = 202610240251
    rng = random.Random(seed)
    atlas = Counter()
    samples = Counter()
    checked = 0
    cut_sets = 0
    for graph in nx.graph_atlas_g():
        if len(graph) < 3 or not nx.is_biconnected(graph):
            continue
        result = check_graph(graph)
        atlas[(result["n"], result["outerplanar"])] += 1
        checked += 1
        cut_sets += sum(result["counts"])
    for n in range(8, 13):
        for kind, generator in (("noncrossing_chords", random_outerplanar), ("open_ears", random_ear_graph)):
            for _ in range(20):
                result = check_graph(generator(n, rng))
                samples[(n, kind, result["outerplanar"])] += 1
                checked += 1
                cut_sets += sum(result["counts"])
    diamond = nx.cycle_graph(4)
    diamond.add_edge(0, 2)
    payload = {
        "conjecture": "025", "version": "0.3", "seed": seed,
        "networkx_version": nx.__version__,
        "atlas": [{"n": n, "outerplanar": outer, "graphs": count} for (n, outer), count in sorted(atlas.items())],
        "random_samples": [{"n": n, "kind": kind, "outerplanar": outer, "graphs": count}
                           for (n, kind, outer), count in sorted(samples.items())],
        "graphs_checked": checked,
        "valid_oriented_cut_sets_enumerated": cut_sets,
        "failures": 0,
        "examples": {"cycle_with_one_chord": check_graph(diamond), "K4": check_graph(nx.complete_graph(4)),
                     "K2_3": check_graph(nx.complete_bipartite_graph(2, 3))},
        "checks": ["b2=n iff cone is planar", "all b_k=n iff cone is planar",
                   "good-edge graph is spanning and biconnected",
                   "outerplanar good edges form a noncrossing Hamilton cycle",
                   "outerplanar cuts are exactly cyclic intervals; rooted size-k count is k"],
        "scope": "Finite implementation checks only; general proofs and attribution are in equality.md. "
                 "Atlas is exhaustive on orders 3-7; random samples on orders 8-12 may repeat.",
    }
    Path(__file__).with_name("outerplanar_equality_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("graphs_checked", "valid_oriented_cut_sets_enumerated", "failures", "examples")}, indent=2))


if __name__ == "__main__":
    main()
