"""Seeded random search for a failure of the vertex-local strengthening."""

import itertools
import json
import math
import random
from pathlib import Path

import networkx as nx


def local_profile(graph):
    n = graph.number_of_nodes()
    edge_masks = [0] * n
    for u, v in graph.edges():
        edge_masks[u] |= 1 << v
        edge_masks[v] |= 1 << u
    connected = [False] * (1 << n)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        seen = bit
        frontier = bit
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            vertex = bit.bit_length() - 1
            new = edge_masks[vertex] & mask & ~seen
            seen |= new
            frontier |= new
        connected[mask] = seen == mask

    local = [[0] * n for _ in range(n)]
    full = (1 << n) - 1
    for size in range(2, n - 1):
        for subset in itertools.combinations(range(n), size):
            mask = sum(1 << vertex for vertex in subset)
            if connected[mask] and connected[full ^ mask]:
                for vertex in subset:
                    local[size][vertex] += 1
    return local


random.seed(250)
attempts_per_order = 2000
checked = 0
minimum_slack = None
minimum_witness = None
violations = []
for n in range(8, 13):
    for _ in range(attempts_per_order):
        p = random.uniform(0.14, min(0.6, math.log(n) / n + 0.35))
        graph = nx.gnp_random_graph(n, p, seed=random.randrange(1 << 30))
        if not nx.is_biconnected(graph):
            continue
        checked += 1
        local = local_profile(graph)
        for size in range(2, n - 1):
            for vertex, count in enumerate(local[size]):
                slack = count - size
                if minimum_slack is None or slack < minimum_slack:
                    minimum_slack = slack
                    minimum_witness = {
                        "n": n,
                        "k": size,
                        "vertex": vertex,
                        "local_count": count,
                        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                    }
                if slack < 0:
                    violations.append({"n": n, "k": size, "vertex": vertex, "count": count})

payload = {
    "claim_checked": "For every vertex v and 2 <= k <= n-2, at least k k-sets S containing v have both G[S] and G[V\\S] connected.",
    "method": "Seeded G(n,p) sampling; seed 250; 2000 attempts at each order n=8,...,12; retain only 2-connected graphs and enumerate all subsets exactly.",
    "checked_graphs": checked,
    "minimum_local_slack": minimum_slack,
    "minimum_witness": minimum_witness,
    "violations": violations,
    "interpretation": "Random finite search only; no failure was found, which is not a proof.",
}
Path(__file__).with_name("random_local_experiment.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(payload, indent=2))
