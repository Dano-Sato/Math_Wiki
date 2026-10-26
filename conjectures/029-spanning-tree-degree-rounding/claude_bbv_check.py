"""029 test on Bauer-Broersma-Veldman graphs G(L,u,v,l,m): m copies of L, clique on all u_i,v_i, join with K_l."""
import sys, time, math, itertools
sys.path.insert(0, __import__("os").path.dirname(__file__))
import networkx as nx, numpy as np
from claude_ust_lib import mu, window_tree

def L_graph():
    G = nx.Graph()
    G.add_edges_from([("a","b"),("b","c"),("c","d"),("d","a"),("t","a"),("t","b"),("w","d"),("w","c"),
                      ("u","a"),("u","d"),("v","b"),("v","c")])
    return G

def bbv(l, m, H=None, x="u", y="v"):
    H = H or L_graph()
    G = nx.Graph(); ends = []
    for i in range(m):
        G.add_edges_from(((i, p), (i, q)) for p, q in H.edges())
        ends += [(i, x), (i, y)]
    G.add_edges_from(itertools.combinations(ends, 2))
    T = [("T", j) for j in range(l)]
    G.add_edges_from(itertools.combinations(T, 2))
    G.add_edges_from((t, w) for t in T for w in list(G.nodes) if w not in T and w[0] != "T")
    return nx.convert_node_labels_to_integers(G, label_attribute="orig")

def no_uv_ham_path(H, x, y):
    n = H.number_of_nodes()
    for p in itertools.permutations([w for w in H if w not in (x, y)]):
        path = (x,) + p + (y,)
        if all(H.has_edge(path[i], path[i+1]) for i in range(n - 1)):
            return False
    return True

print("L has no Hamilton u-v path:", no_uv_ham_path(L_graph(), "u", "v"))
for l in [1, 2, 3, 4, 6]:
    m = 2 * l + 3
    G = bbv(l, m); n = G.number_of_nodes()
    tough = (l + 4 * m) / (2 * m + 1)
    t0 = time.time()
    ham = window_tree(G, {v: 1.5 for v in G})  # windows {1,2} everywhere = Hamilton path
    mm = mu(G); vals = np.array(list(mm.values()))
    cls = {}
    for v, d in G.nodes(data=True):
        o = d["orig"]; k = "T" if o[0] == "T" else o[1]
        cls.setdefault(k, []).append(mm[v])
    summary = {k: round(float(np.mean(v)), 3) for k, v in sorted(cls.items())}
    below2 = int((vals < 2).sum())
    res = window_tree(G, mm)
    print(f"l={l} m={m} n={n} toughness={tough:.3f} hamilton-path-MILP={ham} | mean mu by role {summary} | #mu<2={below2}/{n} | 029 window tree: {res} ({time.time()-t0:.1f}s)", flush=True)
