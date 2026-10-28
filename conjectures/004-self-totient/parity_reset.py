"""Check the exact parity reset and pair decomposition in discussion D024.

This evaluates the original recurrence, not a truncated-prime model.
No asymptotic cancellation is asserted by this experiment.
"""

import argparse
import json
from array import array
from pathlib import Path

from review_verify import factors, literal, signed_divisors, sieve


def run(limit, literal_terms):
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    odd_divisor_counts = array("I", [0]) * (limit + 1)
    counts[1] = odd_divisor_counts[1] = 1
    odd_count = 1
    previous_defect_bit = 0
    previous_odd_bit = 1
    signed_sum = 0
    initial_sum = 0
    composite_sum = 0
    prime_stationary = 0
    odd_prime_count = 0
    stationary = 0
    prefix = [0, 1]
    checked = min(limit, literal_terms)
    rows = []
    next_checkpoint = 1000

    for n in range(2, limit + 1):
        ps = factors(n, spf)
        value = sum(sign * counts[d] for d, sign in signed_divisors(ps))
        assert 1 <= value < n
        if n <= checked:
            prefix.append(value)
        if n % 2 == 0:
            defect = odd_count - value
            # Directly count odd previous values sharing an odd factor of n.
            odd_ps = [p for p in ps if p != 2]
            direct = odd_count - sum(sign * odd_divisor_counts[d]
                                     for d, sign in signed_divisors(odd_ps))
            assert defect == direct >= 0, (n, defect, direct)
            bit = defect % 2
            even_bit = value % 2
            assert even_bit == (previous_defect_bit ^ previous_odd_bit ^ bit)
            flag = int(bit == previous_defect_bit)
            contribution = (2 * previous_odd_bit - 1) * flag
            assert previous_odd_bit + even_bit - 1 == contribution
            signed_sum += contribution
            stationary += flag
            if n == 2:
                initial_sum += contribution
            elif spf[n - 1] == n - 1:
                assert previous_odd_bit == 0
                odd_prime_count += 1
                prime_stationary += flag
            else:
                composite_sum += contribution
            previous_defect_bit = bit
        else:
            previous_odd_bit = value % 2

        odd_count += value % 2
        ds = signed_divisors(factors(value, spf))
        for d, _ in ds:
            counts[d] += 1
            if value % 2:
                odd_divisor_counts[d] += 1
        if n % 2 == 0:
            assert odd_count % 2 == previous_defect_bit
            assert odd_count - n // 2 == signed_sum
            assert signed_sum == initial_sum - prime_stationary + composite_sum
            if n == next_checkpoint or n == limit:
                rows.append({
                    "N": n,
                    "odd_terms_up_to_N": odd_count,
                    "odd_density": odd_count / n,
                    "odd_count_minus_N_over_2": signed_sum,
                    "equal_defect_bit_pairs": stationary,
                    "equal_defect_bit_fraction": stationary / (n // 2),
                    "odd_prime_indices_before_N": odd_prime_count,
                    "prime_equal_defect_bit_pairs": prime_stationary,
                    "prime_equal_defect_bit_fraction": prime_stationary / odd_prime_count,
                    "signed_odd_composite_contribution": composite_sum,
                    "signed_odd_composite_contribution_over_odd_primes": composite_sum / odd_prime_count,
                    "initial_contribution": initial_sum,
                    "crude_absolute_bound_equal_pairs": stationary,
                })
                next_checkpoint *= 10

    assert prefix == literal(checked)
    return {
        "limit": limit,
        "literal_check_terms": checked,
        "scope": "Exact finite identities verified; no limiting parity density proved.",
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--literal-terms", type=int, default=3000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit < 1000 or args.limit % 2 or args.literal_terms < 2:
        parser.error("an even --limit >= 1000 and --literal-terms >= 2 are required")
    result = run(args.limit, args.literal_terms)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
