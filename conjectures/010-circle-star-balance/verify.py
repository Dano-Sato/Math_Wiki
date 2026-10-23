"""Independent certificate checks for 010; Python standard library only."""

import json
from collections import Counter
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def cost(order):
    """Literal definition, all lengths including those above n/2."""
    n = len(order)
    result = 0
    for d in (1,2):
        for k in range(1,n):
            sums = [sum(order[(i+d*j) % n] for j in range(k)) for i in range(n)]
            result = max(result,max(sums)-min(sums))
    return result


def exact_value(values):
    # Fix one occurrence of the minimum by rotation. Do not remove reflections.
    first = min(values)
    rest = values.copy()
    rest.remove(first)
    return min(cost((first,*tail)) for tail in set(permutations(rest)))


def run():
    experiment = json.loads((ROOT/'experiment.json').read_text(encoding='utf-8'))
    refinement = json.loads((ROOT/'refinement.json').read_text(encoding='utf-8'))
    ranks = json.loads((ROOT/'rank_certificates.json').read_text(encoding='utf-8'))
    replacements = {r['original_index']: r for r in refinement['rows']}
    assert not refinement['unresolved_indices']
    exact_checks = 0
    counts = Counter()
    for index,original in enumerate(experiment['rows']):
        row = replacements.get(index,original)
        witness, values = row['witness'], original['values']
        assert Counter(witness) == Counter(values)
        assert cost(witness) == row['cost'] <= 2*original['width']
        counts['exact_grid' if original['exact'] else 'additional_search'] += 1
        if original['exact'] and (original['n'] <= 5 or
                                 (original['n'] == 7 and exact_checks < 52)):
            assert exact_value(values) == original['cost']
            exact_checks += 1
    for cert in ranks['certificates']:
        n, order = cert['n'], cert['zero_based_ranks']
        assert sorted(order) == list(range(n))
        assert all(cost([int(rank > threshold) for rank in order]) <= 2
                   for threshold in range(n-1))
    # Binary equality criterion: independently enumerate every binary necklace
    # up to length eleven (complements omitted).
    binary_checks = []
    for n in range(3,12,2):
        for m in range(1,n//2+1):
            values = [0]*(n-m)+[1]*m
            found = exact_value(values)
            expected = 1 if n % m == 0 else 2
            assert found == expected
            binary_checks.append({'n':n,'minority':m,'optimum':found})
    result = {'date':'2026-10-24','definition_version':'010-0.1',
              'checked_witnesses':dict(counts),
              'initial_search_unresolved':len(experiment['rows_over_bound']),
              'refined_successes':len(replacements), 'remaining_unresolved':0,
              'independent_grid_optimum_checks':exact_checks,
              'universal_real_rank_certificates':[r['n'] for r in ranks['certificates']],
              'binary_exact_checks':binary_checks,
              'sharp_example':{'values':[0,0,1,1,1],'optimum':exact_value([0,0,1,1,1])}}
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))


if __name__ == '__main__':
    run()
