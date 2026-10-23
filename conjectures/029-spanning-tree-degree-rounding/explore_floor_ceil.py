"""Exact checks for floor/ceiling rounding of UST mean degrees."""

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
            edges |= 1 << index[tuple(sorted((leaf, x)))]
            work[leaf] -= 1
            work[x] -= 1
        leaves = [i for i, d in enumerate(work) if d == 1]
        edges |= 1 << index[tuple(sorted(leaves))]
        catalog.append((edges, tuple(deg)))
    return pairs, catalog


def check_graph(n, graph, trees):
    valid = [degrees for mask, degrees in trees if mask & graph == mask]
    if not valid:
        return None
    count = len(valid)
    sums = [sum(degrees[v] for degrees in valid) for v in range(n)]

    # d is in {floor(mean), ceil(mean)} iff count*d lies between
    # floor(sum/count)*count and ceil(sum/count)*count.
    def rounds(v, degree):
        return sums[v] // count <= degree <= (sums[v] + count - 1) // count

    if any(all(rounds(v, degrees[v]) for v in range(n)) for degrees in valid):
        return True
    return {"n": n, "spanning_trees": count,
            "mean_degree_numerators": sums, "mean_degree_denominator": count}


def exhaustive(n):
    pairs, trees = tree_catalog(n)
    checked = 0
    for graph in range(1 << len(pairs)):
        result = check_graph(n, graph, trees)
        if result is None:
            continue
        checked += 1
        if result is not True:
            result["connected_graphs_checked_before_counterexample"] = checked
            return {"n": n, "all_pass": False, "counterexample": result}
    return {"n": n, "all_pass": True, "connected_graphs_checked": checked}


def sample(n, samples, seed):
    pairs, trees = tree_catalog(n)
    rng = random.Random(seed)
    checked = attempts = 0
    while checked < samples:
        p = rng.uniform(0.2, 0.8)
        graph = sum(1 << k for k in range(len(pairs)) if rng.random() < p)
        attempts += 1
        result = check_graph(n, graph, trees)
        if result is None:
            continue
        checked += 1
        if result is not True:
            result["connected_graphs_checked"] = checked
            result["attempts"] = attempts
            return {"n": n, "all_pass": False, "counterexample": result}
    return {"n": n, "all_pass": True, "connected_graphs_checked": checked,
            "attempts": attempts, "seed": seed}


def main():
    data = {
        "claim": "A spanning tree has every vertex degree in the floor/ceiling of the UST expected degree.",
        "method": "Exact spanning-tree enumeration with integer cross multiplication; all labeled connected simple graphs for n=2..6, then seeded random connected graphs for n=7,8.",
        "exhaustive": [exhaustive(n) for n in range(2, 7)],
        "random_samples": [sample(7, 2000, 2941), sample(8, 500, 2942)],
        "scope": "Finite checks only; they do not establish the claim for arbitrary n.",
    }
    Path(__file__).with_name("floor_ceil_experiment.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
