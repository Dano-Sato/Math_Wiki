import itertools, numpy as np, networkx as nx

def flower_snark(k):
    G = nx.Graph()
    for i in range(k):
        (a, b, c, d) = (('a', i), ('b', i), ('c', i), ('d', i))
        G.add_edges_from([(a, b), (a, c), (a, d)])
    for i in range(k):
        j = (i + 1) % k
        G.add_edge(('b', i), ('b', j))
    cyc = [('c', i) for i in range(k)] + [('d', i) for i in range(k)]
    for i in range(2 * k):
        G.add_edge(cyc[i], cyc[(i + 1) % (2 * k)])
    return nx.convert_node_labels_to_integers(G)

def coxeter():
    return nx.LCF_graph(28, [-13, -9, 7, -7, 9, 13], 4) if False else nx.from_dict_of_lists(nx.to_dict_of_lists(_coxeter()))

def _coxeter():
    G = nx.Graph()
    for i in range(7):
        G.add_edge(('a', i), ('a', (i + 1) % 7))
        G.add_edge(('b', i), ('b', (i + 2) % 7))
        G.add_edge(('c', i), ('c', (i + 3) % 7))
        for x in 'abc':
            G.add_edge(('d', i), (x, i))
    return nx.convert_node_labels_to_integers(G)

def is_hamiltonian(G):
    n = G.number_of_nodes()
    adj = {v: set(G[v]) for v in G}
    start = 0
    path = [start]
    seen = {start}

    def rec():
        if len(path) == n:
            return start in adj[path[-1]]
        for w in adj[path[-1]]:
            if w not in seen:
                seen.add(w)
                path.append(w)
                if rec():
                    return True
                path.pop()
                seen.discard(w)
        return False
    return rec()

def substitute(H, P, replace):
    G = nx.Graph()
    att = {}
    for w in H:
        if w in replace:
            F = nx.relabel_nodes(P, {x: (w, x) for x in P})
            v = (w, 0)
            nb = list(F[v])
            F.remove_node(v)
            G.add_edges_from(F.edges())
            att[w] = nb
        else:
            G.add_node((w, 'x'))
    used = {w: 0 for w in H}
    for (a, b) in H.edges():
        pa = att[a][used[a]] if a in att else (a, 'x')
        used[a] += 1
        pb = att[b][used[b]] if b in att else (b, 'x')
        used[b] += 1
        G.add_edge(pa, pb)
    return nx.convert_node_labels_to_integers(G)

def mu(G):
    L = nx.laplacian_matrix(G, nodelist=sorted(G)).toarray().astype(float)
    Lp = np.linalg.pinv(L)
    idx = {v: i for (i, v) in enumerate(sorted(G))}
    m = {v: 0.0 for v in G}
    for (u, v) in G.edges():
        (i, j) = (idx[u], idx[v])
        r = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
        m[u] += r
        m[v] += r
    return m
import math, time
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix

def window_tree(G, m):
    nodes = sorted(G)
    n = len(nodes)
    E = list(G.edges())
    k = len(E)
    lo = {v: math.floor(m[v] + 1e-09) for v in nodes}
    hi = {v: math.ceil(m[v] - 1e-09) for v in nodes}
    for v in nodes:
        if abs(m[v] - round(m[v])) < 1e-09:
            lo[v] = hi[v] = round(m[v])
    nv = 3 * k
    A = lil_matrix((n + n + k + k + 1, nv))
    lb = []
    ub = []
    r = 0
    for v in nodes:
        for (i, (a, b)) in enumerate(E):
            if v in (a, b):
                A[r, i] = 1
        lb.append(lo[v])
        ub.append(hi[v])
        r += 1
    root = nodes[0]
    for v in nodes:
        for (i, (a, b)) in enumerate(E):
            if b == v:
                A[r, k + i] += 1
                A[r, 2 * k + i] -= 1
            if a == v:
                A[r, k + i] -= 1
                A[r, 2 * k + i] += 1
        t = -(n - 1) if v == root else 1
        lb.append(t)
        ub.append(t)
        r += 1
    for i in range(k):
        A[r, k + i] = 1
        A[r, i] = -(n - 1)
        lb.append(-np.inf)
        ub.append(0)
        r += 1
        A[r, 2 * k + i] = 1
        A[r, i] = -(n - 1)
        lb.append(-np.inf)
        ub.append(0)
        r += 1
    for i in range(k):
        A[r, i] = 1
    lb.append(n - 1)
    ub.append(n - 1)
    r += 1
    A = A[:r].tocsr()
    integ = np.r_[np.ones(k), np.zeros(2 * k)]
    res = milp(c=np.zeros(nv), constraints=LinearConstraint(A, lb, ub), integrality=integ, bounds=Bounds(np.zeros(nv), np.r_[np.ones(k), np.full(2 * k, n - 1)]), options={'time_limit': 300})
    if res.status == 0:
        x = res.x[:k] > 0.5
        T = nx.Graph()
        T.add_nodes_from(nodes)
        T.add_edges_from((e for (e, s) in zip(E, x) if s))
        ok = nx.is_tree(T) and all((lo[v] <= T.degree(v) <= hi[v] for v in nodes))
        return 'tree found' + ('' if ok else ' (VERIFY FAILED)')
    return {2: 'INFEASIBLE', 1: 'timeout'}.get(res.status, f'status {res.status}')