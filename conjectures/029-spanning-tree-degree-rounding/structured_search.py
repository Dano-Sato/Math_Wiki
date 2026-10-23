"""Search structured graph families for a floor/ceiling UST-degree counterexample."""

import json
import random
from itertools import product
from pathlib import Path

from explore_floor_ceil import check_graph, tree_catalog


def mask_of(n, edges, index):
    return sum(1 << index[tuple(sorted(e))] for e in edges)


def candidates(n):
    pairs, _ = tree_catalog(n)
    index = {e: k for k, e in enumerate(pairs)}
    out = {}

    def add(name, edges):
        m = mask_of(n, edges, index)
        if m:
            out.setdefault(m, name)

    # Complete bipartite and multipartite examples.
    for a in range(1, n):
        A, B = set(range(a)), set(range(a, n))
        add(f"complete-bipartite-{a}-{n-a}", [(u, v) for u in A for v in B])
    for sizes in ([1, n - 1], [2, n - 2], [1, 1, n - 2],
                  [2, 2, n - 4], [1, 2, n - 3], [1, 1, 1, n - 3]):
        if min(sizes) < 1 or sum(sizes) != n:
            continue
        parts, start = [], 0
        for size in sizes:
            parts.append(set(range(start, start + size)))
            start += size
        add("complete-multipartite-" + "-".join(map(str, sizes)),
            [(u, v) for i, A in enumerate(parts) for B in parts[i + 1:]
             for u in A for v in B])

    # Clique sums joined through a narrow cut, a natural stress case for degree constraints.
    for a in range(1, n):
        A, B = set(range(a)), set(range(a, n))
        internal = [(u, v) for S in (A, B) for u in S for v in S if u < v]
        for k in (1, 2, 3):
            cross = [(u, v) for u in A for v in B][:k]
            add(f"clique-cut-{a}-{n-a}-width-{k}", internal + cross)

    # Cycles with selected chords and complements of sparse edge sets.
    cycle = {(i, (i + 1) % n) for i in range(n)}
    cycle = {tuple(sorted(e)) for e in cycle}
    add("cycle", cycle)
    all_edges = set(pairs)
    for v in range(n):
        for keep in range(n):
            if keep == v:
                continue
            removed = {tuple(sorted((v, w))) for w in range(n) if w not in (v, keep)}
            add(f"complete-minus-star-{v}-keep-{keep}", all_edges - removed)
    for e in pairs:
        add(f"complete-minus-edge-{e}", all_edges - {e})

    rng = random.Random(20261024 + n)
    noncycle = list(all_edges - cycle)
    for i in range(160):
        p = rng.choice((0.12, 0.22, 0.35, 0.5, 0.7, 0.88))
        edges = set(cycle)
        edges.update(e for e in noncycle if rng.random() < p)
        add(f"cycle-chords-sample-{i}", edges)

    return pairs, out


def cut_capacity_obstruction(n, graph, pairs, trees):
    """Return True only if every rounded vector violates a necessary cut bound."""
    valid = [degrees for mask, degrees in trees if mask & graph == mask]
    count = len(valid)
    sums = [sum(degrees[v] for degrees in valid) for v in range(n)]
    options = []
    for s in sums:
        lo, hi = s // count, (s + count - 1) // count
        options.append((lo,) if lo == hi else (lo, hi))

    subset_data = []
    for subset in range(1, (1 << n) - 1):
        vertices = [v for v in range(n) if subset & (1 << v)]
        internal = sum(1 for k, (u, v) in enumerate(pairs)
                       if graph & (1 << k) and (subset >> u & 1) and (subset >> v & 1))
        cut = sum(1 for k, (u, v) in enumerate(pairs)
                  if graph & (1 << k) and ((subset >> u & 1) != (subset >> v & 1)))
        cap = 2 * min(len(vertices) - 1, internal) + cut
        subset_data.append((vertices, cap))

    for degrees in product(*options):
        if sum(degrees) != 2 * n - 2:
            continue
        if all(sum(degrees[v] for v in vertices) <= cap for vertices, cap in subset_data):
            return False
    return True


def main():
    summary = []
    for n in (7, 8):
        pairs, graphs = candidates(n)
        _, trees = tree_catalog(n)
        cut_obstructions = []
        for graph, name in graphs.items():
            result = check_graph(n, graph, trees)
            if result is not True:
                summary.append({"n": n, "family": name, "counterexample": result})
                break
            if cut_capacity_obstruction(n, graph, pairs, trees):
                cut_obstructions.append(name)
        else:
            summary.append({"n": n, "structured_connected_graphs_checked": len(graphs),
                            "all_pass": True,
                            "graphs_where_necessary_cut_capacity_eliminated_all_rounded_vectors": len(cut_obstructions)})
    output = {
        "method": "Exact enumeration of all spanning trees for generated structured graphs; exact integer comparison of UST mean degree with floor/ceiling candidate degrees.",
        "families": ["complete bipartite/multipartite", "clique sums with 1-3 edge cuts", "cycles with seeded random chord sets", "complete graphs with one edge or one star deleted"],
        "results": summary,
        "scope": "This is a targeted finite search, not proof. It is not a systematic census of all graphs of these orders.",
    }
    Path(__file__).with_name("structured_experiment.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
