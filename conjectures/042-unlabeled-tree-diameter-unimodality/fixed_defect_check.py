"""Finite, symbolic and direct-enumeration checks for fixed_defect.md.

Uses NetworkX and SymPy already available in this repository's environment.
The symbolic formulas are expanded from the proved finite-series identity;
they are not fitted to sample counts. Run this script from the repository root.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import time

import networkx as nx
import sympy as sp

from fixed_defect import DefectCounter, product, substitute_square
from height_gf import diameter_rows


def binomial_polynomial(argument: sp.Expr, j: int) -> sp.Expr:
    return sp.prod(argument-i for i in range(j)) / sp.factorial(j)


def parity_polynomial(counter: DefectCounter, k: int, parity: int) -> sp.Poly:
    n = sp.Symbol("n", integer=True)
    length = n-3*k-2
    epsilon = (parity-k) % 2
    side, core = counter.base(k)
    ordinary_base = product(core, core, k)
    increment = side.copy()
    increment[0] -= 1
    term = [1]+[0]*k
    expression = sp.Integer(0)
    for j in range(k+1):
        coefficient = product(ordinary_base, term, k)[k]
        expression += coefficient * binomial_polynomial(length, j)
        term = product(term, increment, k)
    reflection_base = substitute_square(core, k)
    if epsilon:
        reflection_base = product(side, reflection_base, k)
    increment = substitute_square(side, k)
    increment[0] -= 1
    term = [1]+[0]*k
    for j in range(k//2+1):
        coefficient = product(reflection_base, term, k)[k]
        expression += coefficient * binomial_polynomial((length-epsilon)/2, j)
        term = product(term, increment, k)
    return sp.Poly(sp.expand(expression/2), n, domain=sp.QQ)


def rooted_code(tree: nx.Graph, root: int, parent: int | None) -> tuple[tuple, int]:
    children = [rooted_code(tree, v, root) for v in tree[root] if v != parent]
    code = tuple(sorted(code for code, _ in children))
    height = 1+max((h for _, h in children), default=-1)
    return code, height


def direct_rooted_check(counter: DefectCounter, max_n: int) -> dict[str, int]:
    free_trees = rooted_trees = checked = 0
    for n in range(1, max_n+1):
        heights: collections.Counter[int] = collections.Counter()
        trees = [nx.empty_graph(1)] if n == 1 else nx.nonisomorphic_trees(n)
        for tree in trees:
            free_trees += 1
            # Different roots on one free tree can be isomorphic; deduplicate.
            shapes = {rooted_code(tree, v, None) for v in tree}
            for _, h in shapes:
                heights[h] += 1
                rooted_trees += 1
        for h in range(min(counter.max_defect, n-1)+1):
            previous = counter.rooted[h-1][n] if h else 0
            actual = counter.rooted[h][n]-previous
            assert actual == heights[h], ("rooted Euler-product mismatch", n, h)
            checked += 1
    return {"through_n": max_n, "free_trees_enumerated": free_trees,
            "rooted_isomorphism_types": rooted_trees,
            "exact_height_entries_matched": checked}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=200)
    parser.add_argument("--max-k", type=int, default=30)
    parser.add_argument("--polynomials-through-k", type=int, default=8)
    parser.add_argument("--enumerate-through", type=int, default=13)
    args = parser.parse_args()
    if not (args.max_n >= 3*args.max_k+2 and 1 <= args.polynomials_through_k <= args.max_k
            and 1 <= args.enumerate_through <= 2*args.max_k+1):
        parser.error("inconsistent finite ranges")
    started = time.perf_counter()
    folder = Path(__file__).parent
    counter = DefectCounter(args.max_k)
    rows = diameter_rows(args.max_n)
    by_n = {row["n"]: row["diameter_counts"] for row in rows}
    previous = json.loads((folder / "review-diameter-600.json").read_text(encoding="utf-8"))
    hashes = {row["n"]: row["row_sha256"] for row in previous["rows"]}
    hash_checks = stable_checks = 0
    for n, counts in by_n.items():
        if n in hashes:
            digest = hashlib.sha256(",".join(map(str, counts)).encode("ascii")).hexdigest()
            assert digest == hashes[n], ("previous full-row mismatch", n)
            hash_checks += 1
        for k in range(min(args.max_k, (n-2)//3)+1):
            assert counter.count(n, k) == counts[n-k-2], ("stable formula mismatch", n, k)
            stable_checks += 1
    cached_checks = 0
    for label, counts in previous["selected_full_rows"].items():
        n = int(label)
        if n <= args.max_n:
            continue
        for k in range(min(args.max_k, (n-2)//3)+1):
            assert counter.count(n, k) == counts[n-k-2], ("cached stable mismatch", n, k)
            cached_checks += 1
    recurrence_checks = 0
    for k in range(1, args.max_k+1):
        for n in range(3*k+2, args.max_n-2*(k+1)+1):
            difference = sum(
                (-1)**j * comb(k+1, j) * by_n[n+2*j][n+2*j-k-2]
                for j in range(k+2)
            )
            assert difference == 0, ("step-two finite difference mismatch", n, k)
            recurrence_checks += 1
    polynomials = []
    polynomial_checks = 0
    for k in range(1, args.polynomials_through_k+1):
        expressions = {}
        for parity in (0, 1):
            poly = parity_polynomial(counter, k, parity)
            assert poly.degree() == k
            assert poly.LC() == sp.Rational(1, 2*sp.factorial(k))
            if k >= 3:
                assert poly.nth(k-1) == sp.Rational(k-7, 4*sp.factorial(k-1))
            for n in range(3*k+2, args.max_n+1):
                if n % 2 == parity:
                    assert poly.eval(n) == by_n[n][n-k-2], ("polynomial mismatch", n, k)
                    polynomial_checks += 1
            expressions["n_even" if parity == 0 else "n_odd"] = {
                "expression": str(poly.as_expr()),
                "latex": sp.latex(poly.as_expr()),
            }
        polynomials.append({"k": k, "valid_from_n": 3*k+2, **expressions})
    direct = direct_rooted_check(counter, args.enumerate_through)
    large_examples = []
    for k in range(1, min(args.polynomials_through_k, 6)+1):
        n = 10**12 + k % 2
        exact = counter.count(n, k)
        symbolic = parity_polynomial(counter, k, n % 2).eval(n)
        assert exact == symbolic
        large_examples.append({"n": n, "k": k, "count": exact})
    result = {
        "conjecture": "042", "version": "0.4", "date": "2026-10-24",
        "fresh_exact_range_n": [2, args.max_n], "deficits_checked": [0, args.max_k],
        "python_version": platform.python_version(), "networkx_version": nx.__version__,
        "sympy_version": sp.__version__,
        "validation": {
            "prior_full_row_hashes_matched": hash_checks,
            "stable_formula_vs_fresh_center_counts": stable_checks,
            "stable_formula_vs_larger_cached_rows": cached_checks,
            "step_two_difference_checks": recurrence_checks,
            "expanded_polynomials_vs_exact_counts": polynomial_checks,
            "rooted_data_direct_enumeration": direct,
            "large_n_two_methods_matched": len(large_examples),
        },
        "base_data": [{"k": k, "M": counter.base(k)[0], "B": counter.base(k)[1]}
                      for k in range(args.polynomials_through_k+1)],
        "parity_polynomials": polynomials, "large_n_examples": large_examples,
        "scope_note": "Polynomials are derived symbolically from the stable center identity, not interpolated. Finite comparisons audit the implementation. The general period-two polynomial theorem is proved in fixed_defect.md; full unimodality is unresolved.",
    }
    output = folder / "fixed-defect-experiment.json"
    output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"validation": result["validation"],
                      "first_polynomials": polynomials[:4],
                      "seconds": round(time.perf_counter()-started, 3),
                      "output": output.name}, indent=2))


if __name__ == "__main__":
    main()
