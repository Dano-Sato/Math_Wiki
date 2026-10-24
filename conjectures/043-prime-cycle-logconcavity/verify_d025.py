"""Independent exact-arithmetic check of discussion.md D025.

Re-derives the normalized sixteenth-from-the-edge strict log-concavity
polynomials from the EGF and checks both their coefficient signs and the
finite initial ranges against the defining integer recurrence.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb, factorial
from pathlib import Path

import sympy as sp


X, T = sp.symbols("x t")
DEGREE = 35


def is_prime(n: int) -> bool:
    return n >= 2 and all(n % d for d in range(2, int(n**0.5) + 1))


def exp_series(coeffs: list[Fraction], degree: int) -> list[Fraction]:
    """Coefficients of exp(sum coeffs[i] x**i) through the given degree."""
    out = [Fraction(0) for _ in range(degree + 1)]
    out[0] = Fraction(1)
    for n in range(1, degree + 1):
        out[n] = sum(
            Fraction(k) * coeffs[k] * out[n - k]
            for k in range(1, n + 1)
        ) / n
    return out


def multiply(a: list[Fraction], b: list[Fraction], degree: int) -> list[Fraction]:
    return [
        sum((a[i] * b[n - i] for i in range(n + 1)), Fraction(0))
        for n in range(degree + 1)
    ]


def power(a: list[Fraction], q: int, degree: int) -> list[Fraction]:
    result = [Fraction(0)] * (degree + 1)
    result[0] = Fraction(1)
    for _ in range(q):
        result = multiply(result, a, degree)
    return result


def poly_in_m_for_c(j: int, d: int, b: list[Fraction], rminus1: list[Fraction]):
    """C_j=[x^d] B(x) R(x)^(m-j), as an exact polynomial in m."""
    m = sp.symbols("m")
    result = sp.Integer(0)
    powers = [[Fraction(0) for _ in range(d + 1)] for _ in range(d + 1)]
    powers[0][0] = Fraction(1)
    for q in range(1, d + 1):
        powers[q] = multiply(powers[q - 1], rminus1, d)
    for q in range(d + 1):
        coefficient = sum(
            (b[i] * powers[q][d - i] for i in range(d + 1)),
            Fraction(0),
        )
        if coefficient:
            result += sp.Rational(coefficient.numerator, coefficient.denominator) * sp.binomial(m - j, q)
    return sp.Poly(sp.expand_func(result), m).as_expr()


def exact_rows(limit: int) -> list[list[int]]:
    rows = [[1]]
    prime = [is_prime(i) for i in range(limit + 1)]
    facts = [factorial(i) for i in range(limit + 1)]
    for n in range(1, limit + 1):
        row = [0] * (n + 1)
        for j in range(1, n + 1):
            factor = facts[n - 1] // facts[n - j]
            mark = int(prime[j])
            for k, value in enumerate(rows[n - j]):
                row[k + mark] += factor * value
        rows.append(row)
    return rows


def main() -> None:
    # B=(1-x)^(-1) exp(-sum_{p prime} x^p/p), whose logarithm
    # contains exactly the non-prime cycle lengths. R=2 P(x)/x^2.
    log_b = [Fraction(0)] * (DEGREE + 1)
    rminus1 = [Fraction(0)] * (DEGREE + 1)
    for i in range(1, DEGREE + 1):
        if not is_prime(i):
            log_b[i] = Fraction(1, i)
        if i + 2 <= DEGREE and is_prime(i + 2):
            rminus1[i] = Fraction(2, i + 2)
    b = exp_series(log_b, DEGREE)

    m = sp.symbols("m")
    summaries = {}
    for parity, shift in (("even", 29), ("odd", 30)):
        offset = 0 if parity == "even" else 1
        c15 = poly_in_m_for_c(15, 30 + offset, b, rminus1)
        c16 = poly_in_m_for_c(16, 32 + offset, b, rminus1)
        c17 = poly_in_m_for_c(17, 34 + offset, b, rminus1)
        # Clear the sole displayed denominator (m-15), then translate to t.
        numerator = sp.Poly(sp.cancel((m - 15) * (c16**2 - (m - 16) * c17 * c15 / (m - 15))), m)
        shifted = sp.Poly(sp.expand(numerator.as_expr().subs(m, T + shift)), T)
        coefficients = shifted.all_coeffs()
        assert all(c > 0 for c in coefficients), (parity, coefficients)
        summaries[parity] = {
            "degree": shifted.degree(),
            "coefficient_count": len(coefficients),
            "all_shifted_coefficients_positive": True,
            "constant_coefficient": str(shifted.eval(0)),
            "coefficients_ascending": [str(c) for c in reversed(shifted.all_coeffs())],
        }

    # Verify the finite initial cases omitted by the shifted-polynomial proof.
    rows = exact_rows(61)
    gaps = []
    for n in range(34, 62):
        mval = n // 2
        k = mval - 16
        row = rows[n]
        gap = row[k] ** 2 - row[k - 1] * row[k + 1]
        assert gap > 0
        gaps.append({"n": n, "gap": str(gap)})

    result = {
        "claim": "043 v0.1, D025 sixteenth boundary inequality",
        "method": "independent exact rational EGF coefficient reconstruction plus exact integer cycle recurrence",
        "polynomial_checks": summaries,
        "initial_gaps_n_34_to_61": gaps,
        "conclusion": "all D025 sign checks reproduced",
    }
    output = Path(__file__).with_name("verify_d025.json")
    output.write_text(__import__("json").dumps(result, indent=2) + "\n", encoding="utf-8")
    print(__import__("json").dumps(result, indent=2))


if __name__ == "__main__":
    main()










