"""Exact finite-state audit of a proposed proof route for conjecture 004.

This studies b[1] = 1 and b[n] = #{k < n: gcd(b[k], n, P) = 1},
not the original recurrence.  No result here proves 004 or its negation.
For P=2 and P=6, a repeated finite state certifies an infinite periodic
residue sequence.  The full integer values need not be periodic.
"""

import argparse
import json
from collections import Counter
from fractions import Fraction
from math import gcd
from pathlib import Path


def literal_truncated(modulus, limit):
    values = [0, 1]
    for n in range(2, limit + 1):
        values.append(sum(gcd(v, n, modulus) == 1 for v in values[1:]))
    return values


def literal_original(limit):
    values = [0, 1]
    for n in range(2, limit + 1):
        values.append(sum(gcd(v, n) == 1 for v in values[1:]))
    return values


def exact_cycle(modulus, search_limit):
    classes = [d for d in range(1, modulus + 1) if modulus % d == 0]
    counts = {d: int(d == 1) for d in classes}
    values = [0, 1]
    seen = {}
    full_states = {}
    for n in range(2, search_limit + 1):
        state = (n % modulus, tuple(counts[d] % modulus for d in classes))
        if state in seen:
            start = seen[state]
            residues = [v % modulus for v in values[start:n]]
            period = n - start
            assert len(residues) == period
            frequencies = Counter(residues)
            class_increments = {
                d: sum(frequencies[r] for r in range(modulus)
                       if gcd(r, modulus) == d)
                for d in classes
            }
            assert all(increment % modulus == 0
                       for increment in class_increments.values())
            assert all(counts[d] - full_states[state][d] == class_increments[d]
                       for d in classes)
            slopes = {
                str(d): str(Fraction(sum(count for r, count in frequencies.items()
                                        if gcd(r, d) == 1), period))
                for d in classes
            }
            return {
                "modulus": modulus,
                "class_order": classes,
                "cycle_start_index": start,
                "repeated_state_index": n,
                "period": period,
                "phase": state[0],
                "counts_mod_modulus_at_both_indices": list(state[1]),
                "full_counts_at_cycle_start": full_states[state],
                "full_counts_at_repeat": counts,
                "class_increments_per_cycle": class_increments,
                "cycle_residues": residues,
                "cycle_residue_counts": {str(r): frequencies[r]
                                        for r in range(modulus)},
                "odd_density": str(Fraction(sum(frequencies[r]
                                                for r in range(1, modulus, 2)),
                                             period)),
                "limit_b_n_over_n_by_gcd_n_modulus": slopes,
                "prefix_residues_before_cycle": [v % modulus
                                                 for v in values[1:start]],
            }
        seen[state] = n
        full_states[state] = dict(counts)
        value = sum(counts[d] for d in classes if gcd(d, n) == 1)
        assert 1 <= value < n
        values.append(value)
        counts[gcd(value, modulus)] += 1
    raise AssertionError(f"No cycle found for P={modulus} by {search_limit}")


def run(literal_terms):
    rows = []
    original = literal_original(200)
    for modulus in (2, 6):
        row = exact_cycle(modulus, 10000)
        literal = literal_truncated(modulus, literal_terms)
        start, period = row["cycle_start_index"], row["period"]
        for n in range(1, literal_terms + 1):
            predicted = (row["prefix_residues_before_cycle"][n - 1]
                         if n < start else row["cycle_residues"][(n - start) % period])
            assert literal[n] % modulus == predicted, (modulus, n)
        # Verify the predicted exact increase after a residue period, including
        # all classes gcd(n, P).  This is stronger than comparing frequencies.
        for n in range(start, literal_terms - period + 1):
            d = gcd(n, modulus)
            increment = Fraction(row["limit_b_n_over_n_by_gcd_n_modulus"][str(d)]) * period
            assert increment.denominator == 1
            assert literal[n + period] - literal[n] == increment
        first = next(n for n in range(1, 201) if original[n] != literal[n])
        row["first_difference_from_original"] = {
            "n": first, "original_a_n": original[first], "truncated_b_n": literal[first]
        }
        row["literal_gcd_check_terms"] = literal_terms
        rows.append(row)
    return {
        "date": "2026-10-28",
        "scope": "Exact residue cycles of auxiliary finite-prime recurrences only; original conjecture 004 remains unproved.",
        "verification": "Integer state recurrence, repeated state, class increments, and separate literal gcd computation.",
        "models": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literal-terms", type=int, default=3000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.literal_terms < 200:
        parser.error("--literal-terms must be at least 200")
    result = run(args.literal_terms)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
