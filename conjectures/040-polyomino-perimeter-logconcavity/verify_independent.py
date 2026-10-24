"""Independent set-of-coordinate check of the polyomino bitboard census.

This intentionally uses translated coordinate tuples rather than the 16x16
bitboard representation in explore.py. It compares complete perimeter rows
for areas 1 through 10 with the recorded exact census.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

Cell = tuple[int, int]
Shape = tuple[Cell, ...]


def normalize(cells: set[Cell]) -> Shape:
    min_x = min(x for x, _ in cells)
    min_y = min(y for _, y in cells)
    return tuple(sorted((x - min_x, y - min_y) for x, y in cells))


def grow(shapes: set[Shape]) -> set[Shape]:
    following: set[Shape] = set()
    for shape in shapes:
        cells = set(shape)
        for x, y in shape:
            for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if neighbor not in cells:
                    following.add(normalize(cells | {neighbor}))
    return following


def perimeter(shape: Shape) -> int:
    cells = set(shape)
    shared_edges = sum(
        ((x + 1, y) in cells) + ((x, y + 1) in cells)
        for x, y in shape
    )
    return 4 * len(shape) - 2 * shared_edges


def main() -> None:
    recorded = json.loads(Path(__file__).with_name("experiment.json").read_text(encoding="utf-8"))
    shapes: set[Shape] = {((0, 0),)}
    comparisons = []
    for n in range(1, 11):
        counts = Counter(perimeter(shape) for shape in shapes)
        expected = recorded["rows"][str(n)]
        actual_perimeters = sorted(counts)
        actual_coefficients = [counts[p] for p in actual_perimeters]
        assert len(shapes) == expected["fixed_polyomino_count"], (n, len(shapes))
        assert actual_perimeters == expected["perimeters"], (n, actual_perimeters)
        assert actual_coefficients == expected["coefficients"], (n, actual_coefficients)
        comparisons.append({"area": n, "count": len(shapes), "perimeter_row_matches": True})
        if n < 10:
            shapes = grow(shapes)

    result = {
        "method": "independent coordinate-set generation and edge counting",
        "compared_with": "experiment.json bitboard census",
        "areas": comparisons,
        "conclusion": "all complete rows match for areas 1 through 10",
    }
    output = Path(__file__).with_name("verify_independent.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
