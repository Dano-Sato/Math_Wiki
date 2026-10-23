"""Claude review search for 029: exact UST mean degrees and a degree-window
spanning-tree solver for graphs beyond full tree enumeration (n = 8..14).

mu_v = sum_{u~v} R(u,v), with R(u,v) = det L[{u,v}^c] / det L[{w}^c]
computed exactly with fraction-free Bareiss determinants.
"""

from fractions import Fraction
import json
import random
import sys
from pathlib import Path

import networkx as nx


def bareiss_det(M):
    M = [row[:] for row in M]
    n = len(M)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def mean_degrees(G):
    nodes = list(G)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    L = [[0] * n for _ in range(n)]
    for u, v in G.edges():
        a, b = idx[u], idx[v]
        L[a][a] += 1
        L[b][b] += 1
        L[a][b] -= 1
        L[b][a] -= 1
    tau = bareiss_det([r[1:] for r in L[1:]])
    mu = [Fraction(0)] * n
    for u, v in G.edges():
        a, b = idx[u], idx[v]
        keep = [i for i in range(n) if i not in (a, b)]
        r = Fraction(bareiss_det([[L[i][j] for j in keep] for i in keep]), tau)
        mu[a] += r
        mu[b] += r
    return nodes, mu, tau


def floor_ceil(x):
    f = x.numerator // x.denominator
    return f, (f if x.denominator == 1 else f + 1)


def find_tree(G, lo, hi, node_limit=5_000_000):
    """Backtracking search for a spanning tree with lo[v] <= deg <= hi[v].
    Returns edge list, None (proved none), or 'timeout'."""
    nodes = list(G)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    # order edges: vertices with tight windows first
    edges = sorted(((idx[u], idx[v]) for u, v in G.edges()),
                   key=lambda e: (hi[e[0]] + hi[e[1]], e))
    m = len(edges)
    deg = [0] * n
    avail = [0] * n
    for a, b in edges:
        avail[a] += 1
        avail[b] += 1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    chosen = []
    count = [0]

    def rec(k, ntree):
        count[0] += 1
        if count[0] > node_limit:
            raise TimeoutError
        if ntree == n - 1:
            return all(deg[v] >= lo[v] for v in range(n))
        if k == m or m - k < n - 1 - ntree:
            return False
        a, b = edges[k]
        ra, rb = find(a), find(b)
        # include
        if ra != rb and deg[a] < hi[a] and deg[b] < hi[b]:
            parent[ra] = rb
            deg[a] += 1; deg[b] += 1
            avail[a] -= 1; avail[b] -= 1
            chosen.append(edges[k])
            if rec(k + 1, ntree + 1):
                return True
            chosen.pop()
            avail[a] += 1; avail[b] += 1
            deg[a] -= 1; deg[b] -= 1
            parent[ra] = ra
        # exclude
        avail[a] -= 1; avail[b] -= 1
        ok = deg[a] + avail[a] >= lo[a] and deg[b] + avail[b] >= lo[b]
        res = ok and rec(k + 1, ntree)
        avail[a] += 1; avail[b] += 1
        return res

    try:
        if rec(0, 0):
            return [(nodes[a], nodes[b]) for a, b in chosen]
        return None
    except TimeoutError:
        return "timeout"


def check(G, node_limit=5_000_000):
    nodes, mu, tau = mean_degrees(G)
    lo, hi = zip(*(floor_ceil(x) for x in mu))
    res = find_tree(G, lo, hi, node_limit)
    return res, nodes, mu, tau


def is_traceable(G):
    nodes = list(G)
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [0] * n
    for u, v in G.edges():
        adj[idx[u]] |= 1 << idx[v]
        adj[idx[v]] |= 1 << idx[u]
    reach = [0] * (1 << n)  # bitmask of possible endpoints
    for i in range(n):
        reach[1 << i] = 1 << i
    full = (1 << n) - 1
    for S in range(1, 1 << n):
        e = reach[S]
        if not e:
            continue
        if S == full:
            return True
        x = e
        while x:
            low = x & -x
            i = low.bit_length() - 1
            x ^= low
            nb = adj[i] & ~S
            while nb:
                lb = nb & -nb
                reach[S | lb] |= lb
                nb ^= lb
    return reach[full] != 0


def families(rng):
    out = []
    for n in range(8, 15):
        for d in (3, 4, 5):
            if n * d % 2 == 0 and d < n:
                for _ in range(15):
                    out.append((f"random_{d}reg_n{n}", nx.random_regular_graph(d, n, seed=rng.randrange(10**9))))
    for n, k in [(5, 2), (6, 2), (7, 2), (7, 3), (8, 3), (9, 2), (9, 4), (10, 3)]:
        out.append((f"GP({n},{k})", nx.generalized_petersen_graph(n, k) if hasattr(nx, "generalized_petersen_graph") else nx.petersen_graph()))
    out.append(("petersen", nx.petersen_graph()))
    out.append(("line_petersen", nx.line_graph(nx.petersen_graph())))
    for a, b in [(2, 5), (3, 6), (3, 7), (4, 8), (2, 9), (4, 9)]:
        out.append((f"K{a},{b}", nx.complete_bipartite_graph(a, b)))
    for g in ("frucht_graph", "heawood_graph", "tutte_graph", "dodecahedral_graph",
              "desargues_graph", "moebius_kantor_graph", "pappus_graph",
              "truncated_tetrahedron_graph", "truncated_cube_graph", "icosahedral_graph",
              "chvatal_graph", "sedgewick_maze_graph", "octahedral_graph", "cubical_graph"):
        out.append((g, getattr(nx, g)()))
    # random sparse 2-connected-ish graphs with near-uniform mean degree
    for n in range(9, 13):
        for _ in range(150):
            p = rng.choice([0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
            G = nx.gnp_random_graph(n, p, seed=rng.randrange(10**9))
            if nx.is_connected(G):
                out.append((f"gnp_n{n}_p{p}", G))
    return out


def main():
    rng = random.Random(29029)
    report = {"checked": 0, "timeouts": [], "counterexamples": [],
              "maxmu_le2_nontraceable": [], "by_family": {}}
    for name, G in families(rng):
        G = nx.convert_node_labels_to_integers(G)
        res, nodes, mu, tau = check(G)
        report["checked"] += 1
        fam = name.split("_n")[0] if name.startswith(("random", "gnp")) else name
        report["by_family"][fam] = report["by_family"].get(fam, 0) + 1
        if res == "timeout":
            report["timeouts"].append(name)
        elif res is None:
            report["counterexamples"].append({"name": name, "edges": list(G.edges()),
                                              "mu": [str(x) for x in mu]})
            print("COUNTEREXAMPLE", name, list(G.edges()), flush=True)
        if max(mu) <= 2 and G.number_of_nodes() <= 14 and not is_traceable(G):
            report["maxmu_le2_nontraceable"].append(name)
    print(json.dumps({k: v for k, v in report.items()}, indent=1))
    Path(__file__).with_name("claude_search.json").write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
