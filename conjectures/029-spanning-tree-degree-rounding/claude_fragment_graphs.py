"""Claude review: non-traceable cubic graphs from Petersen-minus-vertex fragments
substituted into K4 (all 4 or 3 of 4 vertices). >=3 fragments forbid a Hamilton path."""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
import networkx as nx
from claude_search import check, floor_ceil
def substituted(H, replace):
    P = nx.petersen_graph()
    G = nx.Graph(); att = {}
    for w in H:
        if w in replace:
            F = nx.relabel_nodes(P, {x: (w, x) for x in P}); v = (w, 0)
            nbrs = list(F[v]); F.remove_node(v); G.add_edges_from(F.edges())
            att[w] = nbrs
        else:
            G.add_node(w)
    used = {w: 0 for w in H}
    for a, b in H.edges():
        pa = att[a][used[a]] if a in att else a; used[a] += 1
        pb = att[b][used[b]] if b in att else b; used[b] += 1
        G.add_edge(pa, pb)
    return nx.convert_node_labels_to_integers(G)
for name, H, rep in [("K4 all 4", nx.complete_graph(4), {0,1,2,3}),
                     ("K4 3 of 4", nx.complete_graph(4), {0,1,2})]:
    G = substituted(H, rep)
    res, nodes, mu, tau = check(G, node_limit=20_000_000)
    mx = max(mu)
    windows = sorted(set(floor_ceil(x) for x in mu))
    print(name, G.number_of_nodes(), "cubic", all(d == 3 for _, d in G.degree()),
          "max mu", float(mx), "windows", windows,
          "#mu>2", sum(x > 2 for x in mu), "result", res if res in (None, "timeout") else "tree found")
