"""Exact small-ring cycle enumeration and seeded tests for conjecture 009."""

import argparse
import json
from itertools import product
from math import gcd
from pathlib import Path
from random import Random


def step(state):
    return tuple(gcd(value, state[(i + 1) % len(state)]) + 1 for i, value in enumerate(state))


def uniform(state):
    return all(value == state[0] for value in state)


def cycle_info(cycle):
    assert cycle and all(step(frame) == cycle[(i + 1) % len(cycle)] for i, frame in enumerate(cycle))
    support = sorted({value for frame in cycle for value in frame})
    assert max(support) <= 2 * len(cycle[0]) - 2
    return {
        "period": len(cycle), "minimum": min(support), "maximum": max(support),
        "has_two": 2 in support,
        "gap_free_support": support == list(range(2, max(support) + 1)),
        "support": support, "representative": list(cycle[0]),
    }


def exact_cycles(n):
    """Every nonuniform periodic state lies in [2,2n-2]^n (proved in MD).

    Paths that become uniform or leave this box cannot themselves be cycles
    in the box. Every remaining cycle is discovered by functional-graph tracing.
    """
    bound = 2 * n - 2
    done = set()
    cycles = []
    candidates = 0
    for initial in product(range(2, bound + 1), repeat=n):
        candidates += 1
        if initial in done:
            continue
        path, positions = [], {}
        state = initial
        while state not in done and not uniform(state) and max(state) <= bound:
            if state in positions:
                cycles.append(cycle_info(path[positions[state]:]))
                break
            positions[state] = len(path)
            path.append(state)
            state = step(state)
        done.update(path)
        if not path:
            done.add(initial)
    return {
        "n": n, "periodic_state_box": [2, bound], "enumerated_states": candidates,
        "number_of_nonuniform_cycles": len(cycles), "cycles": cycles,
        "all_cycles_have_two": all(c["has_two"] for c in cycles),
        "all_cycle_supports_gap_free": all(c["gap_free_support"] for c in cycles),
    }


def orbit(initial, cap):
    state = tuple(initial)
    bound = max(max(state) + len(state) - 2, 2 * len(state) - 2)
    path, positions = [], {}
    for time in range(cap + 1):
        if uniform(state):
            return {"kind": "uniform", "time": time, "level": state[0]}
        assert max(state) <= bound, (initial, state, bound)
        if state in positions:
            return {"kind": "periodic", "transient": positions[state], **cycle_info(path[positions[state]:])}
        positions[state] = len(path)
        path.append(state)
        state = step(state)
    return {"kind": "step_limit", "limit": cap}


def samples(n, count, cap):
    rng = Random(20261024 + n)
    kinds = {"uniform": 0, "periodic": 0, "step_limit": 0}
    periods = set()
    maximum = 0
    failures = []
    for k in range(count):
        mode = k % 4
        if mode == 0:
            initial = [rng.randrange(1, 1001) for _ in range(n)]
        elif mode == 1:
            initial = [210 * rng.randrange(1, 11) for _ in range(n)]
        elif mode == 2:
            level = 10 ** 12 + rng.randrange(1, 1000)
            initial = [level] * n
            initial[rng.randrange(n)] += 1
        else:
            initial = [rng.randrange(2, 6) for _ in range(n)]
        result = orbit(initial, cap)
        kinds[result["kind"]] += 1
        if result["kind"] == "periodic":
            periods.add(result["period"])
            maximum = max(maximum, result["maximum"])
            if not result["has_two"] or not result["gap_free_support"]:
                failures.append({"initial": initial, "result": result})
    return {"n": n, "cases": count, "outcomes": kinds, "periods": sorted(periods),
            "largest_periodic_value": maximum, "counterexamples": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact-through", type=int, default=6)
    parser.add_argument("--samples-per-size", type=int, default=100)
    parser.add_argument("--step-limit", type=int, default=20000)
    args = parser.parse_args()
    if not 2 <= args.exact_through <= 6 or args.samples_per_size < 1 or args.step_limit < 1:
        parser.error("exact-through must be 2..6; sample count and step limit must be positive")
    assert step((2, 2, 3)) == (3, 2, 2)
    assert step((7, 7, 7)) == (8, 8, 8)
    exact = []
    for n in range(2, args.exact_through + 1):
        row = exact_cycles(n)
        exact.append(row)
        print({key: row[key] for key in ("n", "enumerated_states", "number_of_nonuniform_cycles", "all_cycles_have_two", "all_cycle_supports_gap_free")}, flush=True)
    tested = [samples(n, args.samples_per_size, args.step_limit) for n in range(7, 21)]
    result = {"definition_version": "009-0.1", "date": "2026-10-24", "exact_cycles": exact,
              "seed": "20261024+n", "sample_cases_per_size": args.samples_per_size,
              "step_limit": args.step_limit, "sampled_orbits": tested,
              "scope": "Exact cycle classification only through the stated ring size, using the proved cycle bound; larger sizes use finite seeded orbit tests."}
    Path(__file__).with_name("experiment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("sample outcomes:", {kind: sum(row["outcomes"][kind] for row in tested) for kind in ("uniform", "periodic", "step_limit")})
    print("sample counterexamples:", sum(len(row["counterexamples"]) for row in tested))


if __name__ == "__main__":
    main()
