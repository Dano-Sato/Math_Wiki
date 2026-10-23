"""Exact finite search for conjecture 026, using only Python's standard library."""

from math import comb
import json
from pathlib import Path


def mobius(n: int) -> int:
    """Return the number-theoretic Möbius function of n."""
    x = n
    sign = 1
    p = 2
    while p * p <= x:
        if x % p == 0:
            x //= p
            sign = -sign
            if x % p == 0:
                return 0
            while x % p == 0:
                x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        sign = -sign
    return sign


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def coefficients(n: int) -> list[int]:
    """Return g_1(n), ..., g_n(n) by divisor-lattice Möbius inversion."""
    terms = [(d, mobius(d)) for d in divisors(n)]
    return [
        sum(mu * comb(n // d, k) for d, mu in terms if mu and k <= n // d)
        for k in range(1, n + 1)
    ]


def main() -> None:
    per_order = []
    minimum_slack = None
    minimum_location = None
    checked_inequalities = 0
    for n in range(2, 301):
        a = coefficients(n)
        slacks = []
        for k in range(2, n):
            # a[j] is g_{j+1}(n).
            slack = a[k - 1] ** 2 - a[k - 2] * a[k]
            if slack <= 0:
                raise AssertionError(f"Conjecture fails at n={n}, k={k}: {slack}")
            slacks.append((slack, k))
        checked_inequalities += len(slacks)
        if slacks:
            local_slack, local_k = min(slacks)
            per_order.append(
                {
                    "n": n,
                    "coefficients_first_three": a[:3],
                    "coefficients_last_three": a[-3:],
                    "minimum_slack": local_slack,
                    "minimum_slack_k": local_k,
                }
            )
            if minimum_slack is None or local_slack < minimum_slack:
                minimum_slack = local_slack
                minimum_location = {"n": n, "k": local_k}
        else:
            per_order.append(
                {
                    "n": n,
                    "coefficients_first_three": a[:3],
                    "coefficients_last_three": a[-3:],
                    "minimum_slack": None,
                    "minimum_slack_k": None,
                }
            )

    output = {
        "scope": "all cyclic groups C_n for 2 <= n <= 300",
        "method": "exact integer coefficients from sum_{d|n} mu(d) * binomial(n/d,k), followed by exact adjacent log-concavity differences",
        "checked_inequalities": checked_inequalities,
        "all_strictly_positive": True,
        "globally_smallest_slack_in_scope": minimum_slack,
        "location_of_smallest_slack": minimum_location,
        "per_order_summary": per_order,
        "limitation": "finite computation only; this does not prove the conjecture for n > 300",
    }
    target = Path(__file__).with_name("experiment.json")
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "per_order_summary"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
