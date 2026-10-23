module

import Mathlib.Data.Rat.Defs
public import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
# One-step log-concavity inequality for a single forbidden proportion

Source: conjecture 026, version 0.2, L1, `conjectures/026-cyclic-generation-logconcavity/conjectures.md`.
This module formalizes the algebraic inequality at the core of the prime-power argument.
It does not formalize the subgroup-counting interpretation or the binomial-ratio bounds.
-/

@[expose] public section

namespace MathWiki
namespace CyclicGeneration

def forbiddenRatio (n m k : ℕ) : ℚ :=
  (Nat.choose m k : ℚ) / Nat.choose n k

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

private theorem forbiddenRatio_succ_eq (m n k : ℕ)
    (hk : 0 < k) (hkm : k ≤ m) (hmn : m < n) :
    forbiddenRatio n m k = forbiddenRatio n m (k - 1) *
      (((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ)) := by
  have hk1 : k - 1 + 1 = k := by omega
  have hrecM := Nat.choose_succ_right_eq m (k - 1)
  have hrecN := Nat.choose_succ_right_eq n (k - 1)
  rw [hk1] at hrecM hrecN
  have hdiffM : m - (k - 1) = m - k + 1 := by omega
  have hdiffN : n - (k - 1) = n - k + 1 := by omega
  rw [hdiffM] at hrecM
  rw [hdiffN] at hrecN
  have hrecM' : (Nat.choose m k : ℚ) * (k : ℚ) =
      (Nat.choose m (k - 1) : ℚ) * ((m - k + 1 : ℕ) : ℚ) := by
    exact_mod_cast hrecM
  have hrecN' : (Nat.choose n k : ℚ) * (k : ℚ) =
      (Nat.choose n (k - 1) : ℚ) * ((n - k + 1 : ℕ) : ℚ) := by
    exact_mod_cast hrecN
  have hkq : (k : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hk)
  have hdenq : ((n - k + 1 : ℕ) : ℚ) ≠ 0 := by positivity
  have hchooseN : (Nat.choose n k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos (show k ≤ n by omega)
    exact_mod_cast (Nat.ne_of_gt hp)
  have hchooseM : (Nat.choose m k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos hkm
    exact_mod_cast (Nat.ne_of_gt hp)
  have hchoosePrevN : (Nat.choose n (k - 1) : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos (show k - 1 ≤ n by omega)
    exact_mod_cast (Nat.ne_of_gt hp)
  unfold forbiddenRatio
  field_simp [hkq, hdenq, hchooseN, hchooseM, hchoosePrevN]
  nlinarith [hrecM', hrecN']

private theorem forbiddenRatio_next_eq (m n k : ℕ)
    (hkm : k ≤ m) (hkn : k < n) :
    forbiddenRatio n m (k + 1) = forbiddenRatio n m k *
      (((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ)) := by
  have hrecM := Nat.choose_succ_right_eq m k
  have hrecN := Nat.choose_succ_right_eq n k
  have hrecM' : (Nat.choose m (k + 1) : ℚ) * (k + 1 : ℚ) =
      (Nat.choose m k : ℚ) * ((m - k : ℕ) : ℚ) := by
    exact_mod_cast hrecM
  have hrecN' : (Nat.choose n (k + 1) : ℚ) * (k + 1 : ℚ) =
      (Nat.choose n k : ℚ) * ((n - k : ℕ) : ℚ) := by
    exact_mod_cast hrecN
  have hk1q : (k + 1 : ℚ) ≠ 0 := by positivity
  have hdenq : ((n - k : ℕ) : ℚ) ≠ 0 := by
    have hp := Nat.sub_pos_of_lt hkn
    exact_mod_cast (Nat.ne_of_gt hp)
  have hchooseN : (Nat.choose n k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos (Nat.le_of_lt hkn)
    exact_mod_cast (Nat.ne_of_gt hp)
  have hchooseNextN : (Nat.choose n (k + 1) : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos (Nat.succ_le_of_lt hkn)
    exact_mod_cast (Nat.ne_of_gt hp)
  have hchooseM : (Nat.choose m k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos hkm
    exact_mod_cast (Nat.ne_of_gt hp)
  unfold forbiddenRatio
  field_simp [hk1q, hdenq, hchooseN, hchooseNextN, hchooseM]
  nlinarith [hrecM', hrecN']

/-- The prime-power proof's inner-index step for the binomial failure fraction.
Assume the two exact binomial ratios have the bounds proved in conjecture 026, L1.
Then the corresponding escape probabilities satisfy the log-concavity inequality. -/
theorem forbiddenRatio_escape_logConcave_at
    (m n k : ℕ) (hk2 : 2 ≤ k) (hkm : k ≤ m) (hmn : m < n)
    (hs : 0 ≤ ((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ))
    (hsr : ((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ) ≤
      ((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ))
    (hr : ((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ) ≤ 1 / 2) :
    (1 - forbiddenRatio n m k) ^ 2 ≥
      (1 - forbiddenRatio n m (k - 1)) * (1 - forbiddenRatio n m (k + 1)) := by
  have hk : 0 < k := by omega
  have hklt : k < n := lt_of_le_of_lt hkm hmn
  have hprev := forbiddenRatio_succ_eq m n k hk hkm hmn
  have hnext := forbiddenRatio_next_eq m n k hkm hklt
  have hcore := one_sub_ratio_logConcave
    (forbiddenRatio n m (k - 1))
    (((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ))
    (((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ))
    (by unfold forbiddenRatio; exact div_nonneg (by positivity) (by positivity)) hs hsr hr
  calc
    (1 - forbiddenRatio n m k) ^ 2 =
        (1 - (((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ)) *
          forbiddenRatio n m (k - 1)) ^ 2 := by rw [hprev]; ring
    _ ≥ (1 - forbiddenRatio n m (k - 1)) *
          (1 - (((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ)) *
            (((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ)) *
            forbiddenRatio n m (k - 1)) := hcore
    _ = (1 - forbiddenRatio n m (k - 1)) *
          (1 - forbiddenRatio n m (k + 1)) := by rw [hnext, hprev]; ring

end CyclicGeneration
end MathWiki
