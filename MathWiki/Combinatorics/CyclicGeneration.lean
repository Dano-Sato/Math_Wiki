import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
# One-step log-concavity inequality for a single forbidden proportion

Source: conjecture 026, version 0.2, L1, `conjectures/026-cyclic-generation-logconcavity/conjectures.md`.
This module formalizes the algebraic inequality at the core of the prime-power argument.
It does not formalize the subgroup-counting interpretation or the binomial-ratio bounds.
-/

namespace MathWiki
namespace CyclicGeneration

/-- If successive forbidden proportions shrink by ratios `r` and `s`,
with `0 ≤ s ≤ r ≤ 1/2`, then subtracting them from one gives the
log-concavity inequality. This is the algebraic kernel used in conjecture 026, L1. -/
theorem one_sub_ratio_logConcave
    (x r s : ℚ)
    (hx : 0 ≤ x)
    (hs : 0 ≤ s)
    (hsr : s ≤ r)
    (hr : r ≤ 1 / 2) :
    (1 - r * x) ^ 2 ≥ (1 - x) * (1 - r * s * x) := by
  have hA : 0 ≤ 1 - 2 * r + r * s := by
    have hrs : 0 ≤ r * s := mul_nonneg (by linarith : 0 ≤ r) hs
    linarith
  have hB : 0 ≤ r * (r - s) := mul_nonneg (by linarith : 0 ≤ r) (by linarith)
  have hfirst : 0 ≤ x * (1 - 2 * r + r * s) := mul_nonneg hx hA
  have hsecond : 0 ≤ x ^ 2 * r * (r - s) := by
    have hx2 : 0 ≤ x ^ 2 := sq_nonneg x
    exact mul_nonneg (mul_nonneg hx2 (by linarith : 0 ≤ r)) (by linarith)
  have hdiff : (1 - r * x) ^ 2 - (1 - x) * (1 - r * s * x) ≥ 0 := by
    calc
    (1 - r * x) ^ 2 - (1 - x) * (1 - r * s * x) =
        x * (1 - 2 * r + r * s) + x ^ 2 * r * (r - s) := by ring
    _ ≥ 0 := add_nonneg hfirst hsecond
  exact sub_nonneg.mp hdiff
end CyclicGeneration
end MathWiki
