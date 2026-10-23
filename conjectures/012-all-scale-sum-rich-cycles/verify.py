"""Verify the displayed all-scale sum-rich cyclic permutations."""

EXAMPLES = {
    3: (1, 2, 3),
    4: (1, 2, 4, 3),
    5: (1, 2, 3, 4, 5),
    6: (1, 2, 3, 4, 6, 5),
    7: (1, 2, 3, 4, 5, 6, 7),
    8: (1, 2, 3, 4, 8, 7, 6, 5),
    9: (1, 2, 3, 4, 5, 6, 8, 9, 7),
    10: (1, 2, 3, 4, 5, 6, 8, 10, 9, 7),
    11: tuple(range(1, 12)),
    12: (1, 2, 3, 4, 5, 6, 7, 12, 10, 8, 9, 11),
    13: tuple(range(1, 14)),
}


def is_all_scale_sum_rich(p):
    n = len(p)
    if sorted(p) != list(range(1, n + 1)):
        return False
    doubled = p + p
    for k in range(1, n // 2 + 1):
        sums = [sum(doubled[i : i + k]) for i in range(n)]
        if len(set(sums)) != n:
            return False
    return True


if __name__ == "__main__":
    for n, p in EXAMPLES.items():
        assert len(p) == n and is_all_scale_sum_rich(p), (n, p)
    print(f"verified {len(EXAMPLES)} displayed witnesses (n=3..13)")
