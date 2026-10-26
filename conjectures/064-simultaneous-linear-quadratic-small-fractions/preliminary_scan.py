"""Exploratory double-precision scan for quadratic irrational examples.

The recurrence tracks {n alpha} and {n^2 alpha} without multiplying alpha by
large n or n^2 at each step. This is only a finite numerical check.
"""

import json
import math
from pathlib import Path


def scan(alpha, limit, epsilons):
    linear = 0.0
    quadratic = 0.0
    difference = alpha  # (n+1)^2 alpha - n^2 alpha at n=0
    hits = {eps: [] for eps in epsilons}
    for n in range(1, limit + 1):
        linear = (linear + alpha) % 1.0
        quadratic = (quadratic + difference) % 1.0
        difference = (difference + 2 * alpha) % 1.0
        value = max(min(linear, 1.0 - linear), min(quadratic, 1.0 - quadratic))
        for eps in epsilons:
            if value < n ** (-0.5 + eps):
                hits[eps].append((n, value))
    return {
        str(eps): {"count": len(ns), "last_five": ns[-5:]}
        for eps, ns in hits.items()
    }


def main():
    limit = 2_000_000
    epsilons = (0.01, 0.05, 0.1)
    alphas = {
        "sqrt2_minus_1": math.sqrt(2) - 1,
        "golden_ratio_inverse": (math.sqrt(5) - 1) / 2,
        "sqrt3_minus_1": math.sqrt(3) - 1,
    }
    result = {
        "method": "double-precision modular recurrences for {n alpha} and {n^2 alpha}; exploratory only",
        "limit": limit,
        "epsilons": epsilons,
        "examples": {name: scan(alpha, limit, epsilons) for name, alpha in alphas.items()},
        "scope": "Finite floating-point scan; no proof, and no conclusion for other badly approximable numbers.",
    }
    Path(__file__).with_name("preliminary_scan.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
