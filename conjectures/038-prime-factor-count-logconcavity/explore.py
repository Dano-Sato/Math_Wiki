"""Exact finite check for conjecture 038.

For every x <= limit, count integers m <= x by omega(m), the number of
distinct prime factors, then test log-concavity using arbitrary-precision
integer arithmetic. The result is finite evidence only.
"""

import argparse
import json


def check(limit: int) -> dict:
    omega = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if omega[p] == 0:
            for multiple in range(p, limit + 1, p):
                omega[multiple] += 1

    counts = [1] + [0] * (limit.bit_length() + 1)  # omega(1) = 0
    checks = 0
    first_failure = None
    max_omega = 0
    for x in range(2, limit + 1):
        k_new = omega[x]
        counts[k_new] += 1
        max_omega = max(max_omega, k_new)
        for k in range(1, max_omega):
            checks += 1
            margin = counts[k] ** 2 - counts[k - 1] * counts[k + 1]
            if margin < 0 and first_failure is None:
                first_failure = {
                    "x": x,
                    "k": k,
                    "counts": counts[: max_omega + 1],
                    "margin": margin,
                }

    return {
        "conjecture": "038-v0.1",
        "limit_x": limit,
        "cutoffs_checked": limit,
        "log_concavity_inequalities_checked": checks,
        "first_failure": first_failure,
        "max_omega": max_omega,
        "counts_at_limit": counts[: max_omega + 1],
        "arithmetic": "exact integer arithmetic",
        "independent_implementation": False,
        "scope_note": "Finite verification only; not a proof for all x.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2_000_000)
    args = parser.parse_args()
    print(json.dumps(check(args.limit), indent=2))
