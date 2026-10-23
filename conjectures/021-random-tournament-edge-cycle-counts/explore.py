"""Exact edge-by-edge Hamilton-cycle counts in seeded random tournaments."""
import json
import math
import random
import statistics
from pathlib import Path


SEED = 20261024
SAMPLES = 30
SIZES = list(range(4, 13))


def endpoint_path_counts(out):
    """Return counts indexed by fixed start and end vertices."""
    n = len(out)
    size = 1 << n
    result = [[0] * n for _ in range(n)]
    for start in range(n):
        dp = [[0] * n for _ in range(size)]
        dp[1 << start][start] = 1
        for mask in range(size):
            if not (mask >> start & 1):
                continue
            for last, count in enumerate(dp[mask]):
                if not count:
                    continue
                remaining = out[last] & ~mask
                while remaining:
                    bit = remaining & -remaining
                    nxt = bit.bit_length() - 1
                    dp[mask | bit][nxt] += count
                    remaining -= bit
        result[start] = dp[-1]
    return result


def random_out_masks(n, rng):
    out = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if rng.getrandbits(1):
                out[i] |= 1 << j
            else:
                out[j] |= 1 << i
    return out


def fixed_arc_second_moment(n):
    """Exact E[(C_e/mu_n)^2] by weighted permutations with endpoints fixed."""
    m = n - 2
    size = 1 << m
    dp = [[0] * m for _ in range(size)]
    for first in range(m):
        dp[1 << first][first] = 2 if first == 0 else 1
    for mask in range(size):
        for last, weight in enumerate(dp[mask]):
            if not weight:
                continue
            remaining = (size - 1) ^ mask
            while remaining:
                bit = remaining & -remaining
                nxt = bit.bit_length() - 1
                # A reversed shared internal edge makes the two paths incompatible.
                if nxt != last - 1:
                    factor = 2 if nxt == last + 1 else 1
                    dp[mask | bit][nxt] += weight * factor
                remaining -= bit
    weighted_pairs = sum(dp[-1][last] * (2 if last == m - 1 else 1)
                         for last in range(m))
    return weighted_pairs / math.factorial(m) - 1


def main():
    rng = random.Random(SEED)
    result = {
        "seed": SEED,
        "samples_per_n": SAMPLES,
        "method": "independent fair tournaments; exact subset DP counts every ordered-endpoint Hamilton path",
        "cycle_edge_mapping": "cycles through arc u->v correspond to paths starting at v and ending at u",
        "conditional_mean": "(n-2)! / 2^(n-1) for each present arc",
        "fixed_arc_second_moment_method": "exact weighted-permutation DP; reports Var(C_e/mu_n) conditional on a fixed arc",
        "fixed_arc_variance_rows": [
            {"n": n, "variance": fixed_arc_second_moment(n),
             "n_times_variance": n * fixed_arc_second_moment(n)}
            for n in range(3, 19)
        ],
        "rows": [],
    }
    for n in SIZES:
        expected = math.factorial(n - 2) / 2 ** (n - 1)
        tournament_maxima = []
        tournament_rms = []
        all_ratios = []
        for _ in range(SAMPLES):
            out = random_out_masks(n, rng)
            paths = endpoint_path_counts(out)
            ratios = []
            for i in range(n):
                for j in range(i + 1, n):
                    # The unique arc closes the Hamilton path in the reverse direction.
                    count = paths[j][i] if (out[i] >> j & 1) else paths[i][j]
                    ratios.append(count / expected)
            all_ratios.extend(ratios)
            tournament_maxima.append(max(abs(x - 1) for x in ratios))
            tournament_rms.append(math.sqrt(sum((x - 1) ** 2 for x in ratios) / len(ratios)))
        ordered_maxima = sorted(tournament_maxima)
        result["rows"].append({
            "n": n,
            "arcs_per_tournament": n * (n - 1) // 2,
            "mean_max_abs_relative_error": statistics.mean(tournament_maxima),
            "q90_max_abs_relative_error": ordered_maxima[int((SAMPLES - 1) * 0.90)],
            "worst_max_abs_relative_error": max(tournament_maxima),
            "mean_rms_relative_error": statistics.mean(tournament_rms),
            "pooled_arc_ratio_mean": statistics.mean(all_ratios),
            "pooled_arc_ratio_sd": statistics.pstdev(all_ratios),
        })
    target = Path(__file__).with_name("experiment.json")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
