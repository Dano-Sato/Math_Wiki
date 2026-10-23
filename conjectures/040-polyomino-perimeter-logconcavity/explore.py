"""Exhaustively enumerate fixed polyominoes by area and edge perimeter."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

BOARD_WIDTH = 16
LEFT_EDGE = sum(1 << (y * BOARD_WIDTH) for y in range(BOARD_WIDTH))
RIGHT_EDGE = sum(1 << (y * BOARD_WIDTH + BOARD_WIDTH - 1) for y in range(BOARD_WIDTH))


def normalize(cells: int) -> int:
    """Translate a 16-by-16 bitboard so its lower-left cell is at (1, 1)."""
    min_x = BOARD_WIDTH
    min_y = BOARD_WIDTH
    remaining = cells
    while remaining:
        bit = remaining & -remaining
        index = bit.bit_length() - 1
        min_x = min(min_x, index % BOARD_WIDTH)
        min_y = min(min_y, index // BOARD_WIDTH)
        remaining ^= bit
    shift = (1 - min_y) * BOARD_WIDTH + (1 - min_x)
    return cells << shift if shift >= 0 else cells >> -shift


def grow(polyominoes: set[int]) -> set[int]:
    following = set()
    for cells in polyominoes:
        neighbors = (
            (cells << BOARD_WIDTH)
            | (cells >> BOARD_WIDTH)
            | ((cells & ~RIGHT_EDGE) << 1)
            | ((cells & ~LEFT_EDGE) >> 1)
        )
        frontier = neighbors & ~cells
        while frontier:
            bit = frontier & -frontier
            following.add(normalize(cells | bit))
            frontier ^= bit
    return following


def edge_perimeter(cells: int) -> int:
    area = cells.bit_count()
    horizontal_adjacencies = ((cells & ~RIGHT_EDGE) & (cells >> 1)).bit_count()
    vertical_adjacencies = (cells & (cells >> BOARD_WIDTH)).bit_count()
    return 4 * area - 2 * (horizontal_adjacencies + vertical_adjacencies)


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
    if not 1 <= args.max_n <= 13:
        raise SystemExit("For reproducible resource use, --max-n must be between 1 and 13.")

    polyominoes = {1 << (BOARD_WIDTH + 1)}
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
