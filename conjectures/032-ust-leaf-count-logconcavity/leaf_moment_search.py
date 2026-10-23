"""Exact leaf-count distributions from induced-subgraph tree counts.

If S is required to be contained in the leaf set, deleting S leaves a tree
on V\\S; each s in S chooses one neighbor there. Thus the number of trees
with S contained in their leaves is tau(G[V\\S])*prod(deg_{G[V\\S]}(s)).
Binomial-moment inversion recovers the exact leaf-count coefficients.
"""
from __future__ import annotations

import itertools
import json
import random
from pathlib import Path


def determinant_bareiss(matrix: list[list[int]]) -> int:
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0:
        return 1
    sign, previous = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if a[r][k]), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator // previous
        for i in range(k + 1, n):
            a[i][k] = 0
        previous = pivot
    return sign * a[n - 1][n - 1]


def tree_count(graph: list[list[int]], vertices: tuple[int, ...]) -> int:
    if len(vertices) <= 1:
        return 1
    root = vertices[-1]
    cofactor = []
    for u in vertices[:-1]:
        row = []
        for v in vertices[:-1]:
            if u == v:
                row.append(sum(graph[u][w] for w in vertices if w != u))
            else:
                row.append(-graph[u][v])
        cofactor.append(row)
    return determinant_bareiss(cofactor)


def coefficients(graph: list[list[int]]) -> list[int]:
    n = len(graph)
    if n == 2:
        return [0, 0, graph[0][1]]
    total = [0] * (n + 1)
    for leaf_mask in range(1 << n):
        leaves = tuple(i for i in range(n) if leaf_mask >> i & 1)
        core = tuple(i for i in range(n) if not (leaf_mask >> i & 1))
        if not core:
            continue
        tau = tree_count(graph, core)
        if tau == 0:
            continue
        ways = tau
        for v in leaves:
            ways *= sum(graph[v][u] for u in core)
        total[len(leaves)] += ways
    # total[j] = sum_T binom(number_of_leaves(T), j).
    exact = [0] * (n + 1)
    for k in range(n + 1):
        exact[k] = sum(((-1) ** (j - k)) * __import__("math").comb(j, k) * total[j]
                        for j in range(k, n + 1))
    assert all(x >= 0 for x in exact)
    return exact


def connected(graph: list[list[int]]) -> bool:
    n = len(graph)
    seen = {0}
    todo = [0]
    while todo:
        u = todo.pop()
        for v, edge in enumerate(graph[u]):
            if edge and v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == n


def failures(a: list[int]) -> list[int]:
    return [k for k in range(1, len(a) - 1) if a[k] ** 2 < a[k - 1] * a[k + 1]]


def graph_from_edges(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    g = [[0] * n for _ in range(n)]
    for u, v in edges:
        g[u][v] = g[v][u] = 1
    return g


def random_search(n: int, tries: int, seed: int) -> dict:
    rng = random.Random(seed)
    pairs = list(itertools.combinations(range(n), 2))
    checked = 0
    ps = [0.15, 0.2, 0.25, 0.35, 0.5, 0.7, 0.9]
    for _ in range(tries):
        p = rng.choice(ps)
        g = graph_from_edges(n, [(u, v) for u, v in pairs if rng.random() < p])
        if not connected(g):
            continue
        checked += 1
        a = coefficients(g)
        bad = failures(a)
        if bad:
            return {"n": n, "generated": tries, "connected_checked": checked,
                    "p_set": ps, "seed": seed, "counterexample_edges": [
                        [u, v] for u, v in pairs if g[u][v]],
                    "coefficients": a, "failed_indices": bad}
    return {"n": n, "generated": tries, "connected_checked": checked,
            "p_set": ps, "seed": seed, "counterexample": None}


def cross_check() -> dict:
    """Compare the moment formula against Prüfer counts for all graphs n<=5."""
    from explore import spanning_tree_masks, coefficients as prufer_coefficients
    checked = 0
    for n in range(2, 6):
        pairs = list(itertools.combinations(range(n), 2))
        trees = spanning_tree_masks(n)
        for bits in range(1 << len(pairs)):
            edges = [edge for i, edge in enumerate(pairs) if bits >> i & 1]
            g = graph_from_edges(n, edges)
            if not connected(g):
                continue
            mask = sum(1 << (u * n + v) for u, v in edges)
            assert coefficients(g) == prufer_coefficients(n, mask, trees)
            checked += 1
    return {"graphs_cross_checked": checked, "passed": True}


def main() -> None:
    result = {
        "method": "induced-subgraph matrix-tree determinants + exact binomial-moment inversion",
        "formula_cross_check": cross_check(),
        "random_search": [random_search(9, 300, 20261026),
                          random_search(10, 100, 20261027),
                          random_search(12, 30, 20261028)],
        "warning": "These are exact counts on finite samples, not a general proof.",
    }
    path = Path(__file__).with_name("leaf_moment_experiment.json")
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
