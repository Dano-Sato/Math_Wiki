"""Exact independence-polynomial counts for the coprimality graph on [n]."""

from functools import lru_cache
from math import gcd
from time import perf_counter


def pairwise_coprime_counts(n: int) -> list[int]:
    # 1 is isolated in the coprimality graph and contributes a factor (1+x).
    vertices = list(range(2, n + 1))
    m = len(vertices)
    adjacency = [0] * m
    for i, a in enumerate(vertices):
        for j in range(i + 1, m):
            if gcd(a, vertices[j]) > 1:
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i

    @lru_cache(maxsize=None)
    def independent_polynomial(mask: int) -> tuple[int, ...]:
        if mask == 0:
            return (1,)

        # A high-degree pivot typically reduces the recursion tree.
        candidates = mask
        pivot = -1
        best_degree = -1
        while candidates:
            bit = candidates & -candidates
            i = bit.bit_length() - 1
            degree = (adjacency[i] & mask).bit_count()
            if degree > best_degree:
                pivot, best_degree = i, degree
            candidates ^= bit

        pivot_bit = 1 << pivot
        without = independent_polynomial(mask ^ pivot_bit)
        with_mask = mask & ~(pivot_bit | adjacency[pivot])
        with_pivot = independent_polynomial(with_mask)
        result = [0] * max(len(without), len(with_pivot) + 1)
        for k, value in enumerate(without):
            result[k] += value
        for k, value in enumerate(with_pivot):
            result[k + 1] += value
        return tuple(result)

    polynomial = independent_polynomial((1 << m) - 1)
    # Multiplication by (1+x), accounting for arbitrary inclusion of 1.
    result = [0] * (len(polynomial) + 1)
    for k, value in enumerate(polynomial):
        result[k] += value
        result[k + 1] += value
    return result


def is_unimodal(values: list[int]) -> bool:
    decreasing = False
    for left, right in zip(values, values[1:]):
        if right < left:
            decreasing = True
        elif right > left and decreasing:
            return False
    return True


def is_log_concave(values: list[int]) -> bool:
    return all(values[k] ** 2 >= values[k - 1] * values[k + 1] for k in range(1, len(values) - 1))


def brute_counts(n: int) -> list[int]:
    """Independent recursive enumeration, used only for small-n cross-checks."""
    counts = [0] * (n + 1)

    def visit(next_value: int, chosen: tuple[int, ...]) -> None:
        counts[len(chosen)] += 1
        for value in range(next_value, n + 1):
            if all(gcd(value, old) == 1 for old in chosen):
                visit(value + 1, chosen + (value,))

    visit(1, ())
    return counts


start = perf_counter()
first_unimodality_failure = None
first_log_concavity_failure = None
results = {}
for n in range(2, 101):
    counts = pairwise_coprime_counts(n)
    results[n] = counts
    if first_unimodality_failure is None and not is_unimodal(counts):
        first_unimodality_failure = (n, counts)
    if first_log_concavity_failure is None and not is_log_concave(counts):
        first_log_concavity_failure = (n, counts)
    if n <= 40 or n % 10 == 0:
        print(n, counts, "unimodal=", is_unimodal(counts), "log_concave=", is_log_concave(counts))

print("first_unimodality_failure:", first_unimodality_failure)
print("first_log_concavity_failure:", first_log_concavity_failure)
for n in range(2, 19):
    assert results[n] == brute_counts(n)[: len(results[n])]
    assert not any(brute_counts(n)[len(results[n]) :])
print("independent_brute_force_crosschecks:", 17, "passed")
print("elapsed_seconds:", round(perf_counter() - start, 3))
