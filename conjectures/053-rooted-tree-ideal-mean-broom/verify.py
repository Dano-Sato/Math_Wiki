"""Exact enumeration of rooted-tree poset ideal means (finite range only)."""

from fractions import Fraction
import json
import sys


def convolve(left, right):
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def is_broom(shape):
    if len(shape) <= 1:
        return all(is_broom(child) for child in shape)
    return all(len(child) == 0 for child in shape)


def encode_shape(shape):
    return [encode_shape(child) for child in shape]


def is_unimodal(sequence):
    descending = False
    for left, right in zip(sequence, sequence[1:]):
        if right < left:
            descending = True
        elif right > left and descending:
            return False
    return True


def broom_mean(n, h):
    m = n - h
    numerator = h * (h - 1) // 2 + h * (2**m)
    if m:
        numerator += m * (2 ** (m - 1))
    return Fraction(numerator, h + 2**m)


def enumerate_shapes(limit):
    by_size = {1: [()]}
    polynomials = {(): [1, 1]}
    report = []

    for n in range(1, limit + 1):
        if n > 1:
            pool = []
            for size in range(1, n):
                pool.extend((size, shape) for shape in by_size[size])

            shapes = []

            def generate(start, remaining, chosen):
                if remaining == 0:
                    shapes.append(tuple(chosen))
                    return
                for i in range(start, len(pool)):
                    size, child = pool[i]
                    if size <= remaining:
                        generate(i, remaining - size, chosen + [child])

            generate(0, n - 1, [])
            by_size[n] = shapes
        else:
            shapes = by_size[1]

        means = []
        nonunimodal = []
        for shape in shapes:
            product = [1]
            for child in shape:
                product = convolve(product, polynomials[child])
            polynomial = [1] + product
            polynomials[shape] = polynomial
            total_ideals = sum(polynomial)
            total_size = sum(k * count for k, count in enumerate(polynomial))
            means.append((Fraction(total_size, total_ideals), shape))
            if not is_unimodal(polynomial) and not nonunimodal:
                nonunimodal = [
                    {
                        "shape": encode_shape(shape),
                        "profile": polynomial,
                    }
                ]

        maximum = max(mean for mean, _ in means)
        winners = [shape for mean, shape in means if mean == maximum]
        broom_candidates = [
            (broom_mean(n, h), h, n - h) for h in range(1, n + 1)
        ]
        broom_maximum = max(value for value, _, _ in broom_candidates)
        broom_parameters = [
            {"stem_vertices": h, "terminal_leaves": m}
            for value, h, m in broom_candidates
            if value == broom_maximum
        ]
        if maximum != broom_maximum or not all(is_broom(shape) for shape in winners):
            raise AssertionError(f"counterexample to broom maximum at n={n}")

        report.append(
            {
                "n": n,
                "rooted_unlabeled_shapes": len(shapes),
                "maximum_mean": f"{maximum.numerator}/{maximum.denominator}",
                "broom_parameters_attaining_maximum": broom_parameters,
                "maximizing_shapes": len(winners),
                "all_maximizers_are_brooms": all(is_broom(shape) for shape in winners),
                "first_nonunimodal_ideal_profile": nonunimodal[0] if nonunimodal else None,
            }
        )
    return report


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    if not 1 <= limit <= 15:
        raise SystemExit("limit must be between 1 and 15")
    print(json.dumps(enumerate_shapes(limit), indent=2))
