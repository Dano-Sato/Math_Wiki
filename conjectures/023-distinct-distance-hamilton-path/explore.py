"""Finite exact checks for conjecture 023 (standard library only)."""

from itertools import combinations, permutations
import json
from pathlib import Path
import random


GRID = tuple((x, y) for x in range(4) for y in range(4))


def check(points):
    n = len(points)
    d = [[(points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2
          for j in range(n)] for i in range(n)]
    total_distances = len({d[i][j] for i in range(n) for j in range(i)})
    target = min(n - 1, total_distances // 2)
    best = 0
    for order in permutations(range(n)):
        used = {d[order[i]][order[i + 1]] for i in range(n - 1)}
        if len(used) > best:
            best = len(used)
            if best >= target:
                return total_distances, target, best
    return total_distances, target, best


def main():
    rows = []
    for n in (4, 6):
        count = 0
        min_slack = None
        witness = None
        for points in combinations(GRID, n):
            distances, target, best = check(points)
            slack = best - target
            count += 1
            if min_slack is None or slack < min_slack:
                min_slack, witness = slack, points
            if slack < 0:
                raise SystemExit({"counterexample": points, "D": distances,
                                  "target": target, "best": best})
        rows.append({"n": n, "sets_checked": count, "minimum_slack": min_slack,
                     "example_at_minimum_slack": witness})

    rng = random.Random(23024)
    sample = rng.sample(list(combinations(GRID, 8)), 100)
    min_slack = None
    witness = None
    for points in sample:
        distances, target, best = check(points)
        slack = best - target
        if min_slack is None or slack < min_slack:
            min_slack, witness = slack, points
        if slack < 0:
            raise SystemExit({"counterexample": points, "D": distances,
                              "target": target, "best": best})
    rows.append({"n": 8, "sets_checked": len(sample), "sampling": "uniform without replacement; seed=23024",
                 "minimum_slack": min_slack, "example_at_minimum_slack": witness})

    result = {
        "claim": "max_H c(H) >= min(n-1, floor(D(P)/2))",
        "distance_metric": "squared Euclidean distance (exact integer comparison)",
        "grid": "{0,1,2,3}^2",
        "results": rows,
        "scope": "Exact for all listed n=4,6 grid subsets; random sample only for n=8. Not a proof for arbitrary planar point sets.",
    }
    Path(__file__).with_name("experiment.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
