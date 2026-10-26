"""Finite check of the exact a_(2p) = O(2p) - R(p) identity.

Here O(2p) counts earlier odd terms and R(p) counts earlier terms equal to p.
The identity is proved in conjectures.md; this script only checks examples.
"""

import argparse
import json
from array import array
from math import gcd
from pathlib import Path

from review_verify import factors, signed_divisors, sieve


def run(limit):
    if limit < 6:
        raise ValueError("limit must be at least 6")
    spf = sieve(limit)
    divisor_counts = array("I", [0]) * (limit + 1)
    value_counts = array("I", [0]) * (limit + 1)
    divisor_counts[1] = value_counts[1] = 1
    odd_before = 1
    literal_prefix = [0, 1]
    records = []

    for n in range(2, limit + 1):
        a_n = sum(sign * divisor_counts[d]
                  for d, sign in signed_divisors(factors(n, spf)))
        if n <= 3000:
            assert a_n == sum(gcd(value, n) == 1
                              for value in literal_prefix[1:]), n
            literal_prefix.append(a_n)
        if n % 2 == 0 and n >= 6:
            p = n // 2
            if spf[p] == p:
                r_p = value_counts[p]
                assert a_n == odd_before - r_p, (n, a_n, odd_before, r_p)
                records.append({"p": p, "R": r_p})
        value_counts[a_n] += 1
        odd_before += a_n & 1
        for d, _ in signed_divisors(factors(a_n, spf)):
            divisor_counts[d] += 1

    max_r = max(item["R"] for item in records)
    return {
        "limit": limit,
        "literal_check_terms": min(limit, 3000),
        "prime_samples": len(records),
        "max_R": max_r,
        "positive_R": sum(item["R"] > 0 for item in records),
        "max_examples": [item for item in records if item["R"] == max_r],
        "warning": "Finite examples do not prove a uniform bound on R(p).",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.limit)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
