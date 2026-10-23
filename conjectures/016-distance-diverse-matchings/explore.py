"""Exhaustively explore the conjectured bound on subsets of a 4x4 grid."""

from itertools import combinations
from functools import lru_cache
import json


GRID = tuple((x, y) for x in range(4) for y in range(4))
SIZES = (4, 6, 8, 10)


def matching_color_sets(points):
    n = len(points)
    d2 = [[0] * n for _ in range(n)]
    all_distances = set()
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            d2[i][j] = d2[j][i] = dx * dx + dy * dy
            all_distances.add(d2[i][j])

    @lru_cache(None)
    def achievable(mask):
        if mask == 0:
            return frozenset((frozenset(),))
        first_bit = mask & -mask
        i = first_bit.bit_length() - 1
        remaining = mask ^ first_bit
        results = set()
        while remaining:
            bit = remaining & -remaining
            j = bit.bit_length() - 1
            remaining ^= bit
            smaller = mask ^ first_bit ^ bit
            for colors in achievable(smaller):
                results.add(colors | {d2[i][j]})
        return frozenset(results)

    max_colors = max(map(len, achievable((1 << n) - 1)))
    return len(all_distances), max_colors


def main():
    summary = {}
    for n in SIZES:
        count = 0
        min_slack = None
        witness = None
        for points in combinations(GRID, n):
            distance_count, matching_max = matching_color_sets(points)
            required = min(n // 2, distance_count // 2)
            slack = matching_max - required
            count += 1
            if min_slack is None or slack < min_slack:
                min_slack = slack
                witness = {
                    "points": points,
                    "distinct_distances": distance_count,
                    "best_matching_colors": matching_max,
                    "required": required,
                }
        summary[str(n)] = {
            "subsets": count,
            "minimum_slack": min_slack,
            "witness": witness,
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
