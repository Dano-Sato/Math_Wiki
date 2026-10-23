"""Reproduce finite evidence for the alternating coprime greedy sequence."""

import argparse
import json
from math import gcd
from pathlib import Path


def reference(count):
    """Literal minimum search; intentionally does not use parity cursors."""
    seq = [1, 2][:count]
    used = set(seq)
    while len(seq) < count:
        index = len(seq) + 1
        candidate = 1
        total = seq[-1] + seq[-2]
        while (
            candidate in used
            or candidate % 2 != index % 2
            or gcd(candidate, total) != 1
        ):
            candidate += 1
        seq.append(candidate)
        used.add(candidate)
    return seq


def experiment(count):
    seq = [1, 2]
    used = {1, 2}
    least_unused = {0: 4, 1: 3}
    checkpoints = {10, 100, 1000, 10000, 100000, 1000000, count}
    rows = []
    records = []
    max_value = 2
    max_displacement = 0

    for index in range(3, count + 1):
        parity = index % 2
        candidate = least_unused[parity]
        total = seq[-1] + seq[-2]
        while candidate in used or gcd(candidate, total) != 1:
            candidate += 2
        seq.append(candidate)
        used.add(candidate)
        while least_unused[parity] in used:
            least_unused[parity] += 2
        max_value = max(max_value, candidate)
        displacement = abs(candidate - index)
        if displacement > max_displacement:
            max_displacement = displacement
            records.append({"index": index, "value": candidate, "displacement": displacement})
        if index in checkpoints:
            rows.append({
                "terms": index,
                "maximum_value": max_value,
                "covered_through": min(least_unused.values()) - 1,
                "maximum_absolute_displacement": max_displacement,
            })

    reference_terms = min(count, 10000)
    checks = {
        "unique": len(set(seq)) == count,
        "positive": all(value > 0 for value in seq),
        "parity": all(value % 2 == index % 2 for index, value in enumerate(seq, 1)),
        "coprimality": all(gcd(seq[i], seq[i - 1] + seq[i - 2]) == 1 for i in range(2, count)),
        "matches_literal_reference": seq[:reference_terms] == reference(reference_terms),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Verification failed: {checks}")
    return {
        "definition_version": "001-0.1",
        "terms": count,
        "prefix_30": seq[:30],
        "checkpoints": rows,
        "displacement_records": records,
        "literal_reference_terms": reference_terms,
        "checks": checks,
        "scope": "Finite computation only; no proof of surjectivity or bounded displacement.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", type=int, default=2000000)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("experiment.json"))
    args = parser.parse_args()
    if args.terms < 3:
        parser.error("--terms must be at least 3")
    result = experiment(args.terms)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
