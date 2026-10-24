"""Exact finite checks of the proofs in tail_bounds.md (Conjecture 042 v0.3).

Run from the repository root:
    python conjectures/042-unlabeled-tree-diameter-unimodality/tail_bounds_check.py

The proof is in tail_bounds.md. This script checks bounds against exact diameter
counts, and separately counts the unique-diameter leaf-decoration family by
direct NetworkX enumeration. No numerical asymptotics are used as a proof.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from math import comb, isqrt
from pathlib import Path
import platform
import time

import networkx as nx

from height_gf import diameter_rows


def good_family(n: int, k: int) -> int:
    """Exact reflection-orbit count G, for n >= 2*k+4 and k >= 1."""
    length = n-k-4
    if k < 1 or length < k:
        raise ValueError("good-family formula requires k >= 1 and n >= 2*k+4")
    fixed = 0 if length % 2 == 0 and k % 2 else comb(length//2, k//2)
    count, remainder = divmod(comb(length, k) + fixed, 2)
    if remainder:
        raise ArithmeticError("nonintegral reflection count")
    return count


def plane_forest_upper(n: int, d: int) -> int:
    """[z^s] C(z)^(d-1), s=n-1-d; an upper bound, not an exact count."""
    s, p = n-1-d, d-1
    if s < 0 or p < 1:
        raise ValueError("requires 2 <= d <= n-1")
    count, remainder = divmod(p * comb(p+2*s, s), p+2*s)
    if remainder:
        raise ArithmeticError("nonintegral plane-forest count")
    return count


def forest_remainder(n: int, k: int) -> int:
    """E(n,k), the explicit exceptional-family upper bound in section 6."""
    d = n-1-k
    result = 2 * comb(d-2, k-1)
    for m in range(1, k):
        coefficient, remainder = divmod(m * comb(2*k, k-m), k)
        if remainder:
            raise ArithmeticError("nonintegral nonempty forest count")
        result += comb(d-1, m) * coefficient
    return result


def good_family_by_enumeration(max_n: int) -> dict[str, object]:
    """Classify actual unlabeled trees, without using the reflection formula."""
    total_trees = 0
    pair_checks = 0
    for n in range(6, max_n+1):
        counts: collections.Counter[int] = collections.Counter()
        for tree in nx.nonisomorphic_trees(n):
            total_trees += 1
            distances = dict(nx.all_pairs_shortest_path_length(tree))
            diameter = max(max(row.values()) for row in distances.values())
            k = n-1-diameter
            if k < 1 or n < 2*k+4:
                continue
            endpoints = [
                (u, v) for u in tree for v in tree
                if u < v and distances[u][v] == diameter
            ]
            if len(endpoints) != 1:
                continue
            left, right = endpoints[0]
            path = nx.shortest_path(tree, left, right)
            path_set = set(path)
            outside = set(tree) - path_set
            if not all(tree.degree(v) == 1 for v in outside):
                continue
            allowed = set(path[2:-2])
            anchors = [next(iter(tree[v])) for v in outside]
            if len(set(anchors)) == k and all(v in allowed for v in anchors):
                counts[k] += 1
        for k in range(1, (n-4)//2+1):
            assert counts[k] == good_family(n, k), ("direct good-family mismatch", n, k)
            pair_checks += 1
    return {"range": [6, max_n], "trees_enumerated": total_trees,
            "good_family_pairs_matched": pair_checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=200)
    parser.add_argument("--enumerate-through", type=int, default=14)
    args = parser.parse_args()
    if args.max_n < 16 or not 6 <= args.enumerate_through <= args.max_n:
        parser.error("require max-n >= 16 and 6 <= enumerate-through <= max-n")
    started = time.perf_counter()
    folder = Path(__file__).parent
    rows = diameter_rows(args.max_n)
    old = json.loads((folder / "review-diameter-600.json").read_text(encoding="utf-8"))
    old_hashes = {row["n"]: row["row_sha256"] for row in old["rows"]}
    hashes_matched = 0
    upper_checks = lower_checks = error_checks = theorem_checks = 0
    samples = []
    for row in rows:
        n, counts = row["n"], row["diameter_counts"]
        digest = hashlib.sha256(
            ",".join(map(str, counts)).encode("ascii")
        ).hexdigest()
        if n in old_hashes:
            assert digest == old_hashes[n], ("previous row digest mismatch", n)
            hashes_matched += 1
        for d in range(2, n):
            assert counts[d-1] <= plane_forest_upper(n, d), ("Catalan upper", n, d)
            upper_checks += 1
        for k in range(1, (n-4)//2+1):
            actual = counts[n-k-2]
            good = good_family(n, k)
            assert good <= actual, ("good-family lower", n, k)
            assert actual-good <= forest_remainder(n, k), ("exception bound", n, k)
            lower_checks += 1
            error_checks += 1
        if n >= 16:
            width = isqrt(n)//2
            for k in range(2, width+1):
                actual, preceding = counts[n-k-2], counts[n-k-1]
                assert comb(n-k-4, k) > 2*comb(n+k-3, k-1), ("strict bound", n, k)
                assert actual > preceding, ("tail theorem", n, k)
                theorem_checks += 1
            tail = counts[-(width+1):]
            assert all(x > y for x, y in zip(tail, tail[1:]))
            if n in {16, 100, args.max_n}:
                samples.append({"n": n, "K": width,
                                "diameters": [n-1-width, n-1], "counts": tail})
    threshold_checks = 0
    for k in range(2, 201):
        for n in (4*k*k, 4*k*k+1, 4*k*k+1000):
            assert comb(n-k-4, k) > 2*comb(n+k-3, k-1), ("large threshold", n, k)
            threshold_checks += 1
    direct = good_family_by_enumeration(args.enumerate_through)
    result = {
        "conjecture": "042", "version": "0.3", "date": "2026-10-24",
        "range": [2, args.max_n], "python_version": platform.python_version(),
        "networkx_version": nx.__version__,
        "validation": {
            "previous_exact_row_hashes_matched": hashes_matched,
            "plane_forest_upper_bounds_checked": upper_checks,
            "good_family_lower_bounds_checked": lower_checks,
            "exceptional_family_bounds_checked": error_checks,
            "T2_comparisons_against_exact_coefficients": theorem_checks,
            "all_T3_tails_checked_from_n": 16,
            "binomial_threshold_checks_k_2_through_200": threshold_checks,
            "direct_unlabeled_tree_classification": direct,
        },
        "tail_samples": samples,
        "scope_note": "Finite checks support implementation and proof auditing. General bounds, growing-width monotonicity and fixed-defect asymptotics are proved in tail_bounds.md; full unimodality remains unresolved.",
    }
    output = folder / "tail-bounds-experiment.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"range": result["range"], "validation": result["validation"],
                      "seconds": round(time.perf_counter()-started, 3),
                      "output": output.name}, indent=2))


if __name__ == "__main__":
    main()
