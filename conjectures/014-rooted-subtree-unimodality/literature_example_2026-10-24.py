"""Check every possible root of Brown's 11-vertex non-unimodal example.

The tree is the root-identification of brooms B_{3,2} and B_{2,3} described
in Figure 1 of Brown (2019), DOI 10.30707/JIS.220.2.157019.
Vertex 0 is the shared root; vertices 1-2 and 6-8 are the handles, with
leaves 3-5 and 9-10 attached to their distal hubs.
"""

ADJ = [set() for _ in range(11)]


def add_edge(u: int, v: int) -> None:
    ADJ[u].add(v)
    ADJ[v].add(u)


for _u, _v in [
    (0, 1), (1, 2), (2, 3), (2, 4), (2, 5),
    (0, 6), (6, 7), (7, 8), (8, 9), (8, 10),
]:
    add_edge(_u, _v)


def rooted_profile(root: int) -> list[int]:
    """Exact coefficients of z * product_child (1 + F_child(z))."""
    parent = {root: -1}
    order = [root]
    for vertex in order:
        for neighbor in ADJ[vertex]:
            if neighbor not in parent:
                parent[neighbor] = vertex
                order.append(neighbor)

    polynomials: dict[int, list[int]] = {}
    for vertex in reversed(order):
        product = [1]
        for child in ADJ[vertex]:
            if parent.get(child) != vertex:
                continue
            factor = polynomials[child][:]
            factor[0] += 1
            result = [0] * (len(product) + len(factor) - 1)
            for i, left in enumerate(product):
                for j, right in enumerate(factor):
                    result[i + j] += left * right
            product = result
        polynomials[vertex] = [0] + product
    return polynomials[root][1:]


def is_unimodal(sequence: list[int]) -> bool:
    return any(
        all(sequence[i] <= sequence[i + 1] for i in range(peak))
        and all(sequence[i] >= sequence[i + 1] for i in range(peak, len(sequence) - 1))
        for peak in range(len(sequence))
    )


if __name__ == "__main__":
    for root in range(len(ADJ)):
        profile = rooted_profile(root)
        print(root, profile, is_unimodal(profile))
