"""Check the Hamiltonian strict bound and the cut-preserving edge reduction.

All graph cut families are enumerated exactly; no universal conclusion is
inferred from the finite search. See single_size_equality.md for proofs.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import itertools
import json
from pathlib import Path
import random

import networkx as nx

from check_outerplanar_equality import connected, crossing_pairs, random_ear_graph


def cut_family(graph: nx.Graph) -> set[int]:
    n = len(graph)
    full = (1 << n) - 1
    adjacency = [sum(1 << w for w in graph[v]) for v in range(n)]
    conn = [connected(adjacency, s) for s in range(full + 1)]
    return {s for s in range(1, full) if conn[s] and conn[full ^ s]}


def hamilton_cycle(graph: nx.Graph) -> list[int] | None:
    """Exact search; a None result exhausts all possible rooted Hamilton cycles."""
    n = len(graph)
    full = (1 << n) - 1
    start = min(graph, key=lambda v: (graph.degree(v), v))
    neighbors = {v: sorted(graph[v], key=lambda w: (graph.degree(w), w)) for v in graph}

    @lru_cache(None)
    def extend(last: int, visited: int) -> tuple[int, ...] | None:
        if visited == full:
            return () if graph.has_edge(last, start) else None
        for following in neighbors[last]:
            if visited & (1 << following):
                continue
            suffix = extend(following, visited | (1 << following))
            if suffix is not None:
                return (following, *suffix)
        return None

    suffix = extend(start, 1 << start)
    return None if suffix is None else [start, *suffix]


def coefficients(lengths: list[int]) -> list[int]:
    row = [1]
    for length in lengths:
        nxt = [0] * (len(row) + length)
        for i, value in enumerate(row):
            for j in range(length + 1):
                nxt[i + j] += value
        row = nxt
    return row


def crossed_chord_certificate(graph: nx.Graph, order: list[int], pair: tuple) -> dict:
    n = len(graph)
    position = {v: i for i, v in enumerate(order)}
    a, b, c, d = sorted(position[v] for edge in pair for v in edge)
    assert {frozenset(edge) for edge in pair} == {
        frozenset((order[a], order[c])), frozenset((order[b], order[d]))}
    lengths = [b - a - 1, c - b - 1, d - c - 1, n - d + a - 1]
    q = coefficients(lengths)
    assert sum(lengths) == n - 4 and all(value >= 1 for value in q)
    assert q == q[::-1]
    base = nx.Graph()
    base.add_nodes_from(range(n))
    nx.add_cycle(base, order)
    base.add_edges_from(pair)
    actual = cut_family(base)
    full = (1 << n) - 1
    intervals = {
        sum(1 << order[(start + j) % n] for j in range(k))
        for k in range(1, n) for start in range(n)
    }
    arcs = [order[a + 1:b], order[b + 1:c], order[c + 1:d], order[d + 1:] + order[:a]]
    extras = set()
    for choices in itertools.product(*(range(length + 1) for length in lengths)):
        selected = {order[a], order[c]}
        for index, (arc, take) in enumerate(zip(arcs, choices)):
            if index % 2 == 0:
                selected.update(arc[:take])
            elif take:
                selected.update(arc[-take:])
        mask = sum(1 << v for v in selected)
        extras.update((mask, full ^ mask))
    assert not intervals & extras
    assert actual == intervals | extras
    counts = Counter(s.bit_count() for s in actual)
    assert counts[1] == counts[n - 1] == n
    assert all(counts[k] == n + 2 * q[k - 2] for k in range(2, n - 1))
    return {"cycle": order, "chords": pair, "arc_internal_sizes": lengths,
            "q": q, "counts": [counts[k] for k in range(1, n)]}


def check_graph(graph: nx.Graph) -> dict:
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    assert nx.is_biconnected(graph)
    actual = cut_family(graph)
    counts = Counter(s.bit_count() for s in actual)
    good = nx.Graph()
    good.add_nodes_from(range(n))
    good.add_edges_from((u, v) for u, v in graph.edges() if ((1 << u) | (1 << v)) in actual)
    assert nx.is_biconnected(good)
    assert cut_family(good) == actual
    order = hamilton_cycle(graph)
    certificate = None
    if order is not None:
        pairs = crossing_pairs(graph, order)
        if pairs:
            certificate = crossed_chord_certificate(graph, order, pairs[0])
            assert all(counts[k] >= n + 2 for k in range(2, n - 1))
        else:
            assert all(counts[k] == n for k in range(1, n))
    cone = graph.copy()
    cone.add_edges_from((n, v) for v in graph)
    outer = nx.check_planarity(cone)[0]
    if not outer:
        assert all(counts[k] >= n + 1 for k in (2, n - 2))
    equal_middle = [k for k in range(3, n - 2) if not outer and counts[k] == n]
    for k in range(2, n - 1):
        if counts[k] != n:
            continue
        row = [s for s in actual if s.bit_count() == k]
        assert all(sum(bool(s & (1 << v)) for s in row) == k for v in graph)
        for u, v in good.edges():
            patterns = Counter((bool(s & (1 << u)), bool(s & (1 << v))) for s in row)
            assert patterns == {(True, True): k - 1, (True, False): 1,
                                (False, True): 1, (False, False): n - k - 1}
    return {"n": n, "hamiltonian": order is not None, "outerplanar": outer,
            "counts": [counts[k] for k in range(1, n)], "crossed_chord_certificate": certificate,
            "single_middle_equalities": equal_middle,
            "edges_removed_without_changing_cut_family": len(graph.edges()) - len(good.edges())}


def main() -> None:
    seed = 202610240252
    rng = random.Random(seed)
    categories = Counter()
    certificate_count = 0
    pruning_edges = 0
    graph_count = 0
    examples = {}
    open_question_counterexamples = []

    def record(graph: nx.Graph, source: str) -> dict:
        nonlocal certificate_count, pruning_edges, graph_count
        result = check_graph(graph)
        categories[(source, result["n"], result["hamiltonian"], result["outerplanar"])] += 1
        certificate_count += result["crossed_chord_certificate"] is not None
        pruning_edges += result["edges_removed_without_changing_cut_family"]
        graph_count += 1
        if result["single_middle_equalities"]:
            open_question_counterexamples.append({"source": source, "n": len(graph),
                "edges": list(graph.edges()), "equal_middle_sizes": result["single_middle_equalities"]})
        return result

    for graph in nx.graph_atlas_g():
        if len(graph) >= 3 and nx.is_biconnected(graph):
            record(graph, "atlas")
    for n in range(8, 14):
        for _ in range(20):
            graph = nx.cycle_graph(n)
            for u, v in itertools.combinations(range(n), 2):
                if rng.random() < 0.12:
                    graph.add_edge(u, v)
            record(graph, "random_hamilton_cycle_with_chords")
            record(random_ear_graph(n, rng), "random_open_ears")
    # Sharpness family: K4 with one edge subdivided n-4 times.
    for n in range(4, 15):
        graph = nx.cycle_graph(n)
        graph.add_edges_from(((0, 2), (1, 3)))
        result = record(graph, "sharp_crossed_chords")
        assert result["counts"] == [n] + [n + 2] * (n - 3) + [n]
        if n in (4, 8, 14):
            examples[f"sharp_n{n}"] = result
    examples["Petersen"] = record(nx.petersen_graph(), "structured_nonhamiltonian")
    assert not examples["Petersen"]["hamiltonian"]
    for m in range(3, 12):
        result = record(nx.complete_bipartite_graph(2, m), "structured_nonhamiltonian")
        assert not result["hamiltonian"]
    payload = {
        "conjecture": "025", "version": "0.4", "networkx_version": nx.__version__, "seed": seed,
        "graphs_checked": graph_count, "crossed_chord_certificates_checked": certificate_count,
        "pruned_edge_instances": pruning_edges, "cut_family_reduction_failures": 0,
        "nonouterplanar_single_middle_equality_counterexamples_found": len(open_question_counterexamples),
        "open_question_counterexamples": open_question_counterexamples,
        "categories": [{"source": source, "n": n, "hamiltonian": ham, "outerplanar": outer, "graphs": count}
                       for (source, n, ham, outer), count in sorted(categories.items())],
        "examples": examples,
        "scope": "Finite exact checks. The Hamiltonian strict bound, sharpness, and edge reduction "
                 "have general proofs in single_size_equality.md. For non-Hamiltonian graphs the single-size "
                 "equality implication remains unresolved; absence of finite counterexamples is not a proof. "
                 "Random samples may repeat.",
    }
    Path(__file__).with_name("single_size_equality_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("graphs_checked", "crossed_chord_certificates_checked",
                                            "pruned_edge_instances", "nonouterplanar_single_middle_equality_counterexamples_found")}, indent=2))
    print(json.dumps({"Petersen_counts": examples["Petersen"]["counts"]}))


if __name__ == "__main__":
    main()
