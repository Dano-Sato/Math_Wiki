"""Claude review: exhaustive check of 029 on subdivisions of small
2-connected base multigraphs (theta, K4, K_{3,3}, prism, K5-e, W5).
Each base edge is replaced by a path with s extra vertices, s in a range.
"""
from itertools import product
import json
from pathlib import Path
import networkx as nx
from claude_search import check

BASES = {
    "theta": ([(0, 1)] * 3, range(0, 9)),          # parallel edges -> subdivided
    "theta4": ([(0, 1)] * 4, range(0, 6)),
    "K4": (list(nx.complete_graph(4).edges()), range(0, 5)),
    "K33": (list(nx.complete_bipartite_graph(3, 3).edges()), range(0, 3)),
    "prism": (list(nx.circular_ladder_graph(3).edges()), range(0, 3)),
    "K5-e": ([e for e in nx.complete_graph(5).edges() if e != (0, 1)], range(0, 2)),
    "W5": (list(nx.wheel_graph(6).edges()), range(0, 2)),
}

def build(base, subs):
    G = nx.Graph()
    nxt = max(max(e) for e in base) + 1
    for (u, v), s in zip(base, subs):
        path = [u] + list(range(nxt, nxt + s)) + [v]
        nxt += s
        nx.add_path(G, path)
    return G

report = {}
for name, (base, rng) in BASES.items():
    seen = set(); checked = bad = to = 0; bads = []
    for subs in product(rng, repeat=len(base)):
        G = build(base, subs)
        if G.number_of_edges() != sum(s + 1 for s in subs):
            continue  # two unsubdivided parallel edges collapsed
        key = nx.weisfeiler_lehman_graph_hash(G)
        if key in seen:
            continue
        seen.add(key)
        res = check(G, node_limit=2_000_000)[0]
        checked += 1
        if res is None:
            bad += 1; bads.append(list(subs))
        elif res == "timeout":
            to += 1
    report[name] = {"subdivision_range": [rng.start, rng.stop - 1],
                    "classes_checked": checked, "counterexamples": bads, "timeouts": to}
    print(name, report[name], flush=True)
Path(__file__).with_name("claude_subdivisions.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
