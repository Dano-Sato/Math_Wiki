from itertools import permutations
from math import comb, gcd
import json
from pathlib import Path


def mobius(n: int) -> int:
    x, sign, p = n, 1, 2
    while p * p <= x:
        if x % (p * p) == 0:
            return 0
        if x % p == 0:
            sign = -sign
            x //= p
            while x % p == 0:
                x //= p
        p += 1
    return -sign if x > 1 else sign


def lyndon_count(n: int, k: int) -> int:
    g = gcd(n, k)
    numerator = sum(mobius(d) * comb(n // d, k // d)
                    for d in range(1, g + 1) if g % d == 0)
    assert numerator % n == 0
    return numerator // n


def peak_row(n: int) -> list[int]:
    row = [0]  # T(n,1)=0
    for i in range(1, n):
        correction = (lyndon_count(n // 2, i // 2)
                      if n % 2 == 0 and (n + i) % 4 == 2 else 0)
        row.append(lyndon_count(n, i) + correction - row[-1])
    return row


def is_single_cycle(p: tuple[int, ...]) -> bool:
    n = len(p)
    visited = set()
    x = 0
    for _ in range(n):
        if x in visited:
            return False
        visited.add(x)
        x = p[x] - 1
    return x == 0 and len(visited) == n


def is_unimodal(p: tuple[int, ...]) -> bool:
    peak = p.index(len(p))
    return (all(p[i] < p[i + 1] for i in range(peak)) and
            all(p[i] > p[i + 1] for i in range(peak, len(p) - 1)))


def is_weakly_unimodal(a: list[int]) -> bool:
    fell = False
    for x, y in zip(a, a[1:]):
        if y < x:
            fell = True
        elif y > x and fell:
            return False
    return True


rows = {str(n): peak_row(n) for n in range(3, 151)}
assert all(is_weakly_unimodal(a) for a in rows.values())

brute = {}
for n in range(3, 10):
    actual = [0] * n
    for p in permutations(range(1, n + 1)):
        if is_single_cycle(p) and is_unimodal(p):
            actual[p.index(n)] += 1
    assert actual == peak_row(n), (n, actual, peak_row(n))
    brute[str(n)] = actual

summary = {
    "formula_source": "Archer-Lauderdale, Enumeration of cyclic permutations in vector grid classes, Lemma 4.4",
    "formula_checked_n": [3, 150],
    "formula_unimodality_verified": True,
    "direct_permutation_enumeration_n": [3, 9],
    "direct_counts_match_formula": True,
    "sample_n10": peak_row(10),
    "sample_n12": peak_row(12),
    "brute_rows": brute,
    "limitation": "Finite exact checks only; no proof for all n."
}
Path(__file__).with_name("experiment.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "brute_rows"}, ensure_ascii=False, indent=2))
