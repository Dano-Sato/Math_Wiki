"""Finite checks for the conditional mean-to-divisibility proof.

Checks exact identities, not hypothesis (A) or any asymptotic conclusion.
"""

import argparse
import json
from array import array
from math import gcd, pi, prod
from pathlib import Path

from review_verify import factors, literal, signed_divisors, sieve


def run(limit, literal_terms):
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    counts[1] = 1
    values = array("I", [0, 1])
    phis = array("I", [0, 1])
    for n in range(2, limit + 1):
        ps = factors(n, spf)
        value = sum(sign * counts[d] for d, sign in signed_divisors(ps))
        assert 1 <= value < n
        values.append(value)
        phi = n
        for p in ps:
            phi = phi // p * (p - 1)
        phis.append(phi)
        for d, _ in signed_divisors(factors(value, spf)):
            counts[d] += 1

    checked = min(limit, literal_terms)
    assert values[:checked + 1].tolist() == literal(checked)
    moduli = (1, 2, 3, 6, 30)
    zs = (2, 3, 5, 7, 11)
    tracked = (1, 2, 3, 6, 30)
    rows = []
    for nmax in sorted({min(limit, 1000), min(limit, 10000), limit}):
        lhs = {m: sum(values[n] for n in range(m, nmax + 1, m))
               for m in moduli}
        exact = dict.fromkeys(moduli, 0)
        main = dict.fromkeys(moduli, 0.0)
        bounds = dict.fromkeys(moduli, 0)
        weighted_unit = dict.fromkeys(moduli, 0.0)
        unit_phi = {m: sum(phis[n] for n in range(m, nmax + 1, m))
                    for m in moduli}
        ordinary_counts = dict.fromkeys(tracked, 0)
        w_sums = {z: dict.fromkeys(tracked, 0.0) for z in zs}
        weighted_divisor_sums = {z: {} for z in zs}
        for z in zs:
            small = [p for p in range(2, z + 1) if spf[p] == p]
            weighted_divisor_sums[z] = dict.fromkeys(
                (d for d, _ in signed_divisors(small)), 0.0)

        for k in range(1, nmax + 1):
            a = values[k]
            ds = signed_divisors(factors(a, spf))
            b = phis[a] / a
            for m in moduli:
                if gcd(a, m) != 1:
                    continue
                weighted_unit[m] += b
                if k < nmax:
                    exact[m] += sum(sign * (nmax // (m * d) - k // (m * d))
                                    for d, sign in ds)
                    main[m] += (nmax - k) * b / m
                    bounds[m] += len(ds)
            for d in tracked:
                ordinary_counts[d] += (a % d == 0)
            for z in zs:
                small_dividing = [p for p in factors(a, spf) if p <= z]
                bz = prod(1 - 1 / p for p in small_dividing)
                w = b / bz
                assert -1e-12 <= w <= 1 + 1e-12
                for d in tracked:
                    if a % d == 0:
                        w_sums[z][d] += w
                for d in weighted_divisor_sums[z]:
                    if a % d == 0:
                        weighted_divisor_sums[z][d] += b

        for m in moduli:
            assert lhs[m] - (m == 1) == exact[m], (nmax, m)
            assert abs(exact[m] - main[m]) <= bounds[m] + 1e-6
        for z in zs:
            expanded = sum(total / phis[d]
                           for d, total in weighted_divisor_sums[z].items())
            assert abs(expanded - w_sums[z][1]) < 1e-8 * nmax
            for d in tracked:
                missing = ordinary_counts[d] - w_sums[z][d]
                assert -1e-8 <= missing <= nmax - w_sums[z][1] + 1e-8

        rows.append({
            "N": nmax,
            "sum_absolute_error_over_N_squared":
                sum(abs(values[k] - phis[k]) for k in range(1, nmax + 1)) / nmax**2,
            "moduli": {str(m): {
                "exact_double_count_verified": True,
                "floor_error": exact[m] - main[m],
                "proven_finite_error_bound": bounds[m],
                "weighted_coprime_mean": weighted_unit[m] / nmax,
                "conditional_target": 6 / pi**2 * prod(p / (p + 1) for p in factors(m, spf)),
                "totient_multiple_sum_over_N_squared": unit_phi[m] / nmax**2,
            } for m in moduli},
            "divisibility_densities": {str(d): ordinary_counts[d] / nmax for d in tracked},
            "truncated_weight_means": {str(z): w_sums[z][1] / nmax for z in zs},
        })
    return {
        "date": "2026-10-27",
        "limit": limit,
        "literal_prefix_checked": checked,
        "exact_identities_and_finite_inequalities_passed": True,
        "scope": "Finite checks only; hypothesis (A) and conjecture 004 remain unproved.",
        "checkpoints": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--literal-terms", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit < 3000 or args.literal_terms < 1:
        parser.error("--limit must be at least 3000 and --literal-terms positive")
    result = run(args.limit, args.literal_terms)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
