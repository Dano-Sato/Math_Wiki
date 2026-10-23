from __future__ import annotations

import argparse
import json
from pathlib import Path


def primes_upto(n: int) -> list[int]:
    sieve = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        sieve[0] = 0
    if n >= 1:
        sieve[1] = 0
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : n + 1 : p] = b"\x00" * (((n - start) // p) + 1)
    return [p for p in range(3, n + 1) if sieve[p]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Exact counts of compositions into odd prime parts.")
    parser.add_argument("--max-n", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("experiment.json"))
    args = parser.parse_args()
    N = args.max_n
    if N < 3:
        raise SystemExit("--max-n must be at least 3")

    primes = primes_upto(N)
    # c[n][k] = number of ordered compositions of n into exactly k odd primes.
    c = [[0] * (N + 1) for _ in range(N + 1)]
    c[0][0] = 1
    for n in range(1, N + 1):
        row = c[n]
        for p in primes:
            if p > n:
                break
            prev = c[n - p]
            for k in range(1, n // 3 + 1):
                row[k] += prev[k - 1]

    inequalities = 0
    minimum_slack: tuple[int, int, int] | None = None
    support_interval_checks = 0
    largest_count_bits = 0
    support_examples: dict[str, list[int]] = {}
    for n in range(3, N + 1):
        parity = n % 2
        ks = list(range(2 if parity == 0 else 1, n // 3 + 1, 2))
        positive = [k for k in ks if c[n][k] > 0]
        if not positive:
            continue
        lo, hi = positive[0], positive[-1]
        support = list(range(lo, hi + 1, 2))
        if any(c[n][k] == 0 for k in support):
            raise AssertionError(f"internal support gap for n={n}, k={support}")
        support_interval_checks += 1
        if n in {3, 11, 17, 100, N}:
            support_examples[str(n)] = [lo, hi]
        for k in support:
            largest_count_bits = max(largest_count_bits, c[n][k].bit_length())
        for j in range(1, len(support) - 1):
            k = support[j]
            slack = c[n][k] ** 2 - c[n][k - 2] * c[n][k + 2]
            inequalities += 1
            if slack <= 0:
                raise AssertionError(f"log-concavity failed at n={n}, k={k}, slack={slack}")
            if minimum_slack is None or slack < minimum_slack[0]:
                minimum_slack = (slack, n, k)

    result = {
        "claim_id": "030",
        "definition": "c(n,k) counts ordered compositions of n into exactly k odd primes (2 excluded)",
        "max_n": N,
        "arithmetic": "exact integer dynamic programming: c(n,k)=sum_{p odd prime <= n} c(n-p,k-1)",
        "n_values_with_nonempty_support_checked": support_interval_checks,
        "log_concavity_inequalities_checked": inequalities,
        "minimum_positive_slack": (
            {"value": str(minimum_slack[0]), "n": minimum_slack[1], "k": minimum_slack[2]}
            if minimum_slack
            else None
        ),
        "largest_coefficient_bit_length": largest_count_bits,
        "support_interval_checked": True,
        "sample_support_endpoints": support_examples,
        "scope_warning": "Finite computation only; it is not a proof for all n.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
