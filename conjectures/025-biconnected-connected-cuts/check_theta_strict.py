"""Exact search for strict internal bounds in three-path theta graphs."""

from __future__ import annotations

from collections import Counter


def theta_coefficients(paths: tuple[int, int, int]) -> list[int]:
    total_internal = sum(paths)
    n = total_internal + 2
    # Coefficients of product_i (1 + x + ... + x**m_i).
    product = [1]
    for length in paths:
        nxt = [0] * (len(product) + length)
        for i, a in enumerate(product):
            for j in range(length + 1):
                nxt[i + j] += a
        product = nxt
    result = []
    for k in range(1, n):
        a_k = sum(max(m - k + 1, 0) for m in paths)
        a_nk = sum(max(m - (n - k) + 1, 0) for m in paths)
        result.append(a_k + a_nk + 2 * product[k - 1])
    return result


def main() -> None:
    failures = []
    minima = {}
    for total in range(3, 61):
        by_k = []
        for a in range(1, total - 1):
            for b in range(a, total - a):
                c = total - a - b
                if c < b:
                    continue
                n = total + 2
                coeffs = theta_coefficients((a, b, c))
                for k in range(3, n - 2):
                    by_k.append((coeffs[k - 1] - n, (a, b, c), k))
        if by_k:
            minima[total] = min(by_k)
            if minima[total][0] < 2:
                failures.append({"n": total + 2, "minimum_gap": minima[total][0], "witness": minima[total][1:]})
    print({"tested_internal_total_range": [3, 60], "strict_n_plus_2_failures": failures, "first_minima": {k: v for k, v in list(minima.items())[:10]}})


if __name__ == "__main__":
    main()
