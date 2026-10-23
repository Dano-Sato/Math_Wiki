"""Check the local participation strengthening for conjecture 024 through n=6."""

import json
from itertools import combinations
from pathlib import Path

from explore import connected, is_two_connected


def check_order(n):
    edge_count = n * (n - 1) // 2
    subsets = {k: tuple(combinations(range(n), k)) for k in range(2, n)}
    minima = {k: None for k in subsets}
    minima_witness = {k: None for k in subsets}
    graphs = 0
    for mask in range(1 << edge_count):
        if mask.bit_count() < n or not is_two_connected(mask, n):
            continue
        graphs += 1
        counts = {k: [0] * n for k in subsets}
        for k, sets in subsets.items():
            for vertices in sets:
                if connected(mask, n, vertices):
                    for v in vertices:
                        counts[k][v] += 1
        for k, per_vertex in counts.items():
            local_min = min(per_vertex)
            if minima[k] is None or local_min < minima[k]:
                minima[k] = local_min
                vertex = per_vertex.index(local_min)
                minima_witness[k] = {"edge_mask": mask, "vertex": vertex,
                                     "participation": local_min}
    return {
        "n": n,
        "labelled_2_connected_graphs": graphs,
        "minimum_connected_k_sets_containing_a_vertex": {
            str(k): minima[k] for k in minima
        },
        "strengthening_holds": all(minima[k] >= k for k in minima),
        "minimum_witnesses": {str(k): minima_witness[k] for k in minima},
    }


def main():
    output = {
        "strengthening": "Every vertex of every 2-connected graph belongs to at least k connected induced k-sets, for 2 <= k < n.",
        "scope": "all labelled simple 2-connected graphs with 3 <= n <= 6",
        "results": [check_order(n) for n in range(3, 7)],
        "limitation": "finite verification only",
    }
    Path(__file__).with_name("local_experiment.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
