"""Evidence for the constant 3/2 in conjecture 003 (Claude).

    go build -o balance.exe balance.go
    python ratio_search.py --exe balance.exe --output ratio_search.json

ratio(A) = (min over circular arrangements of max_k R_k) / (max A - min A),
computed exactly by balance.go -optimum (binary search over exhaustive checks).
"""

import argparse
import json
import random
import subprocess
import time
from itertools import combinations_with_replacement
from pathlib import Path


def optimum(exe, values):
    out = subprocess.run([exe, "-set", ",".join(map(str, values)), "-optimum"],
                         capture_output=True, text=True, check=True).stdout
    return int(out.split("optimum=")[1].split()[0])


def ratio(exe, values):
    return optimum(exe, values) / (max(values) - min(values))


def grid(exe, q, size):
    """All multisets of size `size` from {0, 1/q, ..., 1} containing 0 and 1 (scaled by q)."""
    worst, arg, count = 0.0, None, 0
    for middle in combinations_with_replacement(range(q + 1), size - 2):
        values = sorted([0, q, *middle])
        r = ratio(exe, values)
        count += 1
        if r > worst:
            worst, arg = r, values
    return {"kind": "grid", "q": q, "size": size, "checked": count, "worst_ratio": worst, "worst_set": arg}


def failures(exe, n, trials, rng):
    """How often max - min itself is not achievable, on random integer sets."""
    bad = []
    for t in range(trials):
        if t % 3 == 0:
            values = sorted(rng.randint(1, 1000) for _ in range(n))
        elif t % 3 == 1:
            values = sorted(rng.sample(range(1, 60), n))
        else:
            values = sorted([1, 1000] + [rng.choice([1, 2, 500, 999, 1000]) for _ in range(n - 2)])
        if optimum(exe, values) > max(values) - min(values):
            bad.append(values)
    return {"kind": "random", "n": n, "trials": trials, "failures": len(bad), "examples": bad[:3]}


def climb(exe, n, seconds, rng):
    """Hill climbing on integer sets in [0, 120] for a large ratio."""
    deadline = time.time() + seconds
    worst, arg = 0.0, None
    while time.time() < deadline:
        x = [0, 120] + [rng.choice([0, 120, rng.randint(0, 120)]) for _ in range(n - 2)]
        r = ratio(exe, x)
        for _ in range(25):
            y = x[:]
            y[rng.randrange(2, n)] = rng.choice([0, 60, 120, rng.randint(0, 120)])
            ry = ratio(exe, y)
            if ry >= r:
                x, r = y, ry
        if r > worst:
            worst, arg = r, sorted(x)
    return {"kind": "hill-climb", "n": n, "seconds": seconds, "worst_ratio": worst, "worst_set": arg}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exe", default="balance.exe")
    parser.add_argument("--seconds", type=float, default=60, help="hill-climb time per n")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("ratio_search.json"))
    args = parser.parse_args()
    rng = random.Random(20261024)
    rows = []

    def save(row):
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        args.output.write_text(json.dumps({
            "implementation": "ratio_search.py + balance.go (Claude)",
            "rows": rows,
            "scope": "Finite checks only. Hill-climb maxima are lower bounds for the worst ratio at that n.",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for q, size in [(4, 6), (4, 7), (4, 8), (6, 6), (6, 7)]:
        save(grid(args.exe, q, size))
    for n in range(4, 12):
        save(failures(args.exe, n, 300 if n <= 9 else 120, rng))
    for n in (8, 9, 10, 11):
        save(climb(args.exe, n, args.seconds, rng))


if __name__ == "__main__":
    main()
