"""Audit the unresolved composite-index parity balance at powers of two.

Run from the repository root:
    python conjectures/004-self-totient/composite_parity_blocks.py --terms 1000000

This is a finite calculation, not evidence for a proven limiting rate.
"""

import argparse
import json
from array import array
from math import gcd, log
from pathlib import Path

from review_verify import factors, signed_divisors, sieve


def run(limit):
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    counts[1] = 1
    values = [0, 1]
    prime_count = 0
    composite_odd = 0
    last_composite_odd = 0
    last_composite_count = 0
    rows = []

    for n in range(2, limit + 1):
        if n & (n - 1) == 0 and n >= 4:
            # At n=2^r, P(n)=1 (the index 2) and Q(n)=1+the
            # odd composite-index terms k<n (the remaining 1 is index 1).
            q = 1 + composite_odd
            baseline = (n - 1 - prime_count) / 2
            discrepancy = q - baseline
            composite_count = n - 2 - prime_count
            composite_count_in_block = composite_count - last_composite_count
            rows.append({
                "n": n,
                "Q": q,
                "composite_odd_before_n": composite_odd,
                "composite_count_before_n": composite_count,
                "discrepancy": discrepancy,
                "discrepancy_over_n_over_log_n": discrepancy * log(n) / n,
                "last_dyadic_block_composite_odd_density":
                    (composite_odd - last_composite_odd) /
                    (composite_count_in_block or 1),
            })
            last_composite_odd = composite_odd
            last_composite_count = composite_count

        a_n = sum(sign * counts[d] for d, sign in signed_divisors(factors(n, spf)))
        if n <= 3000:
            assert a_n == sum(gcd(v, n) == 1 for v in values[1:]), n
            values.append(a_n)
        if n & (n - 1) == 0 and n >= 4:
            assert a_n == 2 + composite_odd, (n, a_n, composite_odd)
        if spf[n] == n:
            prime_count += 1
        elif a_n & 1:
            composite_odd += 1
        for d, _ in signed_divisors(factors(a_n, spf)):
            counts[d] += 1

    return {
        "terms": limit,
        "literal_check_terms": min(limit, 3000),
        "scope": "Finite exact recurrence calculation; no limiting claim proved.",
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.terms < 3000:
        parser.error("--terms must be at least 3000")
    result = run(args.terms)
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)


if __name__ == "__main__":
    main()
