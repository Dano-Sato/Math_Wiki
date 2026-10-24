"""Reconstruct the v0.3 proof's prime/boundary witnesses in the old exact cycles.

This illustrates and checks the proof on the 13 cycles classified through n=6.
The general proof is in conjectures.md T1; it is not inferred from this test.
All computations below use integers and the existing experiment.json is read-only.
"""

import hashlib
import json
from math import gcd, isqrt
from pathlib import Path


def step(state):
    return tuple(gcd(a, state[(i + 1) % len(state)]) + 1 for i, a in enumerate(state))


def prime(number):
    return number >= 2 and all(number % d for d in range(2, isqrt(number) + 1))


def witness(initial, expected_period):
    cycle = []
    state = tuple(initial)
    for _ in range(expected_period):
        cycle.append(state)
        state = step(state)
    assert state == tuple(initial)
    assert len(set(cycle)) == expected_period
    assert all(len(set(row)) > 1 for row in cycle)
    support = {a for row in cycle for a in row}
    m, M = min(support), max(support)
    assert support == set(range(m, M + 1))
    assert m >= 2 and 2 * (m - 1) <= M

    h = M // 2
    q = next(q for q in range(h + 1, 2 * h + 1) if prime(q))
    assert m <= q <= M and M < 2 * q
    for t, row in enumerate(cycle):
        for i, a in enumerate(row):
            b = row[(i + 1) % len(row)]
            if a == q and b != q:
                assert 1 <= b <= M < 2 * q
                assert gcd(q, b) == 1
                assert cycle[(t + 1) % len(cycle)][i] == 2
                return {
                    "n": len(initial),
                    "period": expected_period,
                    "representative": initial,
                    "minimum": m,
                    "maximum": M,
                    "half_bound": h,
                    "bertrand_prime": q,
                    "boundary_time": t,
                    "boundary_index": i,
                    "boundary_inputs": [q, b],
                    "next_value": 2,
                }
    raise AssertionError("No prime-to-nonprime-level boundary found")


def main():
    source = Path(__file__).with_name("experiment.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    rows = [
        witness(cycle["representative"], cycle["period"])
        for entry in data["exact_cycles"]
        for cycle in entry["cycles"]
    ]
    assert len(rows) == 13
    result = {
        "date": "2026-10-24",
        "proof_version": "0.3",
        "source_experiment_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "cycles_checked": len(rows),
        "all_prime_boundary_witnesses_valid": True,
        "witnesses": rows,
        "scope": "Exact reconstruction on the previously classified cycles of sizes 3..6. The universal theorem uses the separate written proof and Bertrand's postulate, not this finite list.",
    }
    output = Path(__file__).with_name("bertrand_witnesses.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
