"""Broader exhaustive exact check for conjecture 023 on the 4x4 grid."""

from itertools import combinations
from functools import lru_cache

GRID = tuple((x, y) for x in range(4) for y in range(4))


def reaches_target(points):
    n = len(points)
    distances = [[(points[i][0] - points[j][0]) ** 2 +
                  (points[i][1] - points[j][1]) ** 2 for j in range(n)]
                 for i in range(n)]
    palette = {d: i for i, d in enumerate(sorted({distances[i][j]
                                                  for i in range(n)
                                                  for j in range(i)}))}
    colors = [[-1 if i == j else palette[distances[i][j]]
               for j in range(n)] for i in range(n)]
    target = min(n - 1, len(palette) // 2)

    @lru_cache(None)
    def search(mask, last, used):
        count = used.bit_count()
        if mask == (1 << n) - 1:
            return count >= target
        for nxt in range(n):
            bit = 1 << nxt
            if mask & bit:
                continue
            new_used = used | (1 << colors[last][nxt])
            if new_used.bit_count() + (n - (mask.bit_count())) < target:
                continue
            if search(mask | bit, nxt, new_used):
                return True
        return False

    success = False
    for start in range(n):
        if search(1 << start, start, 0):
            success = True
            break
    return len(palette), target, success


def main():
    rows = []
    for n in (7, 8):
        checked = 0
        failures = []
        for points in combinations(GRID, n):
            d, target, success = reaches_target(points)
            checked += 1
            if not success:
                print({"counterexample": points, "D": d,
                       "target": target})
                return
        rows.append({"n": n, "sets_checked": checked, "failures": failures})
    print(rows)


if __name__ == "__main__":
    main()
