"""Exact diameter counts from height-bounded rooted-tree GFs.

This is independent of the NetworkX unlabeled-tree enumeration in explore.py.
For R_h(x) counting rooted unlabeled trees of height at most h, let
M_h(x) = exp(sum_{k>=1} R_h(x^k)/k), the multiset construction. Then
R_{h+1}(x) = x M_h(x). Coefficients of M_h are computed by the Euler
transform, using n*m_n = sum_{j=1}^n (sum_{d|j} d*r_d) m_{n-j}.

The odd/even center formulas are the ones documented in discussion D006.
"""

from __future__ import annotations

import json
from pathlib import Path


def multiset_coefficients(rooted: list[int], max_n: int) -> list[int]:
    """Return coefficients of exp(sum_{k>=1} R(x^k)/k), through x^max_n."""
    divisor_sums = [0] * (max_n + 1)
    for d in range(1, max_n + 1):
        weight = d * rooted[d]
        if weight:
            for j in range(d, max_n + 1, d):
                divisor_sums[j] += weight

    result = [0] * (max_n + 1)
    result[0] = 1
    for n in range(1, max_n + 1):
        numerator = sum(
            divisor_sums[j] * result[n - j] for j in range(1, n + 1)
        )
        result[n], remainder = divmod(numerator, n)
        if remainder:
            raise ArithmeticError(f"nonintegral Euler transform coefficient at n={n}")
    return result


def convolution_coefficient(left: list[int], right: list[int], n: int) -> int:
    return sum(left[i] * right[n - i] for i in range(n + 1))


def is_unimodal(values: list[int]) -> bool:
    peak = max(range(len(values)), key=values.__getitem__)
    return all(values[i] <= values[i + 1] for i in range(peak)) and all(
        values[i] >= values[i + 1] for i in range(peak, len(values) - 1)
    )


def diameter_rows(max_n: int) -> list[dict[str, object]]:
    if max_n < 2:
        raise ValueError("max_n must be at least 2")
    rooted = [[0] * (max_n + 1) for _ in range(max_n + 2)]
    rooted[0][1] = 1  # R_0(x) = x; rooted[-1] is the zero series.
    multisets: list[list[int]] = []
    for h in range(max_n + 1):
        multiset = multiset_coefficients(rooted[h], max_n)
        multisets.append(multiset)
        rooted[h + 1] = [0] + multiset[:-1]  # R_{h+1}(x) = x M_h(x).

    one_series = [1] + [0] * max_n  # M_{-1}(x) = 1.

    exact_heights = [
        [rooted[h][i] - (rooted[h - 1][i] if h else 0)
         for i in range(max_n + 1)]
        for h in range((max_n + 1) // 2)
    ]

    def multiset_at_height(h: int) -> list[int]:
        return multisets[h] if h >= 0 else one_series

    rows = []
    for n in range(2, max_n + 1):
        counts = []
        for diameter in range(1, n):
            if diameter % 2:
                h = (diameter - 1) // 2
                branches = exact_heights[h]
                numerator = convolution_coefficient(branches, branches, n)
                if n % 2 == 0:
                    numerator += branches[n // 2]  # [x^n] H_h(x^2)
                count, remainder = divmod(numerator, 2)
                if remainder:
                    raise ArithmeticError("unordered-pair count was not integral")
            else:
                r = diameter // 2
                branches = exact_heights[r - 1]
                broad = multiset_at_height(r - 1)
                narrow = multiset_at_height(r - 2)
                count = (
                    broad[n - 1]
                    - narrow[n - 1]
                    - convolution_coefficient(branches, narrow, n - 1)
                )
            counts.append(count)

        rows.append(
            {
                "n": n,
                "diameter_counts": counts,
                "unimodal": is_unimodal(counts),
            }
        )
    return rows


def main() -> None:
    max_n = 100
    rows = diameter_rows(max_n)
    result = {
        "conjecture": "042",
        "method": "height-bounded rooted-tree multiset GFs and exact Euler transform",
        "range": [2, max_n],
        "all_unimodal": all(row["unimodal"] for row in rows),
        "rows": rows,
        "scope_note": "Exact recurrence computation only; not a proof for n > 100.",
    }
    output = Path(__file__).with_name("experiment-height-gf.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "range": result["range"],
                "all_unimodal": result["all_unimodal"],
                "row_count": len(rows),
                "output": output.name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
