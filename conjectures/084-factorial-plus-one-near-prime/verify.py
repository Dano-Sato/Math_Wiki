"""Exact small-n factorizations for conjecture 084.

Requires SymPy. This finite computation is exploratory only and does not
verify the asymptotic conjecture.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from sympy import factorint


rows = []
for n in range(3, 21):
    value = math.factorial(n) + 1
    factors = {int(p): int(e) for p, e in factorint(value).items()}
    largest = max(factors)
    rows.append(
        {
            "n": n,
            "n_factorial_plus_one": str(value),
            "largest_prime_factor": str(largest),
            "factorization": {str(p): e for p, e in factors.items()},
            "log_ratio_approx": math.log(largest) / math.log(value),
        }
    )

output = Path(__file__).with_name("verification.json")
output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
for row in rows:
    print(
        row["n"],
        row["largest_prime_factor"],
        f'{row["log_ratio_approx"]:.6f}',
        row["factorization"],
    )
