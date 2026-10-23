"""Claude review: every connected simple graph on 8 vertices has a non-cut
vertex, so it arises from a connected 7-vertex atlas graph by adding one
vertex adjacent to a nonempty subset. Checking all 853 * 127 extensions
covers every isomorphism class of connected 8-vertex graphs (with repeats).
"""
import json
from pathlib import Path
import networkx as nx
from claude_search import check

base = [g for g in nx.graph_atlas_g() if g.number_of_nodes() == 7 and nx.is_connected(g)]
checked = timeouts = 0
bad = []
for g in base:
    for mask in range(1, 128):
        G = g.copy()
        G.add_edges_from((7, i) for i in range(7) if mask >> i & 1)
        res = check(G)[0]
        checked += 1
        if res is None:
            bad.append(list(G.edges())); print("COUNTEREXAMPLE", list(G.edges()), flush=True)
        elif res == "timeout":
            timeouts += 1
out = {"base_graphs": len(base), "extensions_checked": checked,
       "timeouts": timeouts, "counterexamples": bad}
print(out)
Path(__file__).with_name("claude_n8_exhaustive.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
