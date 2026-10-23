"""Check a vertex-local strengthening of conjecture 025 on the graph atlas."""

import itertools
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx


def connected_mask(n, edge_masks, mask):
    if mask == 0:
        return False
    start = mask & -mask
    seen = start
    frontier = start
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        new = edge_masks[vertex] & mask & ~seen
        seen |= new
        frontier |= new
    return seen == mask


rows = defaultdict(lambda: {"graphs": 0, "minimum_local_slack_by_k": {}})
checked = 0
violations = []
for graph in nx.graph_atlas_g():
    n = graph.number_of_nodes()
    if n < 3 or not nx.is_biconnected(graph):
        continue
    edge_masks = [0] * n
    for u, v in graph.edges():
        edge_masks[u] |= 1 << v
        edge_masks[v] |= 1 << u
    connected = [connected_mask(n, edge_masks, mask) for mask in range(1 << n)]
    local_counts = [[0] * n for _ in range(n)]
    full = (1 << n) - 1
    for size in range(2, n - 1):
        for subset in itertools.combinations(range(n), size):
            mask = sum(1 << vertex for vertex in subset)
            if not connected[mask] or not connected[full ^ mask]:
                continue
            for vertex in subset:
                local_counts[size][vertex] += 1
    rows[n]["graphs"] += 1
    for size in range(2, n - 1):
        slack = min(local_counts[size][vertex] - size for vertex in range(n))
        key = str(size)
        rows[n]["minimum_local_slack_by_k"][key] = min(
            rows[n]["minimum_local_slack_by_k"].get(key, slack), slack
        )
        if slack < 0:
            violations.append({"n": n, "k": size, "slack": slack})
    checked += 1

payload = {
    "claim_checked": "For every vertex v and 2 <= k <= n-2, at least k k-sets S containing v have both G[S] and G[V\\S] connected.",
    "method": "All non-isomorphic biconnected simple graphs in NetworkX graph atlas (orders 3 through 7); all vertex subsets enumerated exactly.",
    "checked_graphs": checked,
    "orders": {
        str(n): row for n, row in sorted(rows.items())
    },
    "violations": violations,
    "interpretation": "Finite verification only; it does not prove the local strengthening or conjecture 025 for arbitrary order.",
}
Path(__file__).with_name("local_experiment.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(payload, indent=2))
