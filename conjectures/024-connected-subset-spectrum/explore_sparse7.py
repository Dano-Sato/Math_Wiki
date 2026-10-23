"""Check the local participation bound on sparse 7-vertex 2-connected graphs."""

from itertools import combinations
import json
from pathlib import Path

from explore import connected, edge_id, is_two_connected


def main():
    n = 7
    possible_edges = tuple(combinations(range(n), 2))
    results = []
    for m in range(n, n + 3):
        graph_count = 0
        minima = {k: None for k in range(2, n)}
        witnesses = {k: None for k in minima}
        counterexample = None
        for chosen in combinations(range(len(possible_edges)), m):
            mask = sum(1 << edge_id(*possible_edges[e], n) for e in chosen)
            if not is_two_connected(mask, n):
                continue
            graph_count += 1
            for k in range(2, n):
                participation = [0] * n
                for vertices in combinations(range(n), k):
                    if connected(mask, n, vertices):
                        for v in vertices:
                            participation[v] += 1
                local_min = min(participation)
                if minima[k] is None or local_min < minima[k]:
                    minima[k] = local_min
                    vertex = participation.index(local_min)
                    witnesses[k] = {"edge_mask": mask, "vertex": vertex,
                                    "participation": local_min}
                if local_min < k and counterexample is None:
                    counterexample = {"edge_mask": mask, "k": k,
                                      "participation_by_vertex": participation}
                    break
            if counterexample is not None:
                break
        results.append({
            "n": n,
            "edges": m,
            "labelled_2_connected_graphs_checked": graph_count,
            "minimum_participation_by_k": {
                str(k): minima[k] for k in minima
            },
            "witnesses": {str(k): witnesses[k] for k in witnesses},
            "counterexample": counterexample,
        })
        if counterexample is not None:
            break
    output = {
        "claim": "Every vertex belongs to at least k connected induced k-sets.",
        "scope": "all labelled 2-connected simple graphs on 7 vertices with 7, 8, or 9 edges",
        "results": results,
        "limitation": "This does not check 7-vertex graphs with 10 or more edges or any larger order.",
    }
    Path(__file__).with_name("sparse7_experiment.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
