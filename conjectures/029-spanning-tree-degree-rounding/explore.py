"""Exact finite check for rounding UST expected degrees by one."""

from itertools import product
import json
from pathlib import Path
import random


def tree_catalog(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    index = {e: k for k, e in enumerate(pairs)}
    catalog = []
    for code in product(range(n), repeat=max(0, n - 2)):
        deg = [1] * n
        for x in code:
            deg[x] += 1
        work = deg[:]
        edges = 0
        for x in code:
            leaf = next(i for i, d in enumerate(work) if d == 1)
            a, b = sorted((leaf, x))
            edges |= 1 << index[(a, b)]
            work[leaf] -= 1
            work[x] -= 1
        leaves = [i for i, d in enumerate(work) if d == 1]
        a, b = leaves
        edges |= 1 << index[tuple(sorted((a, b)))]
        catalog.append((edges, tuple(deg)))
    return pairs, catalog


def check_graph(n, graph, trees):
    valid = [(mask, deg) for mask, deg in trees if mask & graph == mask]
    if not valid:
        return None
    count = len(valid)
    sums = [sum(deg[v] for _, deg in valid) for v in range(n)]
    rounded = any(all(abs(count * deg[v] - sums[v]) <= count for v in range(n))
                  for _, deg in valid)
    if not rounded:
        return {"n": n, "graph_mask": graph, "spanning_trees": count,
                "mean_degrees": [x / count for x in sums]}
    return True


def check_order(n):
    pairs, trees = tree_catalog(n)
    total_graphs = 1 << len(pairs)
    checked = 0
    for graph in range(total_graphs):
        result = check_graph(n, graph, trees)
        if result is None:
            continue
        checked += 1
        if result is not True:
            return {"n": n, "connected_graphs_checked_before_counterexample": checked,
                    "all_have_tree_with_each_degree_within_1_of_uniform_mean": False,
                    "counterexample": result}
    return {"n": n, "connected_graphs_checked": checked,
            "all_have_tree_with_each_degree_within_1_of_uniform_mean": True,
            "counterexample": None}


def sample_order(n, samples, seed):
    pairs, trees = tree_catalog(n)
    rng = random.Random(seed)
    connected = 0
    attempts = 0
    while connected < samples:
        p = rng.uniform(0.2, 0.8)
        graph = sum((1 << k) for k in range(len(pairs)) if rng.random() < p)
        attempts += 1
        result = check_graph(n, graph, trees)
        if result is None:
            continue
        connected += 1
        if result is not True:
            return {"n": n, "connected_graphs_checked": connected,
                    "attempts": attempts, "counterexample": result}
    return {"n": n, "connected_graphs_checked": connected,
            "attempts": attempts, "counterexample": None}


def main():
    results = [check_order(n) for n in range(2, 7)]
    random_samples = [sample_order(7, 500, 2907), sample_order(8, 100, 2908)]
    data = {
        "conjecture": "Every finite connected simple graph has a spanning tree T with |deg_T(v)-E[deg_UST(v)]|<=1 for every vertex v.",
        "method": "Enumerate all labelled simple graphs for each n=2..6; generate spanning trees by Prüfer codes and compute exact rational means.",
        "results": results,
        "random_graph_samples": random_samples,
        "scope": "Finite exact enumeration only; it proves nothing for n>=7.",
    }
    Path(__file__).with_name("experiment.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
