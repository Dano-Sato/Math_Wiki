"""Codex review: independent exact integer solver and all-real rank certificates."""

import json
from collections import Counter
from itertools import combinations_with_replacement, permutations
from pathlib import Path
from random import Random


def cost(order):
    n = len(order)
    extended = list(order) * 2
    prefix = [0]
    for value in extended:
        prefix.append(prefix[-1] + value)
    return max((max(prefix[i+k]-prefix[i] for i in range(n)) -
                min(prefix[i+k]-prefix[i] for i in range(n))
                for k in range(1, n//2+1)), default=0)


def literal_cost(order):
    n = len(order)
    return max((max(sum(order[(i+j) % n] for j in range(k)) for i in range(n)) -
                min(sum(order[(i+j) % n] for j in range(k)) for i in range(n))
                for k in range(1, n)), default=0)


def feasible(values, bound, budget=100000):
    """Prune by sums of completed linear arcs AND their circular complements."""
    n, total = len(values), sum(values)
    if max(values)-min(values) > bound:
        return {"status": "infeasible", "nodes": 0}
    counts = Counter(values)
    keys = sorted(counts)
    first = keys[0]
    counts[first] -= 1
    path = [first]
    prefix = [0, first]
    h = n//2
    nodes, cutoff = 0, False

    def add_arcs(lo, hi):
        low, high = list(lo), list(hi)
        m = len(path)
        for length in range(1, min(m, n-1)+1):
            arc = prefix[m]-prefix[m-length]
            facts = []
            if length <= h:
                facts.append((length, arc))
            if n-length <= h:
                facts.append((n-length, total-arc))
            for k, value in facts:
                low[k] = value if low[k] is None else min(low[k], value)
                high[k] = value if high[k] is None else max(high[k], value)
                if high[k]-low[k] > bound:
                    return None
        return low, high

    def visit(lo, hi):
        nonlocal nodes, cutoff
        nodes += 1
        if nodes > budget:
            cutoff = True
            return None
        updated = add_arcs(lo, hi)
        if updated is None:
            return None
        if len(path) == n:
            if path[1] > path[-1]:
                return None
            assert cost(path) <= bound
            return path.copy()
        for value in keys:
            if not counts[value]:
                continue
            counts[value] -= 1
            path.append(value)
            prefix.append(prefix[-1]+value)
            result = visit(*updated)
            prefix.pop()
            path.pop()
            counts[value] += 1
            if result is not None:
                return result
            if cutoff:
                return None
        return None

    witness = visit([None]*(h+1), [None]*(h+1))
    if witness is not None:
        assert Counter(witness) == Counter(values)
        assert literal_cost(witness) <= bound
        return {"status": "feasible", "nodes": nodes, "witness": witness, "cost": cost(witness)}
    return {"status": "cutoff" if cutoff else "infeasible", "nodes": nodes}


def universal_certificate(rank):
    n = len(rank)
    rows = []
    for threshold in range(1, n):
        word = tuple(int(i >= threshold) for i in rank)
        assert literal_cost(word) <= 1
        rows.append({"threshold": threshold, "binary_word": word, "cost": cost(word)})
    return {"n": n, "rank_zero_based": rank, "threshold_checks": rows}


def convex_certificate(rank):
    n = len(rank)
    rows = []
    for m in range(1, n):
        ramp = [max(0, i-(n-1-m)) for i in range(n)]
        order = [ramp[i] for i in rank]
        assert literal_cost(order) <= m
        rows.append({"tail_length": m, "ramp": ramp, "cost": literal_cost(order), "width": m})
    return {"n": n, "rank_zero_based": rank, "ramp_checks": rows}


def no_universal_convex_rank_eight():
    checked = 0
    for tail in permutations(range(1,8)):
        if tail[0] > tail[-1]:
            continue
        rank = (0,)+tail
        checked += 1
        if all(cost(tuple(max(0,i-(7-m)) for i in rank)) <= m for m in range(1,8)):
            raise AssertionError("Unexpected universal convex order for n=8")
    assert checked == 2520
    return {"n":8, "circular_rank_orders_checked":checked, "universal_order_exists":False,
            "scope":"No single order works for every convex input; this does NOT refute adaptive arrangements in 003-1."}


def main():
    rng = Random(20261024)
    certificates = [universal_certificate(rank) for rank in (
        (0,1), (0,1,2), (0,2,1,3), (0,2,3,1,4), (0,3,5,1,4,2,6))]
    convex_nine = convex_certificate((0,3,6,2,7,4,5,1,8))
    universal_eight = no_universal_convex_rank_eight()
    sharp_values = [0,0,1,2,2,2]
    sharp = {str(bound): feasible(sharp_values, bound) for bound in (2,3)}
    assert sharp['2']['status'] == 'infeasible' and sharp['3']['status'] == 'feasible'
    comparisons = []
    for n in range(3,9):
        for _ in range(8):
            values = sorted([0,4]+[rng.randrange(5) for _ in range(n-2)])
            optimum = min(literal_cost((values[0],)+tail) for tail in set(permutations(values[1:])))
            for bound in (optimum-1, optimum):
                result = feasible(values, bound)
                assert result['status'] == ('feasible' if bound >= optimum else 'infeasible')
            comparisons.append({"values": values, "literal_optimum": optimum})
    grids = []
    for n in (10,12,14):
        counts = {"feasible":0, "infeasible":0, "cutoff":0}
        exceptions = []
        max_nodes = 0
        for middle in combinations_with_replacement(range(5), n-2):
            values = sorted([0,4,*middle])
            result = feasible(values, 6)
            counts[result['status']] += 1
            max_nodes = max(max_nodes, result['nodes'])
            if result['status'] != 'feasible':
                exceptions.append({"values": values, **result})
        grids.append({"n":n, "grid_denominator":4, "counts":counts,
                      "maximum_nodes": max_nodes, "exceptions": exceptions})
        print('grid',n,counts,flush=True)
    convex = []
    for n in range(6,13):
        counts = {"feasible":0, "infeasible":0, "cutoff":0}
        exceptions = []
        for _ in range(20):
            gaps = sorted(rng.randrange(13) for _ in range(n-1))
            if not any(gaps):
                gaps[-1] = 1
            values = [0]
            for gap in gaps:
                values.append(values[-1]+gap)
            result = feasible(values, values[-1])
            counts[result['status']] += 1
            if result['status'] != 'feasible':
                exceptions.append({"values":values, **result})
        convex.append({"n":n, "counts":counts, "exceptions":exceptions})
        print('convex',n,counts,flush=True)
    original = json.loads(Path(__file__).with_name('experiment.json').read_text())
    original_checked = 0
    for row in original['rows']:
        if row.get('found'):
            witness = row['witness']
            assert Counter(witness) == Counter(row['values'])
            assert literal_cost(witness) <= row['bound_max_minus_min']
            original_checked += 1
    output = {"reviewer":"Codex / ChatGPT", "date":"2026-10-24",
              "universal_rank_certificates":certificates, "sharp_example":sharp,
              "universal_convex_nine":convex_nine, "no_universal_convex_eight":universal_eight,
              "literal_comparisons":comparisons, "grid_checks":grids,
              "convex_checks":convex, "original_witnesses_rechecked":original_checked,
              "scope":"Finite integer tests and exact rank certificates. Grid checks do not prove the bound for all reals or all n. Cutoffs are unresolved."}
    Path(__file__).with_name('review_2026-10-24.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
