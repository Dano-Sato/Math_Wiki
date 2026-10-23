"""Exhaustively enumerate fixed polyominoes by area and edge perimeter."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def normalize(cells: set[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    min_x = min(x for x, _ in cells)
    min_y = min(y for _, y in cells)
    return tuple(sorted((x - min_x, y - min_y) for x, y in cells))


def grow(polyominoes: set[tuple[tuple[int, int], ...]]) -> set[tuple[tuple[int, int], ...]]:
    following = set()
    for poly in polyominoes:
        cells = set(poly)
        for x, y in cells:
            for dx, dy in NEIGHBORS:
                cell = (x + dx, y + dy)
                if cell not in cells:
                    following.add(normalize(cells | {cell}))
    return following


def edge_perimeter(poly: tuple[tuple[int, int], ...]) -> int:
    cells = set(poly)
    return sum(
        (x + dx, y + dy) not in cells
        for x, y in cells
        for dx, dy in NEIGHBORS
    )


def log_concavity_failure(coefficients: list[int]) -> dict | None:
    for i in range(1, len(coefficients) - 1):
        if coefficients[i] * coefficients[i] < coefficients[i - 1] * coefficients[i + 1]:
            return {
                "index": i,
                "left": coefficients[i - 1],
                "center": coefficients[i],
                "right": coefficients[i + 1],
            }
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.max_n <= 12:
        raise SystemExit("For reproducible resource use, --max-n must be between 1 and 12.")

    polyominoes = {((0, 0),)}
    rows = {}
    counts = []
    first_failure = None
    for n in range(1, args.max_n + 1):
        by_perimeter = Counter(edge_perimeter(poly) for poly in polyominoes)
        perimeters = sorted(by_perimeter)
        coefficients = [by_perimeter[p] for p in perimeters]
        failure = log_concavity_failure(coefficients)
        contiguous = all(b - a == 2 for a, b in zip(perimeters, perimeters[1:]))
        if first_failure is None and (failure or not contiguous):
            first_failure = {
                "n": n,
                "log_concavity_failure": failure,
                "positive_support_step_2": contiguous,
                "perimeters": perimeters,
                "coefficients": coefficients,
            }
        rows[str(n)] = {
            "fixed_polyomino_count": len(polyominoes),
            "perimeters": perimeters,
            "coefficients": coefficients,
            "log_concave": failure is None,
            "support_step_2": contiguous,
        }
        counts.append(len(polyominoes))
        if n < args.max_n:
            polyominoes = grow(polyominoes)

    result = {
        "conjecture": "040",
        "equivalence": "translations only; rotations and reflections counted separately",
        "perimeter": "number of unit boundary edges; holes allowed",
        "max_n": args.max_n,
        "fixed_polyomino_counts": counts,
        "first_failure": first_failure,
        "rows": rows,
        "scope": "Exact exhaustive finite computation; no claim beyond max_n.",
    }
    out = Path(__file__).with_name("experiment.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"max_n": args.max_n, "counts": counts, "first_failure": first_failure}, ensure_ascii=False))


if __name__ == "__main__":
    main()
