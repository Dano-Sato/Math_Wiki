"""Finite screening for conjecture 073. Requires NetworkX 3.4.2."""
from collections import Counter
import random

import networkx as nx


def connected_subset_counts(graph):
    nodes = list(graph)
    n = len(nodes)
    counts = [0] * (n + 1)
    for mask in range(1, (1 << n) - 1):
        k = mask.bit_count()
        if k < 2:
            continue
        chosen = [nodes[i] for i in range(n) if mask >> i & 1]
        if nx.is_connected(graph.subgraph(chosen)):
            counts[k] += 1
    return counts


def check_graph(graph):
    n = len(graph)
    counts = connected_subset_counts(graph)
    return [(k, counts[k]) for k in range(2, n) if counts[k] < n]


def atlas_screen():
    checked = Counter()
    failures = []
    for graph in nx.graph_atlas_g():
        n = len(graph)
        if n < 3 or n > 7 or not nx.is_biconnected(graph):
            continue
        checked[n] += 1
        failures.extend((n, k, value, sorted(graph.edges()))
                        for k, value in check_graph(graph))
    return checked, failures


def random_screen():
    random.seed(20261027)
    checked = Counter()
    failures = []
    for n in range(8, 11):
        for _ in range(400):
            p = random.uniform(0.2, 0.6)
            graph = nx.gnp_random_graph(n, p, seed=random.randrange(1 << 30))
            if not nx.is_biconnected(graph):
                continue
            checked[n] += 1
            failures.extend((n, k, value, sorted(graph.edges()))
                            for k, value in check_graph(graph))
    return checked, failures


if __name__ == "__main__":
    atlas_counts, atlas_failures = atlas_screen()
    random_counts, random_failures = random_screen()
    print("atlas", dict(atlas_counts), "counterexamples", len(atlas_failures))
    print("random", dict(random_counts), "counterexamples", len(random_failures))
    if atlas_failures or random_failures:
        print("examples", (atlas_failures + random_failures)[:5])
