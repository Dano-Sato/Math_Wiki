"""Exact 10-vertex counterexample: attach leaves to two consecutive vertices of C_8."""

import itertools
import json
from collections import Counter
from pathlib import Path


N_CYCLE = 8
ATTACHED = {0, 1}
N_VERTICES = N_CYCLE + len(ATTACHED)
edges = [(i, (i + 1) % N_CYCLE) for i in range(N_CYCLE)]
edges.extend((v, N_CYCLE + j) for j, v in enumerate(sorted(ATTACHED)))


def component_count(chosen_edges):
    parent = list(range(N_VERTICES))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in chosen_edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    return len({find(v) for v in range(N_VERTICES)})


leaf_counts = Counter()
spanning_trees = 0
for chosen in itertools.combinations(edges, N_VERTICES - 1):
    if component_count(chosen) != 1:
        continue
    spanning_trees += 1
    degrees = [0] * N_VERTICES
    for u, v in chosen:
        degrees[u] += 1
        degrees[v] += 1
    leaf_counts[sum(degree == 1 for degree in degrees)] += 1

coefficients = [leaf_counts[k] for k in range(N_VERTICES + 1)]
failures = [
    k for k in range(1, N_VERTICES)
    if coefficients[k] ** 2 < coefficients[k - 1] * coefficients[k + 1]
]
assert spanning_trees == N_CYCLE
assert [(k, leaf_counts[k]) for k in sorted(leaf_counts)] == [(2, 1), (3, 2), (4, 5)]
assert 3 in failures

result = {
    "graph": "C_8 with one pendant vertex attached to each of two consecutive cycle vertices 0,1",
    "vertices": N_VERTICES,
    "spanning_trees": spanning_trees,
    "nonzero_leaf_coefficients": {str(k): leaf_counts[k] for k in sorted(leaf_counts)},
    "failed_log_concavity_indices": failures,
    "witness": "a_3^2 = 2^2 = 4 < 1*5 = a_2*a_4",
    "verification": "Enumerated every (n-1)-edge subset and retained exactly the connected ones.",
}
Path(__file__).with_name("counterexample_pendant_cycle.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, indent=2))
