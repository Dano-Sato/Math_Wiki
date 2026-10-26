import itertools
import sympy as sp

def audit(m):
    vertices = range(m)
    edges = list(itertools.combinations(vertices, 2))
    for mask in range(1 << len(edges)):
        A = sp.zeros(m)
        deg = [0] * m
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                A[u, v] = A[v, u] = 1
                deg[u] += 1
                deg[v] += 1
        L = sp.diag(*deg) - A
        M = (m + 1) * sp.eye(m) - L
        inv = M.inv()
        diag = [inv[i, i] for i in vertices]
        for u, v in itertools.permutations(vertices, 2):
            if deg[u] > deg[v] and not diag[u] > diag[v]:
                return {"m": m, "mask": mask, "edges": [e for i,e in enumerate(edges) if mask >> i & 1],
                        "deg_u_v": [deg[u],deg[v]], "diag_u_v": [diag[u],diag[v]], "u_v": [u,v]}
    return None

for m in range(2, 6):
    c = audit(m)
    print(m, c)
    if c:
        break
