"""Conjecture 006: maximum matching versus the modulo-three obstruction."""

import json
from collections import deque
from math import isqrt
from pathlib import Path


def sieve(limit):
    prime = bytearray(b"\1") * (limit + 1)
    prime[:2] = b"\0\0"
    for p in range(2, isqrt(limit) + 1):
        if prime[p]:
            prime[p * p::p] = b"\0" * ((limit - p * p) // p + 1)
    return prime


def internal_matching(n, prime):
    # The two residue classes 1,2 mod 3 form disjoint paths with step 3.
    used = set()
    pairs = []
    for x in range(1, 2 * n - 2):
        if x % 3 and x not in used and x + 3 not in used and prime[2 * x + 3]:
            used.update((x, x + 3))
            pairs.append([x, x + 3])
    return pairs


def maximum_matching(n, prime):
    adjacency = [
        [j for j in range(n) if prime[2 * i + 1 + 2 * j + 2] and prime[abs(2 * i + 1 - (2 * j + 2))]]
        for i in range(n)
    ]
    left, right = [-1] * n, [-1] * n
    while True:
        distance = [-1] * n
        queue = deque()
        for u in range(n):
            if left[u] < 0:
                distance[u] = 0
                queue.append(u)
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                other = right[v]
                if other >= 0 and distance[other] < 0:
                    distance[other] = distance[u] + 1
                    queue.append(other)

        def augment(u):
            for v in adjacency[u]:
                other = right[v]
                if other < 0 or (distance[other] == distance[u] + 1 and augment(other)):
                    left[u], right[v] = v, u
                    return True
            distance[u] = -1
            return False

        changes = sum(augment(u) for u in range(n) if left[u] < 0)
        if not changes:
            break
    return [[2 * u + 1, 2 * v + 2] for u, v in enumerate(left) if v >= 0]


def trial_prime(value):
    return value >= 2 and all(value % d for d in range(2, isqrt(value) + 1))


def run():
    sizes = [*range(1, 101), 150, 200, 300, 500, 1000, 2000, 5000, 7425, 7426, 8000, 10000]
    prime = sieve(4 * max(sizes))
    rows = []
    for n in sizes:
        internal = internal_matching(n, prime)
        predicted = min(n, 2 * n // 3 + len(internal))
        pairs = maximum_matching(n, prime)
        used = [v for pair in pairs for v in pair]
        assert len(used) == len(set(used)) and all(1 <= v <= 2 * n for v in used)
        assert all(trial_prime(x + y) and trial_prime(abs(x - y)) for x, y in pairs)
        # Attaining the rigorous upper bound certifies optimality independently
        # of the maximum-matching algorithm's completeness.
        row = {"n": n, "kappa": len(internal), "predicted_maximum": predicted,
               "found_pairs": len(pairs), "matches_prediction": len(pairs) == predicted,
               "pairs": pairs, "internal_pairs": internal}
        rows.append(row)
        if n >= 1000:
            print({key: row[key] for key in ("n", "kappa", "predicted_maximum", "found_pairs", "matches_prediction")}, flush=True)
    output = {"definition_version": "006-0.1", "date": "2026-10-24", "rows": rows,
              "failed_prediction_sizes": [r["n"] for r in rows if not r["matches_prediction"]],
              "scope": "Finite computations; optimum certified by upper-bound attainment where matches_prediction is true."}
    Path(__file__).with_name("bottleneck_experiment.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
