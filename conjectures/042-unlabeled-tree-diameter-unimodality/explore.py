"""Exact finite check of Conjecture 042 using NetworkX's unlabeled trees."""

from __future__ import annotations

import collections
import json
import platform
from pathlib import Path

import networkx as nx


def is_unimodal(values: list[int]) -> bool:
    """Return whether a finite sequence weakly rises then weakly falls."""
    peak = max(range(len(values)), key=values.__getitem__)
    return all(values[i] <= values[i + 1] for i in range(peak)) and all(
        values[i] >= values[i + 1] for i in range(peak, len(values) - 1)
    )


def tree_diameter(tree: nx.Graph) -> int:
    """Compute a tree diameter with two BFS traversals."""
    def farthest(source: int) -> tuple[int, int]:
        distances = {source: 0}
        queue = collections.deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in tree[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        endpoint = max(distances, key=distances.__getitem__)
        return endpoint, distances[endpoint]

    endpoint, _ = farthest(next(iter(tree)))
    return farthest(endpoint)[1]


def main() -> None:
    rows = []
    for n in range(2, 22):
        counts = collections.Counter(
            tree_diameter(tree) for tree in nx.nonisomorphic_trees(n)
        )
        diameters = list(range(min(counts), max(counts) + 1))
        values = [counts[d] for d in diameters]
        rows.append(
            {
                "n": n,
                "tree_count": sum(values),
                "diameter_counts": {str(d): counts[d] for d in diameters},
                "unimodal": is_unimodal(values),
            }
        )

    result = {
        "conjecture": "042",
        "range": [2, 21],
        "generator": "networkx.generators.nonisomorphic_trees",
        "networkx_version": nx.__version__,
        "python_version": platform.python_version(),
        "total_trees_checked": sum(row["tree_count"] for row in rows),
        "all_unimodal": all(row["unimodal"] for row in rows),
        "rows": rows,
        "scope_note": "Exact finite enumeration only; not a proof for n > 21.",
    }
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("range", "total_trees_checked", "all_unimodal")}, indent=2))


if __name__ == "__main__":
    main()
