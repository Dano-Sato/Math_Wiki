"""Independently separate prime-index and composite-index errors in 004.

Run from the repository root with

    python conjectures/004-self-totient/bias_decomposition.py --terms 1000000

The finite calculation uses integer inclusion-exclusion for both a_n and the
exact prime-index contribution. It checks the first 3000 terms literally.
"""

import argparse
import json
from array import array
from math import gcd, sqrt
from pathlib import Path

from review_verify import factors, signed_divisors, sieve


def empty_stats():
    return {key: {"sum": 0.0, "square": 0.0, "max_abs": 0.0}
            for key in ("prime", "composite", "total", "unmodeled")}


def summarize(stats, count):
    return {
        key: {
            "mean": item["sum"] / count,
            "rms": sqrt(item["square"] / count),
            "max_abs": item["max_abs"],
        }
        for key, item in stats.items()
    }


def run(limit, seed=1):
    if not 1 <= seed <= limit:
        raise ValueError("a_1 must be between 1 and the term limit")
    spf = sieve(limit)
    first_missing_prime = next(
        p for p in range(2, limit + 1) if spf[p] == p and seed % p != 0
    )
    shift = first_missing_prime - 1
    all_counts = array("I", [0]) * (limit + 1)
    prime_counts = array("I", [0]) * (limit + 1)
    for d, _ in signed_divisors(factors(seed, spf)):
        all_counts[d] += 1
    prefix = [0, seed]
    prime_indices = 0
    checkpoints = []
    window_start = 101
    next_checkpoint = 1000
    by_parity = {"all": [0, empty_stats()],
                 "even": [0, empty_stats()],
                 "odd": [0, empty_stats()]}

    def update(group, components):
        count, stats = by_parity[group]
        by_parity[group][0] = count + 1
        for key, value in components.items():
            stats[key]["sum"] += value
            stats[key]["square"] += value * value
            stats[key]["max_abs"] = max(stats[key]["max_abs"], abs(value))

    for n in range(2, limit + 1):
        prime_factors = factors(n, spf)
        divisors = signed_divisors(prime_factors)
        a_n = sum(sign * all_counts[d] for d, sign in divisors)
        p_n = sum(sign * prime_counts[d] for d, sign in divisors)
        phi_n = n
        product = 1.0
        for q in prime_factors:
            phi_n = phi_n // q * (q - 1)
            if shift % q != 0:
                product *= (q - 2) / (q - 1)
        if n <= 3000:
            assert a_n == sum(gcd(x, n) == 1 for x in prefix[1:]), n
            assert p_n == sum(gcd(prefix[p], n) == 1
                              for p in range(2, n) if spf[p] == p), n
            prefix.append(a_n)
        if spf[n] == n:
            if n < first_missing_prime:
                assert a_n == 0, n
            else:
                assert a_n == n - shift - int(seed % n == 0), n
        if n > 100:
            scale = phi_n * prime_indices / n
            prime_error = (p_n - prime_indices * product) / scale
            composite_error = (a_n - p_n -
                               (n - 1 - prime_indices) * phi_n / n) / scale
            components = {"prime": prime_error,
                          "composite": composite_error,
                          "total": prime_error + composite_error,
                          "unmodeled": (a_n - phi_n) / scale}
            update("all", components)
            update("even" if n % 2 == 0 else "odd", components)
        if spf[n] == n:
            prime_indices += 1
        # A zero term is not coprime to any later n>1. Its contributions to
        # the Mobius sum cancel, so the divisor tables omit it entirely.
        if a_n > 0:
            for d, _ in signed_divisors(factors(a_n, spf)):
                all_counts[d] += 1
                if spf[n] == n:
                    prime_counts[d] += 1
        if n == next_checkpoint or n == limit:
            checkpoints.append({
                "n": n,
                "window": [window_start, n],
                "by_parity": {
                    group: summarize(stats, count)
                    for group, (count, stats) in by_parity.items()
                },
            })
            window_start = n + 1
            by_parity = {"all": [0, empty_stats()],
                         "even": [0, empty_stats()],
                         "odd": [0, empty_stats()]}
            next_checkpoint *= 10
    return {
        "a1": seed,
        "first_prime_not_dividing_a1": first_missing_prime,
        "eventual_prime_formula": "a_p = p - first_prime_not_dividing_a1 + 1 for p>a1",
        "terms": limit,
        "literal_check_terms": min(limit, 3000),
        "normalization": "phi(n) * #{primes p<n} / n",
        "exact_identity": "total error = [P(n)-pi*g(n)] + [Q(n)-(n-1-pi)*phi(n)/n]",
        "scope": "Finite independent Python computation; not a proof of any limit.",
        "checkpoints": checkpoints,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", type=int, default=1000000)
    parser.add_argument("--a1", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.terms < 1000:
        parser.error("--terms must be at least 1000")
    result = run(args.terms, args.a1)
    output = args.output or Path(__file__).with_name(
        f"bias_decomposition_a1_{args.a1}.json"
    )
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps(result["checkpoints"][-1], ensure_ascii=True))


if __name__ == "__main__":
    main()
