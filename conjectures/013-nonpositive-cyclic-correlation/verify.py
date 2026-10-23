"""Exact integer verification of the finite certificates for conjecture 013."""

import json
from pathlib import Path


def correlations(permutation):
    n = len(permutation)
    centered = [2 * value - (n + 1) for value in permutation]
    return [
        sum(centered[i] * centered[(i + k) % n] for i in range(n))
        for k in range(1, n // 2 + 1)
    ]


def main():
    path = Path(__file__).with_name("certificates.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data["permutations"]
    for n_text, permutation in entries.items():
        n = int(n_text)
        assert n >= 3
        assert len(permutation) == n
        assert sorted(permutation) == list(range(1, n + 1))
        values = correlations(permutation)
        assert all(value <= 0 for value in values), (n, values)
        print(f"n={n}: C={values}")
    print(f"verified {len(entries)} certificates")


if __name__ == "__main__":
    main()
