"""Exact subset-DP verification for conjecture 056; standard library only."""

from itertools import permutations
import json
from pathlib import Path


def coefficients_dp(n: int) -> list[int]:
    """Count Ménage permutations by descents using a subset recurrence.

    Let F_i(S,j;k) count legal prefixes of length i using value set S,
    ending in j, with k descents. At position i, append each unused x except
    the two forbidden values i and i+1 (mod n); add one descent iff j>x.
    """
    # State (used-value mask, last value) -> descent-count polynomial.
    layer = {(0, -1): [1] + [0] * (n - 1)}
    for position in range(n):
        following = {}
        for (mask, last), polynomial in layer.items():
            available = ((1 << n) - 1) ^ mask
            while available:
                bit = available & -available
                available -= bit
                value = bit.bit_length() - 1
                if value == position or value == (position + 1) % n:
                    continue
                target = (mask | bit, value)
                out = following.setdefault(target, [0] * n)
                shift = int(last >= 0 and last > value)
                for descents, count in enumerate(polynomial):
                    if count and descents + shift < n:
                        out[descents + shift] += count
        layer = following

    result = [0] * n
    for (_, _last), polynomial in layer.items():
        for descents, count in enumerate(polynomial):
            result[descents] += count
    return result


def coefficients_bruteforce(n: int) -> list[int]:
    """Independent direct enumeration, used to cross-check the DP through 10."""
    result = [0] * n
    for permutation in permutations(range(n)):
        if any(permutation[i] == i or permutation[i] == (i + 1) % n
               for i in range(n)):
            continue
        descents = sum(permutation[i] > permutation[i + 1]
                       for i in range(n - 1))
        result[descents] += 1
    return result


def is_log_concave(values: list[int]) -> bool:
    return all(values[k] ** 2 >= values[k - 1] * values[k + 1]
               for k in range(1, len(values) - 1))


def is_unimodal(values: list[int]) -> bool:
    return any(
        all(values[i] <= values[i + 1] for i in range(peak))
        and all(values[i] >= values[i + 1]
                for i in range(peak, len(values) - 1))
        for peak in range(len(values))
    )


if __name__ == "__main__":
    rows = {}
    for n in range(3, 19):
        row = coefficients_dp(n)
        if n <= 10:
            assert row == coefficients_bruteforce(n), (n, row)
        rows[str(n)] = {
            "coefficients_k_0_to_n_minus_1": row,
            "log_concave": is_log_concave(row),
            "unimodal": is_unimodal(row),
        }
        print(n, row, "log-concave:", rows[str(n)]["log_concave"],
              "unimodal:", rows[str(n)]["unimodal"])

    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
