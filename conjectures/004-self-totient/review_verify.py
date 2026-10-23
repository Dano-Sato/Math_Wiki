"""Codex review of 004: independent Python computation and exact checks."""

import argparse
import json
from array import array
from fractions import Fraction
from math import gcd
from pathlib import Path


def sieve(limit):
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit ** 0.5) + 1):
        if spf[p] == p:
            for value in range(p * p, limit + 1, p):
                if spf[value] == value:
                    spf[value] = p
    return spf


def factors(value, spf):
    result = []
    while value > 1:
        prime = spf[value]
        result.append(prime)
        while value % prime == 0:
            value //= prime
    return result


def signed_divisors(primes):
    result = [(1, 1)]
    for prime in primes:
        result += [(d * prime, -sign) for d, sign in result]
    return result


def literal(limit):
    values = [0, 1]
    for n in range(2, limit + 1):
        values.append(sum(gcd(previous, n) == 1 for previous in values[1:]))
    return values


def run(limit, literal_terms, original):
    spf = sieve(limit)
    counts = array("I", [0]) * (limit + 1)
    counts[1] = 1
    values = array("I", [0, 1])
    phi_values = array("I", [0, 1])
    max_num, max_den = 1, 1
    min_num, min_den = 1, 1
    upper_equalities = []
    lower_equalities = []
    parity_states = {}
    parity_counterexample = None
    sum_ratio = 0.0
    window_min = None
    window_max = None
    checkpoints = []
    next_checkpoint = 10
    for n in range(2, limit + 1):
        primes = factors(n, spf)
        divisors = signed_divisors(primes)
        value = sum(sign * counts[d] for d, sign in divisors)
        phi = n
        for prime in primes:
            phi = phi // prime * (prime - 1)
        if not 1 <= value < n:
            raise AssertionError((n, value))
        if len(primes) == 1 and n == primes[0] and value != n - 1:
            raise AssertionError("Prime-position identity failed")
        state = (n % 2, counts[2])
        if parity_counterexample is None:
            if state in parity_states and parity_states[state][1] % 2 != value % 2:
                parity_counterexample = {"same_n_parity_and_C2": list(state), "terms": [parity_states[state], [n, value]]}
            else:
                parity_states[state] = [n, value]
        if 6 * value == 7 * phi:
            upper_equalities.append(n)
        if 12 * value == 5 * phi:
            lower_equalities.append(n)
        if value * max_den > max_num * phi:
            max_num, max_den = value, phi
        if value * min_den < min_num * phi:
            min_num, min_den = value, phi
        ratio = value / phi
        sum_ratio += ratio
        if window_min is None or value * window_min[2] < window_min[1] * phi:
            window_min = (n, value, phi)
        if window_max is None or value * window_max[2] > window_max[1] * phi:
            window_max = (n, value, phi)
        values.append(value)
        phi_values.append(phi)
        for d, _ in signed_divisors(factors(value, spf)):
            counts[d] += 1
        if n == next_checkpoint or n == limit:
            tracked = [d for d in (2, 3, 5, 6, 7, 10, 15, 30, 210) if d <= limit]
            checkpoints.append({
                "n": n,
                "mean_a_over_phi_excluding_n1": sum_ratio / (n - 1),
                "decade_min_ratio": str(Fraction(window_min[1], window_min[2])),
                "decade_argmin": window_min[0],
                "decade_max_ratio": str(Fraction(window_max[1], window_max[2])),
                "decade_argmax": window_max[0],
                "divisibility_densities_all_N": {str(d): counts[d] / n for d in tracked},
                "counts": {str(d): counts[d] for d in tracked},
            })
            next_checkpoint *= 10
            window_min = window_max = None

    checked = min(limit, literal_terms)
    assert values[:checked + 1].tolist() == literal(checked)
    assert values[1:41].tolist() == original["prefix_40"]
    original_rows = {row["n"]: row for row in original["checkpoints"]}
    compared = []
    for row in checkpoints:
        n = row["n"]
        if n not in original_rows:
            continue
        old = original_rows[n]
        assert abs(row["mean_a_over_phi_excluding_n1"] - old["mean_a_over_phi"]) < 1e-12
        assert abs(float(Fraction(row["decade_min_ratio"])) - old["decade_min_a_over_phi"]) < 1e-12
        assert abs(float(Fraction(row["decade_max_ratio"])) - old["decade_max_a_over_phi"]) < 1e-12
        for d, key in ((2, "density_a_even"), (3, "density_3_divides_a"), (5, "density_5_divides_a"), (7, "density_7_divides_a")):
            assert abs(row["counts"][str(d)] / (n - 1) - old[key]) < 1e-12
        compared.append(n)
    assert Fraction(max_num, max_den) == Fraction(7, 6)
    assert Fraction(min_num, min_den) == Fraction(5, 12)
    return {
        "reviewer": "Codex / ChatGPT",
        "date": "2026-10-24",
        "definition_unchanged_from": "004 v0.1",
        "terms": limit,
        "literal_check_terms": checked,
        "original_checkpoint_comparisons": compared,
        "prefix_40": values[1:41].tolist(),
        "upper_ratio": str(Fraction(max_num, max_den)),
        "upper_equality_indices": upper_equalities,
        "lower_ratio": str(Fraction(min_num, min_den)),
        "lower_equality_indices": lower_equalities,
        "parity_not_determined_by_n_parity_and_C2": parity_counterexample,
        "checkpoints": checkpoints,
        "scope": "Independent Python computation to the stated limit, not a rerun of 10^8 terms or a convergence proof.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", type=int, default=1000000)
    parser.add_argument("--literal-terms", type=int, default=3000)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("review_2026-10-24.json"))
    args = parser.parse_args()
    if args.terms < 100 or args.literal_terms < 1:
        parser.error("--terms must be >=100 and --literal-terms must be positive")
    original = json.loads(Path(__file__).with_name("experiment.json").read_text(encoding="utf-8"))
    result = run(args.terms, args.literal_terms, original)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {key: value for key, value in result.items() if key not in ("prefix_40", "checkpoints")}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(result["checkpoints"][-1], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
