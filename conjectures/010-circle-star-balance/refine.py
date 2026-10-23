"""Recover unresolved heuristic cases using binary MILP and local refinement.

Requires numpy and scipy. A solver timeout is unresolved, never a counterexample.
Every successful output is checked separately by verify.py without dependencies.
"""

import json
from math import ceil, floor
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

ROOT = Path(__file__).resolve().parent


def binary_witness(n, m):
    if m > n//2:
        return [1-x for x in binary_witness(n, n-m)]
    # If the minority count divides n, equally spaced letters are balanced in
    # both readings because n/m is odd.
    if n % m == 0:
        return [int(i % (n//m) == 0) for i in range(n)]
    profiles = [(d,k) for d in (1,2) for k in range(2,n//2+1)]
    rr, cc, vv = [0]*n, list(range(n)), [1]*n
    lows, highs = [m], [m]
    for j,(d,k) in enumerate(profiles):
        for i in range(n):
            row = len(lows)
            lows.append(0)
            highs.append(2)
            for t in range(k):
                rr.append(row); cc.append((i+d*t) % n); vv.append(1)
            rr.append(row); cc.append(n+j); vv.append(-1)
    size = n+len(profiles)
    matrix = coo_matrix((vv,(rr,cc)),shape=(len(lows),size)).tocsc()
    lower = np.array([0]*n+[ceil(k*m/n)-2 for d,k in profiles], dtype=float)
    upper = np.array([1]*n+[floor(k*m/n) for d,k in profiles], dtype=float)
    lower[0] = 1  # rotation symmetry
    result = milp(np.zeros(size), integrality=np.ones(size),
                  bounds=Bounds(lower,upper), constraints=LinearConstraint(matrix,lows,highs),
                  options={'time_limit': 10})
    if result.x is None:
        raise RuntimeError(f'Unresolved MILP n={n}, m={m}: {result.message}')
    word = [int(round(x)) for x in result.x[:n]]
    assert sum(word) == m
    return word


def refine(values, word, rng):
    values = np.array(values, dtype=np.int64)
    n = len(values)
    midpoint = (min(values)+max(values))/2
    low, high = values[values <= midpoint], values[values > midpoint]
    assert len(high) == sum(word)
    a = np.zeros(n, dtype=np.int64)
    indices = np.array([[(d*i) % n for i in range(n)] for d in (1,2)])
    starts = np.arange(n)[None,None,:]
    ends = starts+np.arange(1,n//2+1)[None,:,None]
    width = int(max(values)-min(values))
    target = 2*width

    def measure(a):
        b = a[indices]
        p = np.concatenate([np.zeros((2,1),dtype=np.int64),np.cumsum(np.tile(b,(1,2)),axis=1)],axis=1)
        sums = p[np.arange(2)[:,None,None],ends]-p[np.arange(2)[:,None,None],starts]
        lo, hi = sums.min(axis=2,keepdims=True), sums.max(axis=2,keepdims=True)
        penalty_low = np.square(np.maximum(sums-lo-target,0)).sum(axis=2)
        penalty_high = np.square(np.maximum(hi-sums-target,0)).sum(axis=2)
        energy = float(np.minimum(penalty_low,penalty_high).sum())/(width*width)
        return energy, int((hi-lo).max())

    evaluations = 0
    best = None
    for restart in range(4):
        a[np.array(word) == 0] = rng.permutation(low)
        a[np.array(word) == 1] = rng.permutation(high)
        current, value = measure(a)
        evaluations += 1
        if best is None or value < best[0]:
            best = (value,a.copy())
        if value <= target:
            break
        for t in range(10000):
            i,j = rng.integers(0,n,2)
            if word[i] != word[j]:
                continue
            a[i],a[j] = a[j],a[i]
            candidate,value = measure(a)
            evaluations += 1
            temperature = 0.002*(1-t/10000)+0.0000001
            if candidate <= current or rng.random() < np.exp((current-candidate)/temperature):
                current = candidate
                if value < best[0]:
                    best = (value,a.copy())
                if value <= target:
                    break
            else:
                a[i],a[j] = a[j],a[i]
        if best[0] <= target:
            break
    return {'cost': best[0], 'witness': best[1].tolist(), 'evaluations': evaluations}


def run():
    original = json.loads((ROOT/'experiment.json').read_text(encoding='utf-8'))
    rng = np.random.default_rng(20261024)
    memo, rows, unresolved = {}, [], []
    for index in original['rows_over_bound']:
        row = original['rows'][index]
        values = row['values']
        midpoint = (min(values)+max(values))/2
        high_count = sum(v > midpoint for v in values)
        key = (row['n'],high_count)
        try:
            if key not in memo:
                memo[key] = binary_witness(*key)
            recovered = refine(values,memo[key],rng)
            recovered.update({'original_index': index, 'n': row['n'], 'width': row['width']})
            rows.append(recovered)
            if recovered['cost'] > 2*row['width']:
                unresolved.append(index)
            print(index, row['n'], recovered['cost'], 'bound', 2*row['width'], flush=True)
        except RuntimeError as error:
            unresolved.append(index)
            print(str(error),flush=True)
    report = {'definition_version': '010-0.1', 'date': '2026-10-24',
              'seed': 20261024, 'method': 'binary MILP followed by within-cluster swaps',
              'rows': rows, 'unresolved_indices': unresolved}
    (ROOT/'refinement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    run()
