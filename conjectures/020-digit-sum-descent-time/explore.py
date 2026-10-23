"""Finite exact data for conjecture 020; standard library only."""

import json
import math
from pathlib import Path


MAX_N = 2_000_000
BASES = (2, 3, 4, 10)
SAMPLES = (100, 1_000, 10_000, 100_000, 1_000_000)


def digit_sum(n, base):
    total = 0
    while n:
        n, digit = divmod(n, base)
        total += digit
    return total


def build_table(base, max_n):
    tau = [0] * (max_n + 1)
    for n in range(base, max_n + 1):
        tau[n] = 1 + tau[n - digit_sum(n, base)]
    return tau


def main():
    results = {
        "definition": "tau_b(n)=min{t>=0:T_b^t(n)<b}, T_b(n)=n-s_b(n)",
        "predicted_limit_of_normalized_value": "2/(b-1)",
        "max_n": MAX_N,
        "bases": {},
    }
    for base in BASES:
        tau = build_table(base, MAX_N)
        checkpoints = sorted({n for n in SAMPLES if n <= MAX_N})
        checkpoints.extend(base**k for k in range(1, 64) if base**k <= MAX_N)
        checkpoints = sorted(set(checkpoints))
        results["bases"][str(base)] = [
            {
                "n": n,
                "tau": tau[n],
                "tau_log_base_n_over_n": tau[n] * math.log(n, base) / n,
            }
            for n in checkpoints
        ]
    output = Path(__file__).with_name("experiment.json")
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output.name}; bases={BASES}; max_n={MAX_N}")


if __name__ == "__main__":
    main()
