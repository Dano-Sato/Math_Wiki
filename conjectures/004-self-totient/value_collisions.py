"""Audit value collisions in 004's exact recurrence.

The coprime-position rank bound is proved in discussion.md, D022.
All growth rates in this output are finite observations, not theorems.
"""

import argparse
import json
from array import array
from math import gcd, log
from pathlib import Path

from review_verify import factors, literal, signed_divisors, sieve


def run(limit, literal_terms):
    spf = sieve(limit)
    divisor_counts = array("I", [0]) * (limit + 1)
    multiplicities = array("I", [0]) * (limit + 1)
    divisor_counts[1] = multiplicities[1] = 1
    prefix = [0, 1]
    checked = min(limit, literal_terms)
    max_multiplicity = 1
    max_value = 1
    collision_energy = 1
    max_r = 0
    max_r_examples = []
    prime_samples = 0
    coprime_position_checks = 0
    rows = []
    next_checkpoint = 1000

    for n in range(2, limit + 1):
        a_n = sum(sign * divisor_counts[d]
                  for d, sign in signed_divisors(factors(n, spf)))
        assert 1 <= a_n < n
        if n <= checked:
            prefix.append(a_n)
        rank = multiplicities[a_n] + 1
        if a_n >= 2 and gcd(a_n, n) == 1:
            # The two initial 1s and all previous occurrences of a_n
            # are distinct entries counted by the defining recurrence.
            assert rank <= a_n - 1, (n, a_n, rank)
            coprime_position_checks += 1

        if n >= 6 and n % 2 == 0:
            p = n // 2
            if spf[p] == p:
                r_p = multiplicities[p]
                assert a_n == n - 1 - divisor_counts[2] - r_p
                prime_samples += 1
                if r_p > max_r:
                    max_r = r_p
                    max_r_examples = []
                if r_p == max_r and len(max_r_examples) < 10:
                    max_r_examples.append({"p": p, "R": r_p})

        collision_energy += 2 * multiplicities[a_n] + 1
        multiplicities[a_n] += 1
        if rank > max_multiplicity:
            max_multiplicity, max_value = rank, a_n
        for d, _ in signed_divisors(factors(a_n, spf)):
            divisor_counts[d] += 1
        if n == next_checkpoint or n == limit:
            rows.append({
                "N": n,
                "max_value_multiplicity": max_multiplicity,
                "one_value_attaining_max": max_value,
                "collision_energy_sum_multiplicity_squared": collision_energy,
                "collision_energy_over_N": collision_energy / n,
                "max_multiplicity_over_log_N": max_multiplicity / log(n),
                "prime_samples_2p_le_N": prime_samples,
                "max_R": max_r,
                "max_R_examples_up_to_ten": list(max_r_examples),
            })
            next_checkpoint *= 10

    assert prefix == literal(checked)
    assert sum(multiplicities) == limit
    assert collision_energy == sum(m * m for m in multiplicities)
    return {
        "limit": limit,
        "literal_check_terms": checked,
        "coprime_position_rank_checks": coprime_position_checks,
        "scope": "Finite exact computation; no asymptotic bound proved.",
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--literal-terms", type=int, default=3000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit < 1000 or args.literal_terms < 2:
        parser.error("--limit >= 1000 and --literal-terms >= 2 are required")
    result = run(args.limit, args.literal_terms)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
