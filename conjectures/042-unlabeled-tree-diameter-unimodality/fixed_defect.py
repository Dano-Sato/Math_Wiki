"""Exact stable fixed-diameter-deficit counts; proof in fixed_defect.md.

Usage:
    python conjectures/042-unlabeled-tree-diameter-unimodality/fixed_defect.py --n 1000000000000 --k 6

The formula is proved for k >= 0 and n >= 3*k+2. It counts unlabeled
unrooted trees with n vertices and diameter n-1-k. It uses finite rooted
tree data through size 2*k+1, followed by truncated integer series powers.
There is no floating-point fitting or polynomial interpolation.
"""

from __future__ import annotations

import argparse
import json
from math import comb


def product(left: list[int], right: list[int], degree: int) -> list[int]:
    result = [0] * (degree+1)
    for i, a in enumerate(left[:degree+1]):
        if a:
            for j, b in enumerate(right[:degree+1-i]):
                if b:
                    result[i+j] += a*b
    return result


def power(series: list[int], exponent: int, degree: int) -> list[int]:
    if exponent < 0:
        raise ValueError("series exponent must be nonnegative")
    result = [1] + [0]*degree
    base = series[:degree+1] + [0]*max(0, degree+1-len(series))
    while exponent:
        if exponent % 2:
            result = product(result, base, degree)
        exponent //= 2
        if exponent:
            base = product(base, base, degree)
    return result


def substitute_square(series: list[int], degree: int) -> list[int]:
    return [series[j//2] if j % 2 == 0 else 0 for j in range(degree+1)]


def multiset_by_product(types: list[int], degree: int) -> list[int]:
    """Euler PRODUCT, independent of height_gf.py's Euler-transform recurrence."""
    result = [1] + [0]*degree
    for size in range(1, min(len(types), degree+1)):
        count = types[size]
        if not count:
            continue
        factor = [0]*(degree+1)
        for multiplicity in range(degree//size+1):
            factor[multiplicity*size] = comb(count+multiplicity-1, multiplicity)
        result = product(result, factor, degree)
    return result


class DefectCounter:
    def __init__(self, max_defect: int):
        if max_defect < 0:
            raise ValueError("max_defect must be nonnegative")
        self.max_defect = max_defect
        size = 2*max_defect+1
        first = [0]*(size+1)
        first[1] = 1
        self.rooted = [first]  # R_0(x)=x, height <= 0.
        for _ in range(max_defect):
            forest = multiset_by_product(self.rooted[-1], size)
            self.rooted.append([0]+forest[:-1])

    def base(self, k: int) -> tuple[list[int], list[int]]:
        """Return M(y) (side forests), B_k(y) (height exactly k), mod y^(k+1)."""
        if not 0 <= k <= self.max_defect:
            raise ValueError("k outside the prepared finite table")
        broad = self.rooted[k]
        previous = self.rooted[k-1] if k else [0]*len(broad)
        side_forests = [broad[q+1] for q in range(k+1)]
        endpoint_core = [broad[k+1+e]-previous[k+1+e] for e in range(k+1)]
        return side_forests, endpoint_core

    def count(self, n: int, k: int) -> int:
        if n < 3*k+2:
            raise ValueError("proved formula requires n >= 3*k+2")
        side, core = self.base(k)
        length = n-3*k-2
        ordinary = product(product(core, core, k), power(side, length, k), k)[k]
        reflection = product(
            substitute_square(core, k),
            power(substitute_square(side, k), length//2, k), k,
        )
        if length % 2:
            reflection = product(side, reflection, k)
        result, remainder = divmod(ordinary+reflection[k], 2)
        if remainder:
            raise ArithmeticError("nonintegral stable center count")
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    if args.k < 0 or args.n < 3*args.k+2:
        parser.error("require k >= 0 and n >= 3*k+2")
    counter = DefectCounter(args.k)
    print(json.dumps({"n": args.n, "deficit": args.k,
                      "diameter": args.n-1-args.k,
                      "count": counter.count(args.n, args.k),
                      "proved_valid_from_n": 3*args.k+2}, indent=2))


if __name__ == "__main__":
    main()
