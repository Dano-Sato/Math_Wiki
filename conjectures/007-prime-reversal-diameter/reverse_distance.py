"""Distance of the reversed permutation under prime-length reversals (conjecture 007-1, Claude).

    python reverse_distance.py --max 12 --output reverse_distance.json

Exact bidirectional breadth-first search between the identity and (n, n-1, ..., 1).
"""

import argparse
import json
import time
from pathlib import Path


def is_prime(k):
    return k > 1 and all(k % d for d in range(2, int(k ** 0.5) + 1))


def distance(n, target):
    lengths = [L for L in range(2, n + 1) if is_prime(L)]
    moves = [(i, L) for L in lengths for i in range(n - L + 1)]
    start, goal = tuple(range(1, n + 1)), tuple(target)
    if start == goal:
        return 0
    seen_a, seen_b = {start: 0}, {goal: 0}
    layer_a, layer_b = [start], [goal]
    while True:
        if len(layer_a) > len(layer_b):
            seen_a, seen_b, layer_a, layer_b = seen_b, seen_a, layer_b, layer_a
        nxt = []
        for p in layer_a:
            d = seen_a[p]
            for i, L in moves:
                r = p[:i] + p[i:i + L][::-1] + p[i + L:]
                if r in seen_b:
                    return d + 1 + seen_b[r]
                if r not in seen_a:
                    seen_a[r] = d + 1
                    nxt.append(r)
        layer_a = nxt


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max", type=int, default=12)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("reverse_distance.json"))
    args = parser.parse_args()
    rows = []
    for n in range(2, args.max + 1):
        t = time.time()
        d = distance(n, range(n, 0, -1))
        rows.append({"n": n, "n_is_prime": is_prime(n), "distance_of_reverse": d, "seconds": round(time.time() - t, 2)})
        print(rows[-1], flush=True)
    args.output.write_text(json.dumps({
        "implementation": "reverse_distance.py (Claude)",
        "rows": rows,
        "scope": "Exact distances for the listed n.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
