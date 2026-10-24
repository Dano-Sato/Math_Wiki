"""Exact bounded-alphabet exclusion for 2-free gcd-plus-one periodic orbits.

This is a finite certificate, NOT a proof for every alphabet bound. The transfer
argument and the dependence on the proved cycle bound are in conjectures.md L5.
The existing exhaustive experiment.json is preserved.
"""

import argparse
import hashlib
import json
from math import gcd
from pathlib import Path


def update(a, b):
    return gcd(a, b) + 1


def initial_pairs(bound):
    return {
        (a, b)
        for a in range(3, bound + 1)
        for b in range(3, bound + 1)
        if 3 <= update(a, b) <= bound
    }


def prune_fast(pairs):
    """Symmetry permits the same predecessor/output set on both sides."""
    assert all((b, a) in pairs for a, b in pairs)
    outputs = {}
    for a, b in pairs:
        outputs.setdefault(b, set()).add(update(a, b))
    image = {(c, d) for values in outputs.values() for c in values for d in values}
    return pairs & image


def prune_reference(pairs):
    """Direct image of all length-two directed walks; no symmetry shortcut."""
    successors = {}
    for b, c in pairs:
        successors.setdefault(b, []).append(c)
    image = {
        (update(a, b), update(b, c))
        for a, b in pairs
        for c in successors.get(b, [])
    }
    return pairs & image


def summary(pairs, round_number):
    digest = hashlib.sha256()
    for a, b in sorted(pairs):
        digest.update(f"{a},{b}\n".encode("ascii"))
    off_diagonal = sorted((a, b) for a, b in pairs if a != b)
    result = {
        "round": round_number,
        "pairs": len(pairs),
        "off_diagonal_pairs": len(off_diagonal),
        "sha256_sorted_ascii_pairs": digest.hexdigest(),
    }
    if len(off_diagonal) <= 20:
        result["remaining_off_diagonal_pairs"] = [list(pair) for pair in off_diagonal]
    return result


def reference_checks():
    rounds = 0
    for bound in range(3, 21):
        pairs = initial_pairs(bound)
        while True:
            fast = prune_fast(pairs)
            reference = prune_reference(pairs)
            assert fast == reference
            rounds += 1
            if not any(a != b for a, b in fast) or fast == pairs:
                assert not any(a != b for a, b in fast)
                break
            pairs = fast
    return rounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.bound < 3:
        parser.error("bound must be at least 3")
    reference_rounds = reference_checks()
    pairs = initial_pairs(args.bound)
    trace = []
    while True:
        row = summary(pairs, len(trace))
        trace.append(row)
        if row["off_diagonal_pairs"] == 0:
            break
        new_pairs = prune_fast(pairs)
        if new_pairs == pairs:
            break
        pairs = new_pairs
    excluded = trace[-1]["off_diagonal_pairs"] == 0
    result = {
        "date": "2026-10-24",
        "definition_version": "009-0.2",
        "alphabet": [3, args.bound],
        "update": "gcd(a,b)+1",
        "recurrence": "E_(r+1) = E_r intersect {(f(a,b), f(b,c)) : (a,b),(b,c) in E_r}",
        "exact_integer_arithmetic": True,
        "reference_implementation_checked_bounds": [3, 20],
        "reference_implementation_rounds_checked": reference_rounds,
        "trace": trace,
        "terminal_pairs_all_diagonal": excluded,
        "two_free_periodic_orbits_excluded_for_this_alphabet": excluded,
        "ring_size_bound_using_L2": (args.bound + 2) // 2 if excluded else None,
        "scope": "Excludes every period and ring length whose periodic values lie in this finite alphabet. Together with L2, proves 009 and (by L4) 009-1 only for 2 <= n <= the stated ring-size bound. Not a classification of cycles, not a proof for unbounded n, and not Lean-certified.",
    }
    output = args.output or Path(__file__).with_name(f"pair_prune_{args.bound}.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not excluded:
        print("Nonempty off-diagonal fixed point is inconclusive; it is not a counterexample.")


if __name__ == "__main__":
    main()
