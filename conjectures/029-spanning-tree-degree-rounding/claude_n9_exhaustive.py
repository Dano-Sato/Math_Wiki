"""Claude review: exhaustive 029 check for connected 9-vertex graphs.
Connected 8-vertex classes are built from atlas n=7 by one-vertex extension
and deduplicated by exact isomorphism (WL-hash buckets); each class is then
extended by a vertex with every nonempty neighbourhood (covers all classes
of connected 9-vertex graphs, with repeats).
"""
import json
from pathlib import Path
import networkx as nx
from claude_search import check

base7 = [g for g in nx.graph_atlas_g() if g.number_of_nodes() == 7 and nx.is_connected(g)]
buckets = {}
classes8 = []
for g in base7:
    for mask in range(1, 128):
        G = g.copy()
        G.add_edges_from((7, i) for i in range(7) if mask >> i & 1)
        h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
        if any(nx.is_isomorphic(G, H) for H in buckets.get(h, [])):
            continue
        buckets.setdefault(h, []).append(G)
        classes8.append(G)
print("connected 8-vertex classes:", len(classes8), flush=True)
checked = timeouts = 0
bad = []
for G0 in classes8:
    for mask in range(1, 256):
        G = G0.copy()
        G.add_edges_from((8, i) for i in range(8) if mask >> i & 1)
        res = check(G)[0]
        checked += 1
        if res is None:
            bad.append(list(G.edges())); print("COUNTEREXAMPLE", list(G.edges()), flush=True)
        elif res == "timeout":
            timeouts += 1
out = {"connected_8_classes": len(classes8), "extensions_checked": checked,
       "timeouts": timeouts, "counterexamples": bad}
print(out)
Path(__file__).with_name("claude_n9_exhaustive.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
