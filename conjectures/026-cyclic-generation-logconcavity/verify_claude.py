"""Independent check of conjecture 026 and the stronger 026-1 (Claude).

    python verify_claude.py --max 1200 --output verify_claude.json

g_k(n) = sum_{d | n} mu(d) C(n/d, k)  (written independently of explore.py).
026   : g_k^2 > g_{k-1} g_{k+1}                     for 2 <= k <= n-1.
026-1 : h_k = g_k / C(n,k) is log-concave in k, i.e. h_k^2 >= h_{k-1} h_{k+1},
        equivalently g_k^2 (k (n-k)) >= g_{k-1} g_{k+1} (k+1)(n-k+1).
026-1 implies 026 because C(n,k) is strictly log-concave.
Exact integer arithmetic throughout. The literal count of generating subsets is
compared with the formula by brute force for n <= 14.
"""

import argparse
import json
from itertools import combinations
from math import comb, gcd


def mobius_table(limit):
    mu = [1] * (limit + 1)
    is_comp = [False] * (limit + 1)
    primes = []
    mu[0] = 0
    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > limit:
                break
            is_comp[i * p] = True
            if i % p == 0:
                mu[i * p] = 0
                break
            mu[i * p] = -mu[i]
    return mu


def coefficients(n, mu):
    ds = [d for d in range(1, n + 1) if n % d == 0 and mu[d] != 0]
    return [0] + [sum(mu[d] * comb(n // d, k) for d in ds if k <= n // d) for k in range(1, n + 1)]


def brute(n):
    """Literal count of k-subsets of Z_n generating Z_n (gcd of elements with n is 1)."""
    out = [0] * (n + 1)
    for k in range(1, n + 1):
        for subset in combinations(range(n), k):
            g = n
            for a in subset:
                g = gcd(g, a)
            if g == 1:
                out[k] += 1
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max", type=int, default=1200)
    parser.add_argument("--output", default="verify_claude.json")
    args = parser.parse_args()
    mu = mobius_table(args.max)
    for n in range(2, 15):
        if coefficients(n, mu) != brute(n):
            raise AssertionError(f"formula disagrees with brute force at n={n}")
    fails_026, fails_strong, equal_strong = [], [], 0
    checked = 0
    for n in range(2, args.max + 1):
        g = coefficients(n, mu)
        for k in range(2, n):
            checked += 1
            lhs, rhs = g[k] * g[k], g[k - 1] * g[k + 1]
            if lhs <= rhs:
                fails_026.append((n, k))
            s_lhs, s_rhs = lhs * k * (n - k), rhs * (k + 1) * (n - k + 1)
            if s_lhs < s_rhs:
                fails_strong.append((n, k))
            elif s_lhs == s_rhs:
                equal_strong += 1
    result = {
        "implementation": "verify_claude.py (Claude, independent of explore.py)",
        "checked_n": [2, args.max],
        "brute_force_formula_check_n": [2, 14],
        "inequalities_checked": checked,
        "failures_026": fails_026[:20],
        "failures_026_1": fails_strong[:20],
        "equalities_in_026_1": equal_strong,
        "scope": "Exact finite verification for 2 <= n <= max.",
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
