"""Exact finite audit of the proposed resolvent degree monotonicity (RDM).

For each labelled simple graph F on m=2,...,5 vertices, set
M=(m+1)I-L(F). Check exactly with rational arithmetic that
 deg(u)>deg(v) implies (M^{-1})[u,u]>(M^{-1})[v,v].
This is finite verification only, not a proof for arbitrary m.
"""
from itertools import combinations, permutations
import json
from pathlib import Path
import sympy as sp

summary = []
for m in range(2, 6):
    pairs = list(combinations(range(m), 2))
    graphs = 1 << len(pairs)
    checked_comparisons = 0
    for mask in range(graphs):
        A = sp.zeros(m)
        degree = [0] * m
        for j, (u, v) in enumerate(pairs):
            if (mask >> j) & 1:
                A[u, v] = A[v, u] = 1
                degree[u] += 1
                degree[v] += 1
        L = sp.diag(*degree) - A
        M = (m + 1) * sp.eye(m) - L
        inv = M.inv()
        for u, v in permutations(range(m), 2):
            if degree[u] > degree[v]:
                checked_comparisons += 1
                if not inv[u, u] > inv[v, v]:
                    raise AssertionError({
                        "m": m, "mask": mask, "edges": [pairs[j] for j in range(len(pairs)) if (mask >> j) & 1],
                        "u": u, "v": v, "degrees": [degree[u], degree[v]],
                        "diagonal": [str(inv[u, u]), str(inv[v, v])],
                    })
    summary.append({"vertices": m, "labelled_graphs": graphs, "strict_degree_comparisons": checked_comparisons,
                    "result": "all exact rational comparisons passed"})

result = {
    "claim": "For every simple graph F on m vertices, deg(u)>deg(v) implies ((m+1)I-L(F))^{-1}[u,u] > ((m+1)I-L(F))^{-1}[v,v].",
    "status": "COMPUTATIONALLY VERIFIED on all labelled simple F with 2<=m<=5 only",
    "method": "Exhaust all adjacency masks and compare SymPy exact rationals; no floating-point decisions.",
    "graphs_total": sum(row["labelled_graphs"] for row in summary),
    "by_order": summary,
    "limitations": ["Does not prove RDM for arbitrary m.", "Does not audit a Schur-complement proof not supplied in this task."]
}
Path(__file__).with_name("rdm_exact_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
