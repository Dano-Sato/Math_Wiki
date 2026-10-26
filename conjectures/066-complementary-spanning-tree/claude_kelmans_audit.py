"""066 Claude 검산: CST(n<=7 전수), Tree-CST(n<=14 전수), Kelmans 변환과 보수의 교환성.

모든 신장나무 수는 축소 라플라시안의 정확한 정수 행렬식(Bareiss)으로 계산한다.
실행: python conjectures/066-complementary-spanning-tree/claude_kelmans_audit.py
결과: 같은 폴더의 claude_kelmans_audit.json
"""
import json
import random
from pathlib import Path

import networkx as nx
import sympy as sp
from networkx.generators.atlas import graph_atlas_g


def tau(G):
    if G.number_of_nodes() == 1:
        return 1
    if not nx.is_connected(G):
        return 0
    L = sp.Matrix(nx.laplacian_matrix(G, nodelist=sorted(G)).toarray().tolist())
    return int(L[1:, 1:].det(method="bareiss"))


def bound(n):
    return (n - 3) * (n - 1) ** (n - 4)


def kelmans(G, u, v):
    """v의 이웃 중 u와 인접하지 않은 것(u 제외)을 u로 옮긴다."""
    H = G.copy()
    for w in list(G[v]):
        if w != u and not G.has_edge(u, w):
            H.remove_edge(v, w)
            H.add_edge(u, w)
    return H


def g6(G):
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def sq(G):
    return sum(d * d for _, d in G.degree())


def both_connected(G):
    return nx.is_connected(G) and nx.is_connected(nx.complement(G))


def main():
    out = {"cst": {}, "tree_cst": {}, "kelmans_complement": {}, "kelmans_terminal": {}}

    for n in range(4, 8):
        graphs = [G for G in graph_atlas_g() if G.number_of_nodes() == n and both_connected(G)]
        prods = [(tau(G) * tau(nx.complement(G)), G) for G in graphs]
        m = min(p for p, _ in prods)
        out["cst"][n] = {
            "pairs": len(graphs),
            "min": m,
            "bound": bound(n),
            "violations": [g6(G) for p, G in prods if p < bound(n)],
            "equality_graph6": [g6(G) for p, G in prods if p == bound(n)],
        }
        # 강한 Σd² 증가 Kelmans 단계를 하면 양쪽 연결이 깨지는 종착 그래프
        term = []
        for p, G in prods:
            ok = any(
                sq(K) > sq(G) and both_connected(K)
                for u in G for v in G if u != v
                for K in [kelmans(G, u, v)]
            )
            if not ok:
                term.append({"graph6": g6(G), "edges": G.number_of_edges(), "product": p})
        out["kelmans_terminal"][n] = {"count": len(term), "min_product": min(t["product"] for t in term), "graphs": term}

    for n in range(5, 15):
        vals = []
        for T in nx.nonisomorphic_trees(n):
            if max(d for _, d in T.degree()) == n - 1:
                continue
            vals.append((tau(nx.complement(T)), sorted((d for _, d in T.degree()), reverse=True)))
        m = min(v for v, _ in vals)
        out["tree_cst"][n] = {
            "nonstar_trees": len(vals),
            "min": m,
            "bound": bound(n),
            "argmin_degree_sequences": [d for v, d in vals if v == m],
            "second_value": sorted({v for v, _ in vals})[1],
        }

    rng = random.Random(1)
    trials = iso = mono = 0
    for _ in range(400):
        n = rng.randint(5, 8)
        G = nx.gnp_random_graph(n, rng.random(), seed=rng.randrange(10**9))
        u, v = rng.sample(range(n), 2)
        K, C = kelmans(G, u, v), nx.complement(G)
        trials += 1
        iso += nx.is_isomorphic(nx.complement(K), kelmans(C, v, u))
        mono += tau(K) <= tau(G) and tau(nx.complement(K)) <= tau(C)
    out["kelmans_complement"] = {"seed": 1, "trials": trials, "complement_isomorphic": iso, "both_tau_nonincreasing": mono}

    path = Path(__file__).with_name("claude_kelmans_audit.json")
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "kelmans_terminal"}, ensure_ascii=False)[:2000])
    print({n: (d["count"], d["min_product"]) for n, d in out["kelmans_terminal"].items()})


if __name__ == "__main__":
    main()
