"""Check d_k(G,v) >= k on all theta graphs up to 17 vertices."""

import json
from pathlib import Path


def make_theta(a, b, c):
    """Return adjacency bitmasks for three internally disjoint paths."""
    n = a + b + c + 2
    adj = [0] * n
    next_vertex = 2
    for internal_count in (a, b, c):
        path = [0] + list(range(next_vertex, next_vertex + internal_count)) + [1]
        next_vertex += internal_count
        for u, v in zip(path, path[1:]):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    return n, adj


def is_connected(mask, adj):
    seen = mask & -mask
    frontier = seen
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        new = adj[vertex] & mask & ~seen
        seen |= new
        frontier |= new
    return seen == mask


def check_theta(a, b, c):
    n, adj = make_theta(a, b, c)
    counts = [[0] * n for _ in range(n + 1)]
    for mask in range(1, 1 << n):
        k = mask.bit_count()
        if 2 <= k < n and is_connected(mask, adj):
            vertices = mask
            while vertices:
                bit = vertices & -vertices
                vertices ^= bit
                counts[k][bit.bit_length() - 1] += 1
    minima = {str(k): min(counts[k]) for k in range(2, n)}
    return {
        "internal_path_vertices": [a, b, c],
        "vertices": n,
        "minimum_d_k_by_k": minima,
        "bound_holds": all(int(value) >= int(k) for k, value in minima.items()),
    }


def main():
    results = []
    for total in range(3, 16):
        for a in range(1, total - 1):
            for b in range(a, total - a):
                c = total - a - b
                if b <= c:
                    results.append(check_theta(a, b, c))
    output = {
        "claim": "Every vertex of every theta graph belongs to at least k connected induced k-sets, for 2 <= k < n.",
        "scope": "all theta graphs with 3 to 15 total internal path vertices (5 to 17 graph vertices), up to isomorphism",
        "graphs_checked": len(results),
        "all_pass": all(row["bound_holds"] for row in results),
        "results": results,
        "limitation": "finite verification only; it does not prove the bound for all theta graphs or all 2-connected graphs",
    }
    Path(__file__).with_name("theta_local_experiment.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in output.items() if k != "results"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
