"""Exact finite search for the minimax denominator in 4/n unit-fraction sums."""

from fractions import Fraction
import json
from pathlib import Path


def best_solution(n: int):
    """Return (largest denominator, sorted solution) by exhaustive a,b search."""
    best = None
    best_tuple = None
    for a in range(n // 4 + 1, (3 * n) // 4 + 1):
        rem_num = 4 * a - n
        # 1/b + 1/c = rem_num/(n*a), with a <= b <= c.
        b_max = (2 * n * a) // rem_num
        for b in range(a, b_max + 1):
            den = 4 * a * b - n * (a + b)
            if den <= 0:
                continue
            num = n * a * b
            if num % den:
                continue
            c = num // den
            if c < b:
                continue
            largest = c
            if best is None or largest < best:
                best = largest
                best_tuple = (a, b, c)
    return best, best_tuple


def main():
    rows = []
    for n in range(2, 101):
        largest, solution = best_solution(n)
        if solution is None:
            raise RuntimeError(f"no representation found for n={n}")
        a, b, c = solution
        if Fraction(1, a) + Fraction(1, b) + Fraction(1, c) != Fraction(4, n):
            raise AssertionError(f"bad exact identity for n={n}: {solution}")
        rows.append({"n": n, "solution": list(solution), "max_denominator": largest})

    worst = max(rows, key=lambda row: Fraction(row["max_denominator"], row["n"] ** 2))
    out = {
        "range": [2, 100],
        "method": "complete exact search over sorted a<=b<=c; c is forced by each a,b pair",
        "count": len(rows),
        "worst_D_over_n2": {
            "n": worst["n"],
            "D": worst["max_denominator"],
            "ratio": str(Fraction(worst["max_denominator"], worst["n"] ** 2)),
            "solution": worst["solution"],
        },
        "rows": rows,
    }
    path = Path(__file__).with_name("experiment.json")
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in out.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
