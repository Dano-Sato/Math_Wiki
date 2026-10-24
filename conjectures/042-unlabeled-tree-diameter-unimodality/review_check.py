"""Reproduce the finite diameter check and verify the proved boundary formulas.

Run: python conjectures/042-unlabeled-tree-diameter-unimodality/review_check.py
The center recurrence is in height_gf.py; the total-count check below instead
uses unrestricted rooted trees and Otter's dissymmetry identity. Neither this
finite computation nor a total-count agreement proves general unimodality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

from height_gf import diameter_rows, is_unimodal


def unrooted_totals(max_n: int) -> list[int]:
    """Compute U=R-(R^2-R(x^2))/2, without height or diameter states."""
    rooted = [0] * (max_n + 1)
    divisor_sums = [0] * (max_n + 1)
    for n in range(1, max_n + 1):
        if n == 1:
            rooted[n] = 1
        else:
            numerator = sum(divisor_sums[j] * rooted[n-j] for j in range(1, n))
            rooted[n], remainder = divmod(numerator, n-1)
            if remainder:
                raise ArithmeticError("nonintegral unrestricted rooted count")
        for j in range(n, max_n + 1, n):
            divisor_sums[j] += n * rooted[n]
    totals = [0] * (max_n + 1)
    for n in range(1, max_n + 1):
        square = sum(rooted[j] * rooted[n-j] for j in range(1, n))
        diagonal = rooted[n//2] if n % 2 == 0 else 0
        correction, remainder = divmod(square-diagonal, 2)
        if remainder:
            raise ArithmeticError("nonintegral unrooted count")
        totals[n] = rooted[n] - correction
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=600)
    args = parser.parse_args()
    if args.max_n < 5:
        parser.error("--max-n must be at least 5")
    started = time.perf_counter()
    rows = diameter_rows(args.max_n)
    totals = unrooted_totals(args.max_n)
    folder = Path(__file__).parent
    enumerated = json.loads((folder / "experiment.json").read_text(encoding="utf-8"))
    previous = json.loads((folder / "experiment-height-gf.json").read_text(encoding="utf-8"))
    by_n = {row["n"]: row["diameter_counts"] for row in rows}
    enumeration_checks = 0
    for row in enumerated["rows"]:
        n = row["n"]
        if n <= args.max_n:
            expected = [row["diameter_counts"].get(str(d), 0) for d in range(1, n)]
            assert by_n[n] == expected, ("NetworkX mismatch", n)
            enumeration_checks += 1
    previous_checks = 0
    for row in previous["rows"]:
        n = row["n"]
        if n <= args.max_n:
            assert by_n[n] == row["diameter_counts"], ("previous GF mismatch", n)
            previous_checks += 1
    summaries = []
    failures = []
    boundary_checks = 0
    for row in rows:
        n, counts = row["n"], row["diameter_counts"]
        assert len(counts) == n-1
        assert all(isinstance(c, int) and c >= 0 for c in counts)
        assert all(c > 0 for c in counts[(0 if n == 2 else 1):])
        assert sum(counts) == totals[n], ("Otter total mismatch", n)
        if n >= 5:
            third = (n-4)**2 // 4 + 2*((n-3)//2) - 1
            expected = [third, (n-2)//2, 1]
            assert counts[-3:] == expected, ("boundary formula mismatch", n)
            assert counts[-3] >= counts[-2] >= counts[-1]
            gap = counts[-2]**2 - counts[-3]*counts[-1]
            assert gap == (2 if n % 2 == 0 else (5-n)//2)
            boundary_checks += 1
        if not is_unimodal(counts):
            failures.append({"n": n, "diameter_counts": counts})
        peak = max(counts)
        summaries.append({
            "n": n,
            "tree_count": sum(counts),
            "peak_diameters": [d for d, c in enumerate(counts, 1) if c == peak],
            "unimodal": is_unimodal(counts),
            "row_sha256": hashlib.sha256(
                ",".join(map(str, counts)).encode("ascii")
            ).hexdigest(),
        })
    selected = {n: by_n[n] for n in (7, 22, 100, 250, args.max_n) if n in by_n}
    result = {
        "conjecture": "042", "statement_version": "0.2", "date": "2026-10-24",
        "python_version": platform.python_version(), "range": [2, args.max_n],
        "method": "exact height-bounded multiset recurrence; all integer arithmetic",
        "all_unimodal": not failures, "failures": failures,
        "validation": {
            "networkx_rows_matched": enumeration_checks,
            "previous_height_gf_rows_matched": previous_checks,
            "unrestricted_otter_totals_matched": len(rows),
            "boundary_formulas_and_parity_gap_matched": boundary_checks,
        },
        "rows": summaries, "selected_full_rows": selected,
        "row_digest_encoding": "SHA256 of ASCII comma-joined counts for d=1,...,n-1",
        "sources": ["https://oeis.org/A000055", "https://oeis.org/A034853"],
        "scope_note": "Finite exact verification; general unimodality remains open. Boundary formulas have a separate proof in discussion D008.",
    }
    output = folder / f"review-diameter-{args.max_n}.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"range": result["range"], "all_unimodal": result["all_unimodal"],
                      "validation": result["validation"],
                      "seconds": round(time.perf_counter()-started, 3),
                      "output": output.name}, indent=2))


if __name__ == "__main__":
    main()
