"""Exact finite check of Euclidean-division-count unimodality for all N <= LIMIT."""

from math import gcd


LIMIT = 3000
hist = [0]
checked_inequalities = 0
first_logconcavity_failure = None


def division_count(a: int, b: int) -> int:
    """Number of divisions on ordered input (b, a), with b > a."""
    count = 0
    while a:
        b, a = a, b % a
        count += 1
    return count


def is_unimodal(values: list[int]) -> bool:
    """Allow a flat peak; reject any increase after a strict decrease."""
    descending = False
    for left, right in zip(values, values[1:]):
        if right < left:
            descending = True
        elif right > left and descending:
            return False
    return True


for n in range(2, LIMIT + 1):
    # Add exactly the reduced fractions whose denominator is n.
    for a in range(1, n):
        if gcd(a, n) == 1:
            k = division_count(a, n)
            while len(hist) <= k:
                hist.append(0)
            hist[k] += 1

    values = hist[1:]
    if not is_unimodal(values):
        raise AssertionError(f"unimodality fails at N={n}: {values}")

    for k in range(2, len(hist) - 1):
        checked_inequalities += 1
        if first_logconcavity_failure is None and hist[k] ** 2 < hist[k - 1] * hist[k + 1]:
            first_logconcavity_failure = (n, k, hist[k - 1 : k + 2])

    if n == 405:
        assert hist[1:] == [404, 2084, 5691, 9930, 11909, 10151, 6175, 2681, 802, 145, 12, 1]

print(
    {
        "max_denominator_bound": LIMIT,
        "unimodality_checks": LIMIT - 1,
        "status": "all passed",
        "logconcavity_inequalities_checked": checked_inequalities,
        "first_logconcavity_failure": first_logconcavity_failure,
    }
)
