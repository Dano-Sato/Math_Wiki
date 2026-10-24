"""Construct k distinct rooted size-k connected bipartitions.

This implements the induction in proof.md, independently of counting all cuts.
The finite checks validate the implementation; the general proof is textual.
Requires NetworkX. Run from any directory; output stays beside this script.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import networkx as nx


def st_order(graph: nx.Graph, source: int, target: int) -> list[int]:
    """Ear insertion gives source first, target last, and two-sided neighbors."""
    assert graph.has_edge(source, target)
    without_edge = graph.copy()
    without_edge.remove_edge(source, target)
    order = nx.shortest_path(without_edge, source, target)
    while len(order) < len(graph):
        remaining = set(graph) - set(order)
        component = next(iter(nx.connected_components(graph.subgraph(remaining))))
        attachments = [v for v in order if any(w in component for w in graph[v])]
        assert len(attachments) >= 2
        first, last = attachments[0], attachments[-1]
        x = next(w for w in graph[first] if w in component)
        y = next(w for w in graph[last] if w in component)
        interior = nx.shortest_path(graph.subgraph(component), x, y)
        position = order.index(first) + 1
        order[position:position] = interior
    positions = {v: i for i, v in enumerate(order)}
    assert order[0] == source and order[-1] == target
    for v in order[1:-1]:
        assert any(positions[w] < positions[v] for w in graph[v])
        assert any(positions[w] > positions[v] for w in graph[v])
    return order


def rooted_witnesses(graph: nx.Graph, root: int) -> dict[int, set[frozenset[int]]]:
    """For every 1 <= k < n, return exactly k distinct valid sets containing root."""
    n = len(graph)
    assert n >= 3 and nx.is_biconnected(graph)
    if n == 3:
        return {
            k: {frozenset(s) for s in itertools.combinations(graph, k) if root in s}
            for k in (1, 2)
        }
    neighbor = next(iter(graph[root]))
    order = st_order(graph, root, neighbor)
    partner = order[1]
    assert graph.has_edge(root, partner)
    assert nx.is_connected(graph.subgraph(set(graph) - {root, partner}))
    contracted = nx.contracted_nodes(graph, root, partner, self_loops=False)
    assert nx.is_biconnected(contracted)
    smaller = rooted_witnesses(contracted, root)
    separating_order = st_order(graph, root, partner)
    witnesses = {1: {frozenset({root})}}
    for k in range(2, n):
        lifted = {subset | {partner} for subset in smaller[k - 1]}
        extra = frozenset(separating_order[:k])
        assert partner not in extra and extra not in lifted
        witnesses[k] = lifted | {extra}
    return witnesses


def validate_graph(graph: nx.Graph) -> tuple[int, int]:
    """Check constructed witnesses against independent exhaustive subset enumeration."""
    vertices = set(graph)
    n = len(graph)
    exact = {
        k: {
            frozenset(subset)
            for subset in itertools.combinations(graph, k)
            if nx.is_connected(graph.subgraph(subset))
            and nx.is_connected(graph.subgraph(vertices - set(subset)))
        }
        for k in range(1, n)
    }
    assert all(len(family) >= n for family in exact.values())
    cases = total_witnesses = 0
    for root in graph:
        constructed = rooted_witnesses(graph, root)
        for k, family in constructed.items():
            assert len(family) == k
            assert family <= exact[k]
            assert all(root in subset and len(subset) == k for subset in family)
            cases += 1
            total_witnesses += len(family)
    return cases, total_witnesses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--random-per-order", type=int, default=20)
    parser.add_argument("--max-random-order", type=int, default=12)
    args = parser.parse_args()
    assert args.random_per_order >= 0 and args.max_random_order >= 8
    seed = 20261024025
    rng = random.Random(seed)
    atlas_by_order: Counter[int] = Counter()
    random_by_order: Counter[int] = Counter()
    cases = total_witnesses = 0
    for graph in nx.graph_atlas_g():
        if len(graph) < 3 or not nx.is_biconnected(graph):
            continue
        new_cases, new_witnesses = validate_graph(graph)
        cases += new_cases
        total_witnesses += new_witnesses
        atlas_by_order[len(graph)] += 1
    for n in range(8, args.max_random_order + 1):
        for _ in range(args.random_per_order):
            # Growing open ears makes sparse, generally non-Hamiltonian examples.
            initial = rng.randint(3, n)
            graph = nx.cycle_graph(initial)
            while len(graph) < n:
                endpoints = rng.sample(list(graph), 2)
                length = rng.randint(1, min(3, n - len(graph)))
                interior = list(range(len(graph), len(graph) + length))
                nx.add_path(graph, [endpoints[0], *interior, endpoints[1]])
            for u, v in itertools.combinations(range(n), 2):
                if rng.random() < 0.05:
                    graph.add_edge(u, v)
            new_cases, new_witnesses = validate_graph(graph)
            cases += new_cases
            total_witnesses += new_witnesses
            random_by_order[n] += 1
    payload = {
        "conjecture": "025",
        "proof": "proof.md; st-ordering and rooted edge-contraction induction",
        "networkx_version": nx.__version__,
        "seed": seed,
        "atlas_graphs_by_order": dict(sorted(atlas_by_order.items())),
        "random_ear_graphs_by_order": dict(sorted(random_by_order.items())),
        "root_size_cases": cases,
        "constructed_witnesses_checked": total_witnesses,
        "failures": 0,
        "scope": "Finite implementation check, not a replacement for the general proof. "
        "All subsets independently enumerated for each graph; every root and size tested. "
        "Random samples may repeat and are not all isomorphism classes.",
    }
    output = Path(__file__).with_name("construct_rooted_cuts_result.json")
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
