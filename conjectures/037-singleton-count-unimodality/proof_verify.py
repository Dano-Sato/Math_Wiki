"""Exact finite audits of the auxiliary inequalities in the 037 v0.3 proof.

The universal proof is proof_unimodality.md; this script checks for algebra,
parity, indexing, and small-case mistakes. It does not prove infinite claims.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from review_verify import bell_triangle_no_singletons, require


def mul_linear(p: tuple[int, int], q: tuple[int, int]) -> tuple[int, int, int]:
    """Coefficients of (p[0]+p[1]*e)*(q[0]+q[1]*e)."""
    return (p[0] * q[0], p[0] * q[1] + p[1] * q[0], p[1] * q[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=2000)
    args = parser.parse_args()
    if args.max_n < 10:
        parser.error("--max-n must be at least 10")
    b = bell_triangle_no_singletons(args.max_n + 1)
    for m in range(5, args.max_n + 1):
        require(b[m] ** 2 + b[m] * b[m - 1] > b[m - 1] * b[m + 1],
                f"Ratio step bound fails at {m}")
        require(b[m] ** 2 + 2 * b[m] * b[m - 1] > m * b[m - 1] ** 2,
                f"Quadratic ratio bound fails at {m}")
        require(2 * b[m] <= 3 * (m - 1) * b[m - 1],
                f"Elementary ratio upper bound fails at {m}")
    for m in range(6, args.max_n + 1):
        require(2 * b[m - 1] - 1 >= 2 * m, f"Linear H bound fails at {m}")
    for m in range(9, args.max_n + 1):
        require(2 * b[m - 1] - 1 >= 8 * m * m,
                f"Quadratic H bound fails at {m}")
    for m in range(4, args.max_n + 1):
        require((m + 1) * b[m] ** 2 + b[m] * b[m + 1]
                > m * b[m - 1] * b[m + 1], f"Strict threshold bound fails at {m}")

    # Verify (16) symbolically as a polynomial identity, for every tested m.
    for m in range(3, args.max_n + 1):
        epsilon = (-1) ** m
        prev, cur, following = ((epsilon, b[m - 1]), (-epsilon, b[m]),
                                (epsilon, b[m + 1]))
        square = mul_linear(cur, cur)
        cross = mul_linear(cur, prev)
        outer = mul_linear(prev, following)
        fa = tuple(square[d] + cross[d] - outer[d] for d in range(3))
        correction = (epsilon * (cur[0] + 2 * prev[0] + following[0]) - 1,
                      epsilon * (cur[1] + 2 * prev[1] + following[1]), 0)
        rhs = tuple(fa[d] + correction[d] for d in range(3))
        f = b[m] ** 2 + b[m] * b[m - 1] - b[m - 1] * b[m + 1]
        require(rhs == (0, 0, f), f"Parity identity (16) fails at {m}")

    for t in range(2, 31):
        for j in range(1, 31):
            derivative = (Fraction(1, j) - Fraction(1, j + 2)
                          + t * (Fraction(1, j + 1) - Fraction(1, j)))
            expected = Fraction((2 - t) * j + 2 - 2 * t, j * (j + 1) * (j + 2))
            require(derivative == expected and derivative < 0,
                    f"Log derivative error: t={t}, j={j}")
            lam = Fraction(j, j + 2) * Fraction(j + 1, j) ** t
            require(lam > Fraction(j + t, j + 2),
                    f"Strict Bernoulli bound fails: t={t}, j={j}")

    bases = {str(m): b[m] ** 2 + b[m] * b[m - 1] - b[m - 1] * b[m + 1]
             for m in (5, 7)}
    require(bases == {"5": 1, "7": 3571}, "Wrong initial values")
    result = {
        "conjecture": "037", "version": "0.3", "max_m": args.max_n,
        "ratio_step_bound": "b[m]^2+b[m]*b[m-1]>b[m-1]*b[m+1], m>=5",
        "quadratic_ratio_bound": "b[m]^2+2*b[m]*b[m-1]>m*b[m-1]^2, m>=5",
        "all_finite_inequality_checks_passed": True,
        "parity_identity": {"range": [3, args.max_n], "exact_polynomial_check": True},
        "positive_kernel_finite_algebra_checks": {"t": [2, 30], "j": [1, 30]},
        "initial_F_values": bases,
        "initial_H_values": {"6": 2 * b[5] - 1, "9": 2 * b[8] - 1},
        "scope": "Finite cross-checks only; the proof for all indices is in proof_unimodality.md. No approximation to e or truncated infinite sum is used.",
    }
    output = Path(__file__).with_name("proof_verification.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
