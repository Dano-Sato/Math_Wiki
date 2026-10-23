"""Exhaustively test rooted-subtree unimodality on all labeled trees up to n=8."""

from itertools import product
import json
from pathlib import Path


def prufer_tree(n, code):
    degree = [1] * n
    for v in code:
        degree[v] += 1
    adj = [set() for _ in range(n)]
    for v in code:
        leaf = next(i for i, d in enumerate(degree) if d == 1)
        adj[leaf].add(v)
        adj[v].add(leaf)
        degree[leaf] -= 1
        degree[v] -= 1
    a, b = (i for i, d in enumerate(degree) if d == 1)
    adj[a].add(b)
    adj[b].add(a)
    return adj


def rooted_counts(adj, root):
    parent = [-2] * len(adj)
    parent[root] = -1
    order = [root]
    for v in order:
        for w in adj[v]:
            if parent[w] == -2:
                parent[w] = v
                order.append(w)
    polys = [None] * len(adj)
    for v in reversed(order):
        product_poly = [1]
        for w in adj[v]:
            if parent[w] == v:
                # The child polynomial stores coefficients of F_w(z), with
                # its degree-zero coefficient explicitly present as zero.
                factor = polys[w].copy()
                factor[0] += 1  # 1 + F_w(z)
                grown = [0] * (len(product_poly) + len(factor) - 1)
                for i, a in enumerate(product_poly):
                    for j, b in enumerate(factor):
                        grown[i + j] += a * b
                product_poly = grown
        polys[v] = [0] + product_poly  # F_v(z) = z * product_poly
    return polys[root][1:]


def is_unimodal(values):
    descending = False
    for left, right in zip(values, values[1:]):
        if right < left:
            descending = True
        elif right > left and descending:
            return False
    return True


def tree_centers(adj):
    eccentricities = []
    for start in range(len(adj)):
        distances = [-1] * len(adj)
        distances[start] = 0
        queue = [start]
        for v in queue:
            for w in adj[v]:
                if distances[w] == -1:
                    distances[w] = distances[v] + 1
                    queue.append(w)
        eccentricities.append(max(distances))
    radius = min(eccentricities)
    return [v for v, e in enumerate(eccentricities) if e == radius]


def main():
    results = []
    for n in range(1, 9):
        code_count = n ** (n - 2) if n >= 2 else 1
        tested = 0
        first_no_good_root = None
        first_bad_root = None
        first_bad_center = None
        for code in product(range(n), repeat=max(0, n - 2)):
            adj = prufer_tree(n, code) if n >= 2 else [set()]
            profiles = [rooted_counts(adj, root) for root in range(n)]
            good_roots = [root for root, profile in enumerate(profiles)
                          if is_unimodal(profile)]
            bad_roots = [root for root, profile in enumerate(profiles)
                         if not is_unimodal(profile)]
            tested += 1
            if bad_roots and first_bad_root is None:
                first_bad_root = {
                    "prufer_code": list(code),
                    "edges": [[v, w] for v in range(n) for w in adj[v] if v < w],
                    "bad_root_profiles": {str(root): profiles[root]
                                          for root in bad_roots},
                    "good_roots": good_roots,
                }
            if not good_roots and first_no_good_root is None:
                first_no_good_root = {
                    "prufer_code": list(code),
                    "edges": [[v, w] for v in range(n) for w in adj[v] if v < w],
                    "profiles": profiles,
                }
                break
            centers = tree_centers(adj)
            bad_centers = [root for root in centers
                           if not is_unimodal(profiles[root])]
            if bad_centers and first_bad_center is None:
                first_bad_center = {
                    "prufer_code": list(code),
                    "edges": [[v, w] for v in range(n) for w in adj[v] if v < w],
                    "centers": centers,
                    "bad_center_profiles": {str(root): profiles[root]
                                             for root in bad_centers},
                    "all_good_roots": good_roots,
                }
        results.append({"n": n, "labeled_trees_expected": code_count,
                        "labeled_trees_tested": tested,
                        "first_tree_with_no_good_root": first_no_good_root,
                        "first_tree_with_a_bad_root": first_bad_root,
                        "first_tree_where_a_center_fails": first_bad_center})
        if first_no_good_root is not None:
            break
    output = {"method": "Pruefer enumeration; exact integer polynomial DP at every root",
              "results": results,
              "scope": "All labeled trees at each completed size; finite computation only."}
    Path(__file__).with_name("review_2026-10-24.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
