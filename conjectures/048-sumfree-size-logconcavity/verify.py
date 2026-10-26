"""Exact enumeration for conjecture 048 (finite range only)."""

from __future__ import annotations

import json
import sys


def enumerate_profiles(limit: int) -> list[dict[str, object]]:
    """Return exact size profiles for sum-free subsets of [n], n <= limit."""
    sets = [0]
    profiles = []

    for n in range(1, limit + 1):
        added = []
        for mask in sets:
            # Adding n is legal precisely when the old set has no x+y=n.
            # The range includes x=y=n/2 when n is even.
            legal = True
            for x in range(1, n // 2 + 1):
                y = n - x
                if ((mask >> (x - 1)) & 1) and ((mask >> (y - 1)) & 1):
                    legal = False
                    break
            if legal:
                added.append(mask | (1 << (n - 1)))
        sets.extend(added)

        counts = [0] * (n + 1)
        for mask in sets:
            counts[mask.bit_count()] += 1
        last_nonzero = max(i for i, value in enumerate(counts) if value)
        counts = counts[: last_nonzero + 1]
        failures = [
            k
            for k in range(1, len(counts) - 1)
            if counts[k] * counts[k] < counts[k - 1] * counts[k + 1]
        ]
        profiles.append(
            {
                "n": n,
                "total": len(sets),
                "counts": counts,
                "log_concavity_failures_at_k": failures,
            }
        )

    return profiles


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    if limit < 1:
        raise SystemExit("limit must be positive")
    print(json.dumps(enumerate_profiles(limit), indent=2))
