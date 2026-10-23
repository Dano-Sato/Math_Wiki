"""Exact finite check for conjecture 037; no external packages."""
from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path


def no_singleton_partitions(max_n: int) -> list[int]:
    """b[m]: set partitions of [m] with no singleton blocks."""
    b = [0] * (max_n + 1)
    b[0] = 1
    for m in range(1, max_n + 1):
        b[m] = sum(comb(m - 1, j - 1) * b[m - j] for j in range(2, m + 1))
    return b


def is_unimodal(row: list[int]) -> bool:
    """Weak unimodality: no increase after the sequence has decreased."""
    decreasing = False
    for left, right in zip(row, row[1:]):
        if right < left:
            decreasing = True
        elif right > left and decreasing:
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=400)
    args = parser.parse_args()
    if args.max_n < 2:
        raise SystemExit("--max-n must be at least 2")

    b = no_singleton_partitions(args.max_n)
    examples = {}
    first_failure = None
    for n in range(2, args.max_n + 1):
        row = [comb(n, k) * b[n - k] for k in range(n - 1)]
        if not is_unimodal(row) and first_failure is None:
            first_failure = {"n": n, "row": row}
        if n in (2, 4, 5, 6, 10, 20, 50, 100, args.max_n):
            examples[str(n)] = row

    output = {
        "conjecture": "037",
        "max_n": args.max_n,
        "checked_rows": args.max_n - 1,
        "recurrence": "b[0]=1; b[1]=0; b[m]=sum(C(m-1,j-1)*b[m-j], j=2..m)",
        "first_non_unimodal": first_failure,
        "examples": examples,
        "scope": "Exact finite computation only; does not prove the universal conjecture.",
    }
    out_path = Path(__file__).with_name("experiment.json")
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ("max_n", "checked_rows", "first_non_unimodal")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
