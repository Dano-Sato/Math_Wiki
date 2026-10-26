"""Exact RDM audit for all labelled simple graphs on six vertices.

This extends audit_rdm_exact.py by one order. It checks only a finite family.
"""
from itertools import combinations, permutations
import json
from pathlib import Path

import sympy as sp

m = 6
pairs = list(combinations(range(m), 2))
checked_comparisons = 0
for mask in range(1 << len(pairs)):
    adjacency = sp.zeros(m)
    degrees = [0] * m
    for bit, (u, v) in enumerate(pairs):
        if (mask >> bit) & 1:
            adjacency[u, v] = adjacency[v, u] = 1
            degrees[u] += 1
            degrees[v] += 1
    laplacian = sp.diag(*degrees) - adjacency
    matrix = (m + 1) * sp.eye(m) - laplacian
    determinant = matrix.det(method="domain-ge")
    if determinant <= 0:
        raise AssertionError({"mask": mask, "determinant": determinant})
    # Diagonal entries of M^{-1} are principal cofactors divided by det(M).
    cofactors = [matrix.minor_submatrix(i, i).det(method="domain-ge") for i in range(m)]
    for u, v in permutations(range(m), 2):
        if degrees[u] > degrees[v]:
            checked_comparisons += 1
            if cofactors[u] <= cofactors[v]:
                raise AssertionError({
                    "mask": mask,
                    "edges": [pairs[j] for j in range(len(pairs)) if (mask >> j) & 1],
                    "u": u,
                    "v": v,
                    "degrees": degrees,
                    "inverse_diagonal_numerators": cofactors,
                })

result = {
    "claim": "For every simple graph F on six vertices, deg(u)>deg(v) implies ((7)I-L(F))^{-1}[u,u] > ((7)I-L(F))^{-1}[v,v].",
    "status": "COMPUTATIONALLY VERIFIED for all labelled simple graphs on six vertices only",
    "method": "Exhaust all 2^15 adjacency masks; compare exact integer principal cofactors over a common positive determinant.",
    "labelled_graphs": 1 << len(pairs),
    "strict_degree_comparisons": checked_comparisons,
    "limitations": ["Finite verification only; does not prove RDM for arbitrary m."],
}
Path(__file__).with_name("rdm_m6_exact_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
