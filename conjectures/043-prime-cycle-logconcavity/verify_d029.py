"""Exact Sturm certificate that the n=13 section polynomial is not real-rooted."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from verify_d026 import exact_rows


def variation_count(signs: list[int]) -> int:
    return sum(left != right for left, right in zip(signs, signs[1:]))


def signs_at_infinity(sequence, negative: bool) -> list[int]:
    signs = []
    for polynomial in sequence:
        sign = int(sp.sign(polynomial.LC()))
        if negative and polynomial.degree() % 2:
            sign *= -1
        signs.append(sign)
    return signs


def main() -> None:
    n = 13
    row = exact_rows(n)[n]
    variable = sp.symbols("y")
    polynomial = sp.Poly(
        sum(coefficient * variable**k for k, coefficient in enumerate(row[: n // 2 + 1])),
        variable,
    )
    sturm = polynomial.sturm()
    negative_signs = signs_at_infinity(sturm, negative=True)
    positive_signs = signs_at_infinity(sturm, negative=False)
    negative_variations = variation_count(negative_signs)
    positive_variations = variation_count(positive_signs)
    real_roots = negative_variations - positive_variations
    assert polynomial.degree() == 6
    assert real_roots == 2

    result = {
        "claim": "043 v0.1, failure of the real-rootedness route at n=13",
        "coefficients_ascending": [str(c) for c in row[: n // 2 + 1]],
        "sturm_signs_at_negative_infinity": negative_signs,
        "sturm_variations_at_negative_infinity": negative_variations,
        "sturm_signs_at_positive_infinity": positive_signs,
        "sturm_variations_at_positive_infinity": positive_variations,
        "distinct_real_root_count": real_roots,
        "degree": polynomial.degree(),
        "conclusion": "the degree-6 polynomial is not real-rooted",
    }
    output = Path(__file__).with_name("verify_d029.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "coefficients_ascending",
        "sturm_variations_at_negative_infinity",
        "sturm_variations_at_positive_infinity",
        "distinct_real_root_count",
        "degree",
        "conclusion",
    )}, indent=2))


if __name__ == "__main__":
    main()
