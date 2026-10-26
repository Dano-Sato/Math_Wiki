"""Seeded exact scan of random 2-trees for conjecture 029.

This is a finite experiment, not a proof. Means are computed exactly as
rational numbers and candidate spanning trees are searched with the existing
degree-window backtracker.
"""

import json
import random
from pathlib import Path

import networkx as nx

from claude_search import check


def random_2tree(rng, n):
    # Start from K3, then repeatedly attach a new vertex to both ends of a
    # uniformly selected existing edge. Every generated graph is 2-connected.
    graph = nx.complete_graph(3)
    edges = list(graph.edges())
    for v in range(3, n):
        u, w = rng.choice(edges)
        graph.add_edge(v, u)
        graph.add_edge(v, w)
        edges.extend(((v, u), (v, w)))
    return nx.convert_node_labels_to_integers(graph)


def main():
    rng = random.Random(20261027)
    cases = []
    seen = set()
    for n in range(8, 14):
        accepted = 0
        attempts = 0
        while accepted < 40 and attempts < 400:
            attempts += 1
            graph = random_2tree(rng, n)
            key = tuple(sorted(tuple(sorted(e)) for e in graph.edges()))
            if key in seen:
                continue
            seen.add(key)
            result, nodes, mu, tau = check(graph, node_limit=2_000_000)
            status = "pass" if result not in (None, "timeout") else str(result)
            cases.append({
                "n": n,
                "edges": len(graph.edges()),
                "tau": str(tau),
                "status": status,
                "mu": [str(x) for x in mu],
            })
            accepted += 1
            if status != "pass":
                print(json.dumps(cases[-1]), flush=True)
        print(f"n={n}: {accepted} checked", flush=True)
    summary = {
        "method": "Seeded random maximal 2-trees, exact UST expected degrees via Laplacian minors, and exact degree-window spanning-tree search.",
        "seed": 20261027,
        "cases": len(cases),
        "counterexamples": sum(c["status"] == "None" for c in cases),
        "timeouts": sum(c["status"] == "timeout" for c in cases),
        "by_order": {
            str(n): sum(c["n"] == n for c in cases) for n in range(8, 14)
        },
        "examples": cases,
        "scope": "A finite seeded sample of maximal 2-connected series-parallel graphs; no general conclusion follows.",
    }
    output = Path(__file__).with_name("codex_2tree_scan.json")
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "examples"}, indent=2))


if __name__ == "__main__":
    main()
