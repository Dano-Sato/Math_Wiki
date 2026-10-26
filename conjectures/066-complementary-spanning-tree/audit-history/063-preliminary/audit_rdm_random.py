import numpy as np
import random

for m in range(6, 16):
    for q in range(5000):
        prob = random.random()
        A = np.triu((np.random.random((m, m)) < prob).astype(float), 1)
        A += A.T
        d = A.sum(0)
        M = (m + 1) * np.eye(m) - np.diag(d) + A
        D = np.diag(np.linalg.inv(M))
        for u in range(m):
            for v in range(m):
                if d[u] > d[v] and D[u] <= D[v] + 1e-12:
                    print('counterexample', m, 'p', q, 'edges', [(i,j) for i in range(m) for j in range(i+1,m) if A[i,j]], 'uv', u, v, 'degrees', d[u], d[v], 'diags', D[u], D[v])
                    raise SystemExit
    print('passed random', m)
