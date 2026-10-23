"""Finite search for conjecture 002; Python standard library only."""

import argparse
import json
from itertools import permutations
from math import exp
from pathlib import Path
from random import Random


def widths(order):
    n = len(order)
    pairs = [order[i] + order[(i + 1) % n] for i in range(n)]
    triples = [pairs[i] + order[(i + 2) % n] for i in range(n)]
    return max(pairs) - min(pairs), max(triples) - min(triples)


def check_witness(order, bound):
    """Check the certificate using separate literal circular window sums."""
    n = len(order)
    if sorted(order) != list(range(1, n + 1)):
        raise ValueError("Not a permutation of 1,...,n")
    extended = list(order) + list(order)
    ranges = []
    for window in (2, 3):
        sums = [sum(extended[i:i + window]) for i in range(n)]
        ranges.append(max(sums) - min(sums))
    if tuple(ranges) != widths(order):
        raise AssertionError("Independent width calculations disagree")
    if max(ranges) > bound:
        raise ValueError("Certificate exceeds the requested bound")
    return ranges


def feasible(n, bound):
    """Exhaustive DFS, pruning only monotonically increasing partial ranges.

    Rotation fixes the first entry to 1. Reversal allows second < last.
    No node or time cutoff is used, so a None result proves finite infeasibility.
    """
    path = [1]
    nodes = 0

    def visit(mask, lo2, hi2, lo3, hi3):
        nonlocal nodes
        nodes += 1
        for value in range(2, n + 1):
            bit = 1 << value
            if mask & bit:
                continue
            pair = path[-1] + value
            low2, high2 = min(lo2, pair), max(hi2, pair)
            if high2 - low2 > bound:
                continue
            low3, high3 = lo3, hi3
            if len(path) >= 2:
                triple = path[-2] + path[-1] + value
                low3, high3 = min(lo3, triple), max(hi3, triple)
                if high3 - low3 > bound:
                    continue
            if len(path) == n - 1:
                if path[1] > value:
                    continue
                low2, high2 = min(low2, value + 1), max(high2, value + 1)
                closing = (path[-1] + value + 1, value + 1 + path[1])
                low3, high3 = min(low3, *closing), max(high3, *closing)
                if max(high2 - low2, high3 - low3) <= bound:
                    return path + [value]
                continue
            path.append(value)
            result = visit(mask | bit, low2, high2, low3, high3)
            path.pop()
            if result is not None:
                return result
        return None

    witness = visit(1 << 1, 10 * n, -1, 10 * n, -1)
    return witness, nodes


def literal_optimum(n):
    """Independent full enumeration, without DFS pruning, for small n."""
    return min(max(widths((1,) + tail)) for tail in permutations(range(2, n + 1)))


def normalize(order):
    index = order.index(1)
    rotated = order[index:] + order[:index]
    return min(rotated, rotated[:1] + rotated[:0:-1])


def anneal(n, attempts, steps):
    """Find certificates; failure to find one is not a lower bound."""
    rng = Random(20261023 + n)
    target = n // 2 + 1
    best = 10 * n
    best_order = None
    for attempt in range(attempts):
        order = list(range(1, n + 1))
        rng.shuffle(order)
        x, y = widths(order)
        energy = max(x, y) + 0.05 * (x + y)
        if max(x, y) < best:
            best, best_order = max(x, y), order.copy()
        for step in range(steps):
            i, j = rng.sample(range(n), 2)
            order[i], order[j] = order[j], order[i]
            x, y = widths(order)
            new_energy = max(x, y) + 0.05 * (x + y)
            temperature = max(0.08, 2.5 * (1 - step / steps) ** 2)
            if new_energy <= energy or rng.random() < exp((energy - new_energy) / temperature):
                energy = new_energy
                if max(x, y) < best:
                    best, best_order = max(x, y), order.copy()
                if best <= target:
                    return normalize(best_order), attempt + 1
            else:
                order[i], order[j] = order[j], order[i]
    return normalize(best_order), attempts


def run(attempts, steps):
    exact_rows = []
    for n in range(3, 13):
        trials = []
        for bound in range(n // 2, n // 2 + 2):
            order, nodes = feasible(n, bound)
            trials.append({"bound": bound, "found": order is not None, "nodes": nodes})
            if order is not None:
                break
        if order is None:
            raise RuntimeError(f"Conjecture fails in exact search at n={n}")
        ranges = check_witness(order, bound)
        if n <= 9 and literal_optimum(n) != bound:
            raise AssertionError("Literal enumeration disagrees with DFS")
        exact_rows.append({"n": n, "optimum": bound, "widths": ranges, "witness": order, "trials": trials})

    certificate_rows = []
    for n in [13, *range(14, 25), 30, 40]:
        order, attempts_used = anneal(n, attempts, steps)
        ranges = check_witness(order, max(widths(order)))
        certificate_rows.append({
            "n": n,
            "conjectured_bound": n // 2 + 1,
            "witness_widths": ranges,
            "witness": order,
            "satisfies_conjectured_bound": max(ranges) <= n // 2 + 1,
            "attempts_used": attempts_used,
        })
    return {
        "definition_version": "002-0.1",
        "exact_search": exact_rows,
        "literal_enumeration_checked_through": 9,
        "certificate_search": certificate_rows,
        "heuristic_settings": {"seed": "20261023+n", "attempts": attempts, "steps_per_attempt": steps},
        "scope": "Exact minima only for n=3,...,12. Other rows are checked existence certificates, not optimality proofs. No general proof.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempts", type=int, default=20)
    parser.add_argument("--steps", type=int, default=100000)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("experiment.json"))
    args = parser.parse_args()
    if args.attempts < 1 or args.steps < 1:
        parser.error("--attempts and --steps must be positive")
    result = run(args.attempts, args.steps)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in result["exact_search"]:
        print(f"exact n={row['n']}: optimum={row['optimum']}, widths={row['widths']}")
    for row in result["certificate_search"]:
        print(f"certificate n={row['n']}: widths={row['witness_widths']}, meets_bound={row['satisfies_conjectured_bound']}")


if __name__ == "__main__":
    main()
