"""Contrast for conjecture 038 (Claude): the same log-concavity with Omega (prime factors counted
with multiplicity) instead of omega fails, already at x = 16 and repeatedly afterwards.

    python omega_multiplicity_check.py --limit 3000000
"""

import argparse
import collections
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=3_000_000)
    args = parser.parse_args()
    n = args.limit
    big_omega = [0] * (n + 1)
    for p in range(2, n + 1):
        if big_omega[p] == 0:
            pk = p
            while pk <= n:
                for m in range(pk, n + 1, pk):
                    big_omega[m] += 1
                pk *= p
    counts = [0] * 64
    counts[0] = 1
    failures = []
    for x in range(2, n + 1):
        j = big_omega[x]
        counts[j] += 1
        for k in (j - 1, j + 1):  # only these can newly fail (see verify_claude.go)
            if k >= 1 and counts[k - 1] and counts[k + 1] and counts[k] ** 2 < counts[k - 1] * counts[k + 1]:
                failures.append((x, k))
    by_digits = collections.Counter(len(str(x)) for x, _ in failures)
    print(json.dumps({
        "limit_x": n,
        "failures": len(failures),
        "first_failures": failures[:5],
        "last_failures": failures[-3:],
        "failures_by_number_of_digits_of_x": dict(sorted(by_digits.items())),
        "scope": "Finite computation; shows the Omega analogue of 038 is false.",
    }, indent=2))


if __name__ == "__main__":
    main()
