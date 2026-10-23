"""Exhaustively check conjecture 024 on labelled simple graphs through n=6."""

from itertools import combinations
import json
from pathlib import Path


def edge_id(i: int, j: int, n: int) -> int:
    return i * (2 * n - i - 1) // 2 + (j - i - 1)


def connected(mask: int, n: int, vertices: tuple[int, ...]) -> bool:
    if len(vertices) <= 1:
        return True
    allowed = set(vertices)
    seen = {vertices[0]}
    stack = [vertices[0]]
    while stack:
        u = stack.pop()
        for v in vertices:
            if v not in seen and (mask >> edge_id(min(u, v), max(u, v), n)) & 1:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(allowed)


def is_two_connected(mask: int, n: int) -> bool:
    all_vertices = tuple(range(n))
    if not connected(mask, n, all_vertices):
        return False
    return all(
        connected(mask, n, tuple(v for v in all_vertices if v != deleted))
        for deleted in all_vertices
    )


def check_order(n: int) -> dict:
    edge_count = n * (n - 1) // 2
    subsets = {k: tuple(combinations(range(n), k)) for k in range(2, n)}
    minima = {k: None for k in subsets}
    two_connected_graphs = 0
    for mask in range(1 << edge_count):
        if mask.bit_count() < n:
            continue
        if not is_two_connected(mask, n):
            continue
        two_connected_graphs += 1
        for k, sets in subsets.items():
            count = sum(connected(mask, n, vertices) for vertices in sets)
            if minima[k] is None or count < minima[k]:
                minima[k] = count
    return {
        "n": n,
        "labelled_2_connected_graphs": two_connected_graphs,
        "minimum_connected_induced_sets_by_size": {
            str(k): minima[k] for k in minima
        },
        "conjecture_holds": all(minima[k] >= n for k in minima),
    }


def main() -> None:
    results = [check_order(n) for n in range(3, 7)]
    output = {
        "scope": "all labelled simple graphs of orders 3 through 6",
        "method": "edge-mask enumeration; test connectivity after deleting each single vertex; count connected induced vertex sets of each size 2 through n-1",
        "results": results,
        "limitation": "finite verification only; no claim for orders greater than 6",
    }
    target = Path(__file__).with_name("experiment.json")
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
