"""Independent checks for the incremental 006 review; standard library only."""

import importlib.util
import json
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def prime_by_division(value):
    return value >= 2 and all(value % d for d in range(2, isqrt(value) + 1))


def run():
    report = json.loads((ROOT / 'review_incremental.json').read_text(encoding='utf-8'))
    rows = report['rows']
    maximum_n = len(rows)
    assert [r['n'] for r in rows] == list(range(1, maximum_n + 1))
    prime = bytearray(b'\1') * (4 * maximum_n + 1)
    prime[:2] = b'\0\0'
    for p in range(2, isqrt(len(prime) - 1) + 1):
        if prime[p]:
            for multiple in range(p*p, len(prime), p):
                prime[multiple] = 0
    # Dynamic programming on paths, independent of the Go greedy matching.
    dp = [0] * (2 * maximum_n + 1)
    last = [0, 0, 0]
    for x in range(1, len(dp)):
        if x % 3:
            dp[x] = dp[x-3] if x > 3 else 0
            if x > 3 and prime[2*x-3]:
                dp[x] = max(dp[x], 1 + (dp[x-6] if x > 6 else 0))
            last[x % 3] = dp[x]
        if x % 2 == 0:
            row = rows[x//2-1]
            assert row['kappa'] == last[1] + last[2]
            assert row['predicted'] == min(x//2, x//3 + row['kappa'])
    failures = [r['n'] for r in rows if r['maximum'] != r['predicted']]
    assert failures == report['failed_sizes'] == [2, 3]
    witness_pairs = 0
    for key, pairs in report['witnesses'].items():
        n = int(key)
        vertices = [x for pair in pairs for x in pair]
        assert len(vertices) == len(set(vertices))
        assert all(1 <= x <= 2*n for x in vertices)
        assert len(pairs) == rows[n-1]['maximum']
        assert all(prime_by_division(x+y) and prime_by_division(abs(x-y)) for x,y in pairs)
        witness_pairs += len(pairs)
    old = json.loads((ROOT / 'bottleneck_experiment.json').read_text(encoding='utf-8'))
    for row in old['rows']:
        new = rows[row['n']-1]
        assert new['maximum'] == row['found_pairs'] and new['kappa'] == row['kappa']
    spec = importlib.util.spec_from_file_location('original_006', ROOT / 'bottleneck_verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cross_checks = []
    for n in [101, 137, 503, 1009, 3001]:
        pairs = module.maximum_matching(n, prime)
        assert len(pairs) == rows[n-1]['maximum']
        cross_checks.append({'n': n, 'maximum': len(pairs)})
    # The first obstruction to fixing an arbitrary maximum internal matching.
    greedy = module.internal_matching(4, prime)
    assert greedy == [[1, 4], [2, 5]]
    assert [y for y in range(1, 9) if prime[6+y] and prime[abs(6-y)]] == [1]
    # A permutation avoiding b = +/-a mod q for each individual q >= 5.
    local_checks = []
    for q in range(5, 102):
        if not prime[q]:
            continue
        inverse_two = (q+1)//2
        image = [1 if a == 0 else 0 if a == inverse_two else 2*a % q for a in range(q)]
        assert sorted(image) == list(range(q))
        assert all((b-a) % q and (b+a) % q for a,b in enumerate(image))
        local_checks.append(q)
    result = {'date': '2026-10-24', 'definition_version': '006-0.1',
              'all_sizes': [4, maximum_n], 'all_sizes_count': maximum_n-3,
              'failed_sizes_including_out_of_domain': failures,
              'independent_kappa_dp_sizes': maximum_n,
              'previous_rows_agree': len(old['rows']),
              'saved_witnesses_checked': len(report['witnesses']),
              'saved_pairs_trial_division_checked': witness_pairs,
              'static_algorithm_cross_checks': cross_checks,
              'greedy_internal_counterexample': {'n': 4, 'pairs': greedy, 'blocked_vertex': 6},
              'single_prime_residue_bijections_checked': local_checks}
    (ROOT / 'review_2026-10-24.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    run()
