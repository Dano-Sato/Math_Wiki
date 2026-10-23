"""Heuristic search for rings meeting the L1 lower bound floor(n/2) exactly (Claude, D005).

    python floor_search.py --from 23 --to 40 --output floor_search.json

Every witness is re-checked from the definition. A failure to find one proves nothing.
"""

import argparse
import json
import time
from math import exp
from pathlib import Path
from random import Random


def widths(order):
    n = len(order)
    pairs = [order[i] + order[(i + 1) % n] for i in range(n)]
    triples = [order[i] + order[(i + 1) % n] + order[(i + 2) % n] for i in range(n)]
    return max(pairs) - min(pairs), max(triples) - min(triples)


def energy(order, target):
    # excess over the target, plus a weak pull toward small total width
    x, y = widths(order)
    return max(0, x - target) + max(0, y - target) + 0.02 * (x + y)


def search(n, target, seconds, seed):
    rng = Random(seed)
    deadline = time.time() + seconds
    restarts = 0
    while time.time() < deadline:
        restarts += 1
        order = list(range(1, n + 1))
        rng.shuffle(order)
        e = energy(order, target)
        steps = 200000
        for step in range(steps):
            i, j = rng.sample(range(n), 2)
            order[i], order[j] = order[j], order[i]
            new = energy(order, target)
            temperature = max(0.05, 2.0 * (1 - step / steps) ** 2)
            if new <= e or rng.random() < exp((e - new) / temperature):
                e = new
                if max(widths(order)) <= target:
                    return order, restarts
            else:
                order[i], order[j] = order[j], order[i]
            if step % 5000 == 0 and time.time() > deadline:
                break
    return None, restarts


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="lo", type=int, default=23)
    parser.add_argument("--to", dest="hi", type=int, default=40)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("floor_search.json"))
    args = parser.parse_args()
    rows = []
    for n in range(args.lo, args.hi + 1):
        target = n // 2
        order, restarts = search(n, target, args.seconds, 20261023 + n)
        if order is not None:
            if sorted(order) != list(range(1, n + 1)) or max(widths(order)) > target:
                raise AssertionError(f"bad witness at n={n}")
        rows.append({"n": n, "target_floor_half": target, "found": order is not None,
                     "widths": list(widths(order)) if order else None, "witness": order,
                     "restarts": restarts, "seconds_limit": args.seconds})
        print(f"n={n} floor={target} found={order is not None}", flush=True)
        args.output.write_text(json.dumps({
            "implementation": "floor_search.py (Claude), simulated annealing",
            "rows": rows,
            "scope": "found=true is a checked witness that E_n = floor(n/2). found=false proves nothing.",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
