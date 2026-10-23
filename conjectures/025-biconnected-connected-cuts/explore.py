import itertools
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx


def connected_mask(n, edge_masks, mask):
    if mask == 0:
        return False
    start = (mask & -mask).bit_length() - 1
    seen = 1 << start
    frontier = seen
    while frontier:
        vbit = frontier & -frontier
        frontier ^= vbit
        v = vbit.bit_length() - 1
        new = edge_masks[v] & mask & ~seen
        seen |= new
        frontier |= new
    return seen == mask


rows = defaultdict(lambda: {"graphs": 0, "minimum_by_k": {}, "attained_by_cycle": False})
checked = 0
for graph in nx.graph_atlas_g():
    n = graph.number_of_nodes()
    if n < 3 or not nx.is_biconnected(graph):
        continue
    # Graph Atlas labels its vertices consecutively from 0.
    edge_masks = [0] * n
    for u, v in graph.edges():
        edge_masks[u] |= 1 << v
        edge_masks[v] |= 1 << u
    connected = [connected_mask(n, edge_masks, m) for m in range(1 << n)]
    minima = {}
    for k in range(1, n):
        counts = 0
        for subset in itertools.combinations(range(n), k):
            mask = sum(1 << v for v in subset)
            complement = ((1 << n) - 1) ^ mask
            if connected[mask] and connected[complement]:
                counts += 1
        minima[str(k)] = counts
    row = rows[n]
    row["graphs"] += 1
    for k, count in ((int(k), v) for k, v in minima.items()):
        row["minimum_by_k"][str(k)] = min(row["minimum_by_k"].get(str(k), count), count)
    if nx.is_isomorphic(graph, nx.cycle_graph(n)):
        row["attained_by_cycle"] = True
    checked += 1

payload = {
    "method": "all non-isomorphic biconnected simple graphs in NetworkX graph atlas (orders 3 through 7); all vertex subsets enumerated",
    "checked_graphs": checked,
    "orders": {str(n): {"biconnected_graphs": d["graphs"], "minimum_connected_bipartitions_by_subset_size": d["minimum_by_k"], "cycle_attains_n_for_all_k": d["attained_by_cycle"]} for n, d in sorted(rows.items())},
    "interpretation": "finite verification only; the atlas is not a proof for arbitrary order"
}
Path(__file__).with_name("experiment.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
