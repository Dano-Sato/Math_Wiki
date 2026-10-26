#!/usr/bin/env python3
"""Exhaustively check the maximum-height peak-count conjecture for Dyck paths."""

import json
from pathlib import Path


def dyck_height_sequences(n: int, height: int = 0, heights: tuple[int, ...] = (0,)):
    if len(heights) == 2 * n + 1:
        if height == 0:
            yield heights
        return
    if height < n:
        yield from dyck_height_sequences(n, height + 1, heights + (height + 1,))
    if height > 0:
        yield from dyck_height_sequences(n, height - 1, heights + (height - 1,))


def count_by_top_peaks(n: int) -> list[int]:
    counts = [0] * (n + 1)
    for heights in dyck_height_sequences(n):
        maximum = max(heights)
        top_peaks = sum(
            heights[i] == maximum
            and heights[i - 1] == maximum - 1
            and heights[i + 1] == maximum - 1
            for i in range(1, len(heights) - 1)
        )
        counts[top_peaks] += 1
    return counts[1:]


def main() -> None:
    by_semilength = {}
    first_failure = None
    for n in range(1, 13):
        counts = count_by_top_peaks(n)
        by_semilength[str(n)] = counts
        if any(left < right for left, right in zip(counts, counts[1:])):
            first_failure = {"n": n, "counts": counts}
            break

    result = {
        "claim": "counts by number of peaks at maximum height are weakly decreasing",
        "scope": "all Dyck paths of semilength n for each tested n",
        "semilengths_tested": list(map(int, by_semilength)),
        "counts_by_semilength": by_semilength,
        "total_paths_tested": sum(sum(counts) for counts in by_semilength.values()),
        "first_failure": first_failure,
        "method": "recursive exact enumeration of Dyck paths and integer counting",
        "is_proof": False,
    }
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
