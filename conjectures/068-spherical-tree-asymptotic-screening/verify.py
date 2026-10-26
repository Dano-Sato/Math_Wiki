"""Exact finite checks for 068; no verification of the infinite theorem.

Run from any directory with Python 3.10+; standard library only.
The JSON records its source hash and the finite scope of each check.
"""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
BOOTSTRAP = (5, 4, 3, 5, 3, 3, 4, 4, 5, 3, 3, 4, 5, 4, 3, 4, 3)
A = (5, 3)
B = (7, 1, 5, 3, 3)
IDENTITY = ((Q(1), Q(0)), (Q(0), Q(1)))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def matrix(word):
    result = IDENTITY
    for c in word:
        result = multiply(((Q(4), Q(-4)), (Q(c - 4), Q(4))), result)
    return result


def projectively_equal(a, b):
    aa = [x for row in a for x in row]
    bb = [x for row in b for x in row]
    pivot = next(i for i, x in enumerate(bb) if x)
    return aa[pivot] != 0 and all(
        aa[i] * bb[pivot] == bb[i] * aa[pivot] for i in range(4)
    )


def f(c, q):
    denominator = (c - 4) * q + 4
    assert denominator != 0
    return 4 * (q - 1) / denominator


def orbit(word, x=Q(1)):
    states = [x]
    for c in word:
        assert x > 0
        x = 2 - Q(c, 4) / x
        states.append(x)
    return states


def pole(k):
    return -4 + Q(232, 3) * Q(5, 3) ** k


def ceiling(x):
    return -(-x.numerator // x.denominator)


def main():
    assert projectively_equal(matrix(A), ((Q(3), Q(-8)), (Q(0), Q(5))))
    assert projectively_equal(matrix(B), ((Q(-12), Q(460)), (Q(3), Q(-220))))

    # Matrix identities compare rational functions, not sampled evaluations.
    for k in range(1, 17):
        growth = Q(5, 3) ** k
        r = pole(k)
        expected = ((Q(4), 140 * growth - 4 * r), (Q(-1), r))
        assert projectively_equal(matrix(A * k + B), expected)

    states = orbit(BOOTSTRAP)
    assert all(0 < x < 1 for x in states[1:])
    q_states = [1 / (1 - x) for x in states[1:]]
    assert q_states[-1] == 312 > pole(1)

    # Check the telescoping product identity and final-pivot correction.
    product = Q(1)
    middle_product = Q(1)
    for m, c in enumerate(BOOTSTRAP, start=1):
        product *= Q(c, 4)
        if m > 1:
            middle_product *= 1 - (1 - states[m - 1]) ** 2
        assert product == (2 - states[m]) * middle_product
        defect = 1 - states[m]
        assert states[m] - 1 + defect == 0
        assert all(x > 0 for x in states[:m])

    q = q_states[-1]
    steps = len(BOOTSTRAP)
    cycles = []
    for k in range(1, 9):
        r = pole(k)
        assert q > r
        run_length = (q - r).__floor__() + 1
        entrance = q - run_length
        distance = r - entrance
        assert entrance > 1 and 0 < distance <= 1
        q = entrance
        minimum = q
        word = A * k + B
        for c in word:
            q = f(c, q)
            assert q > 1
            minimum = min(minimum, q)
        expected = 140 * Q(5, 3) ** k / distance - 4
        assert q == expected and q > pole(k + 1)
        steps += run_length + len(word)
        cycles.append({
            "k": k,
            "background_run_length": run_length,
            "prefix_length": steps,
            "distance_below_pole": str(distance),
            "minimum_q_inside_W": str(minimum),
            "exit_q": str(q),
            "next_pole": str(pole(k + 1)),
        })

    # One concrete finite continuity/barrier witness for the bootstrap block.
    defect = 1 - states[-1]
    eta = Q(1, 2)
    while True:
        trial = orbit(BOOTSTRAP, 1 + eta)
        if all(0 < x < 1 for x in trial[1:]) and trial[-1] <= 1 - defect / 2:
            break
        eta /= 2
    assert orbit(BOOTSTRAP, Q(1))[-1] == 1 - defect
    background_before = ceiling(1 / eta)
    background_after = ceiling(2 / defect) + 2
    # For any positive surviving exit bounded as above, q <= 2/defect.
    assert Q(2) / defect - background_after < 1

    result = {
        "id": "068",
        "version": "0.1",
        "arithmetic": "exact integers and fractions; Python standard library",
        "source_sha256": sha256((HERE / "source.txt").read_bytes()).hexdigest(),
        "checks": {
            "A_and_B_mobius_matrices": "passed",
            "W_k_rational_function_identity": {"k_min": 1, "k_max": 16},
            "bootstrap": {
                "word": list(BOOTSTRAP),
                "q_states": [str(x) for x in q_states],
                "minimum_q": str(min(q_states)),
                "exit_q": str(q_states[-1]),
            },
            "telescoping_product_identity_prefixes": len(BOOTSTRAP),
            "ldl_last_pivot_correction_prefixes": len(BOOTSTRAP),
            "compressed_seed_cycles": cycles,
            "finite_barrier_witness": {
                "word": "bootstrap",
                "endpoint_defect": str(defect),
                "eta": str(eta),
                "background_before_lower_bound": background_before,
                "background_after_lower_bound": background_after,
            },
        },
        "limitations": [
            "No finite calculation proves the infinite screening equivalence.",
            "No finite calculation proves absence of every infinite alternative parsing.",
            "Tree/Jacobi essential norms and the infinite construction require proof review.",
            "No Lean proof or independent model review is included.",
        ],
    }
    target = HERE / "verification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("068: all exact finite checks passed; results saved to verification.json")


if __name__ == "__main__":
    main()
