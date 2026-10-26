"""Exact-arithmetic verification of the nineteenth boundary inequality."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from verify_d026 import T, exact_rows, exp_series, is_prime, poly_in_m_for_c


J = 19
DEGREE = 2 * J + 3


def shifted_polynomial(offset: int, shift: int, b, rminus1):
    m = sp.symbols("m")
    c_left = poly_in_m_for_c(J - 1, 2 * (J - 1) + offset, b, rminus1)
    c_mid = poly_in_m_for_c(J, 2 * J + offset, b, rminus1)
    c_right = poly_in_m_for_c(J + 1, 2 * (J + 1) + offset, b, rminus1)
    numerator = sp.Poly(
        sp.cancel(
            (m - (J - 1))
            * (c_mid**2 - (m - J) * c_right * c_left / (m - (J - 1)))
        ),
        m,
    )
    shifted = sp.Poly(sp.expand(numerator.as_expr().subs(m, T + shift)), T)
    coefficients = shifted.all_coeffs()
    assert all(coefficient > 0 for coefficient in coefficients)
    return {
        "degree": shifted.degree(),
        "coefficient_count": len(coefficients),
        "all_shifted_coefficients_positive": True,
        "coefficients_ascending": [str(c) for c in reversed(coefficients)],
    }


def main() -> None:
    log_b = [sp.Rational(0)] * (DEGREE + 1)
    rminus1 = [sp.Rational(0)] * (DEGREE + 1)
    for i in range(1, DEGREE + 1):
        if not is_prime(i):
            log_b[i] = sp.Rational(1, i)
        if i + 2 <= DEGREE and is_prime(i + 2):
            rminus1[i] = sp.Rational(2, i + 2)
    b = exp_series(log_b, DEGREE)

    polynomials = {
        "even": shifted_polynomial(0, 2 * J - 3, b, rminus1),
        "odd": shifted_polynomial(1, 2 * J - 2, b, rminus1),
    }

    rows = exact_rows(2 * (2 * J - 3) + 1)
    initial_gaps = []
    for n in range(2 * J + 2, 2 * (2 * J - 3) + 2):
        m = n // 2
        k = m - J
        gap = rows[n][k] ** 2 - rows[n][k - 1] * rows[n][k + 1]
        assert gap > 0, n
        initial_gaps.append({"n": n, "gap": str(gap)})

    result = {
        "claim": "043 v0.1, nineteenth boundary inequality",
        "inequality": "a[n,m-19]^2 > a[n,m-20] * a[n,m-18], m=floor(n/2)",
        "method": "exact rational EGF coefficient polynomials and exact integer recurrence",
        "polynomial_checks": polynomials,
        "initial_gaps_n_40_to_71": initial_gaps,
        "conclusion": "all D030 sign checks verified",
    }
    output = Path(__file__).with_name("verify_d030.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "polynomials": {
            parity: {"degree": data["degree"], "coefficient_count": data["coefficient_count"]}
            for parity, data in polynomials.items()
        },
        "initial_gaps": len(initial_gaps),
        "all_initial_gaps_positive": True,
        "certificate": output.name,
    }, indent=2))


if __name__ == "__main__":
    main()
