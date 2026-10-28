"""Finite checks for the local-to-global sieve identities in the connection note.

Uses literal gcd generation and direct pair counting. Does not prove any
asymptotic hypothesis or an implication to an external open problem.
"""

import argparse
import json
from collections import Counter
from fractions import Fraction
from math import gcd, prod
from pathlib import Path

from review_verify import factors, literal, signed_divisors, sieve


def run(limit):
    values = literal(limit)
    spf = sieve(limit)
    phi = [0] + [n * prod(Fraction(p - 1, p) for p in factors(n, spf))
                 for n in range(1, limit + 1)]
    histogram = Counter(values[1:])
    energy = sum(m * m for m in histogram.values())
    for p in range(2, limit + 1):
        if spf[p] == p:
            cp = sum(v % p == 0 for v in values[1:])
            assert cp * cp <= (limit // p) * energy
    rows = []
    for z in (2, 5, 11):
        tails = [0] + [prod(p for p in factors(v, spf) if p > z)
                       for v in values[1:]]
        direct_total = 0
        small_error = 0
        uniform_defect = 0
        for n in range(2, limit + 1):
            small = prod(p for p in factors(n, spf) if p <= z)
            loss = sum(gcd(tails[k], n) > 1 for k in range(1, n))
            actual_small = sum(gcd(values[k], small) == 1 for k in range(1, n))
            uniform_small = sum(gcd(j, small) == 1 for j in range(1, n))
            actual_defect = actual_small - values[n]
            baseline_defect = uniform_small - phi[n]
            assert 0 <= actual_defect <= loss
            assert baseline_defect >= 0
            assert values[n] - phi[n] == (actual_small - uniform_small
                                         - actual_defect + baseline_defect)
            direct_total += loss
            small_error += abs(actual_small - uniform_small)
            uniform_defect += baseline_defect
        double_total = 0
        main_term = Fraction(0)
        floor_bound = 0
        for k in range(1, limit):
            ds = signed_divisors([p for p in factors(values[k], spf) if p > z])
            coprime = sum(sign * (limit // d - k // d) for d, sign in ds)
            double_total += limit - k - coprime
            weight = sum(Fraction(sign, d) for d, sign in ds)
            main_term += (limit - k) * (1 - weight)
            floor_bound += len(ds)
        assert direct_total == double_total
        assert abs(direct_total - main_term) <= floor_bound
        assert z * uniform_defect <= limit * limit
        error = sum(abs(values[n] - phi[n]) for n in range(1, limit + 1))
        assert error <= small_error + direct_total + uniform_defect
        rows.append({"z": z, "exact_large_prime_pair_loss": direct_total,
                     "weighted_main_term": float(main_term),
                     "floor_error": float(direct_total - main_term),
                     "floor_error_bound": floor_bound,
                     "small_prime_error_sum": int(small_error),
                     "uniform_large_prime_defect_sum": int(uniform_defect),
                     "mean_absolute_error_sum": int(error)})
    crossings = [{"index": n, "previous": values[n - 1], "value": values[n],
                  "common_prime": 3} for n in (13, 19)]
    assert all(r["previous"] < 10 <= r["value"]
               and gcd(r["previous"], r["value"]) % 3 == 0 for r in crossings)
    return {"literal_terms": limit,
            "scope": "Finite exact identities only; no asymptotic assumptions verified.",
            "repeated_EKG_style_crossings_at_threshold_10": crossings,
            "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit < 20:
        parser.error("--limit must be at least 20")
    result = run(args.limit)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
