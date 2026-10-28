"""Exact finite checks for the rough-index loss estimate and L17.

The limiting theorem is proved in rough_index_average.md. These checks
verify integer counting inequalities and report finite almost-prime data.
"""

import argparse
import json
from array import array
from pathlib import Path

from review_verify import factors, literal, signed_divisors, sieve


def run(limit, literal_terms):
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    counts[1] = 1
    omega = array("B", [0]) * (limit + 1)
    prefix = [0, 1]
    checked = min(limit, literal_terms)
    cutoffs = (10, 30, 100)
    thresholds = ((1, 10), (1, 20), (1, 50))
    loss_sums = dict.fromkeys(cutoffs, 0)
    union_bound_sums = dict.fromkeys(cutoffs, 0)
    rough_counts = dict.fromkeys(cutoffs, 0)
    rough_losses = dict.fromkeys(cutoffs, 0)
    totals = dict.fromkeys(range(1, 5), 0)
    bad = {r: [0] * len(thresholds) for r in totals}
    rows = []
    next_checkpoint = 10_000

    for n in range(2, limit + 1):
        ps = factors(n, spf)
        value = sum(sign * counts[d] for d, sign in signed_divisors(ps))
        assert 1 <= value < n
        if n <= checked:
            prefix.append(value)
        omega[n] = omega[n // spf[n]] + 1
        phi = n
        for p in ps:
            phi = phi // p * (p - 1)
        r = omega[n]
        if r in totals:
            totals[r] += 1
            for j, (num, den) in enumerate(thresholds):
                bad[r][j] += den * abs(value - phi) > num * phi

        for y in cutoffs:
            big = [p for p in ps if p > y]
            loss = n - 1 - sum(sign * counts[d]
                               for d, sign in signed_divisors(big))
            union_bound = sum(counts[p] for p in big)
            assert 0 <= loss <= union_bound, (n, y, loss, union_bound)
            loss_sums[y] += loss
            union_bound_sums[y] += union_bound
            if ps[0] > y:
                assert loss == n - 1 - value
                rough_counts[y] += 1
                rough_losses[y] += loss
        for d, _ in signed_divisors(factors(value, spf)):
            counts[d] += 1

        if n == next_checkpoint or n == limit:
            prime_counts = {
                y: sum(counts[p] for p in range(y + 1, n + 1) if spf[p] == p)
                for y in cutoffs
            }
            loss_rows = []
            for y in cutoffs:
                max_factors = 0
                power = y + 1
                while power <= n:
                    max_factors += 1
                    power *= y + 1
                # Integer version of the proof's final logarithmic bound.
                assert prime_counts[y] <= n * max_factors
                intermediate = (n // (y + 1)) * prime_counts[y]
                final = (n // (y + 1)) * n * max_factors
                assert loss_sums[y] <= union_bound_sums[y] <= intermediate <= final
                loss_rows.append({
                    "y": y,
                    "total_large_prime_union_loss": loss_sums[y],
                    "sum_of_individual_prime_losses": union_bound_sums[y],
                    "intermediate_integer_upper_bound": intermediate,
                    "final_integer_upper_bound": final,
                    "rough_index_count": rough_counts[y],
                    "rough_index_loss_sum": rough_losses[y],
                })
            rows.append({
                "N": n,
                "almost_prime_rows": [
                    {"Omega": r, "count": totals[r],
                     "bad_counts": {f"{num}/{den}": bad[r][j]
                                    for j, (num, den) in enumerate(thresholds)},
                     "bad_fractions": {f"{num}/{den}": bad[r][j] / totals[r]
                                       for j, (num, den) in enumerate(thresholds)}}
                    for r in totals if totals[r]
                ],
                "loss_bound_rows": loss_rows,
            })
            next_checkpoint *= 10

    assert prefix == literal(checked)
    return {
        "limit": limit,
        "literal_check_terms": checked,
        "note": "Finite verification only. Cutoffs 10, 30, 100 are computational examples; the asymptotic proof uses y=(log X)^4.",
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--literal-terms", type=int, default=3000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit < 10_000 or args.literal_terms < 2:
        parser.error("--limit >= 10000 and --literal-terms >= 2 are required")
    result = run(args.limit, args.literal_terms)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
