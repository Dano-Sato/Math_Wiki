module

public import Mathlib.Data.Rat.Defs
public import Mathlib.Data.Nat.Choose.Basic
public import Mathlib.Data.Nat.Find
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Lean.Elab.Tactic.Omega

/-!
# Ratio thresholds and unimodality of weighted binomial rows

Source: conjecture 037, version 0.3,
`conjectures/037-singleton-count-unimodality/proof_unimodality.md`, sections 1, 6, 7.

This module proves the algebraic implication from two growth-ratio bounds to
strictly increasing thresholds, the exact adjacent-step identity for weighted
binomial rows, and the finite no-down-then-up criterion for unimodality.
These are reusable sufficient-condition lemmas, not claims of new mathematics.

The positive-moment and covariance argument establishing the ratio bounds for
singleton-free Bell numbers is a written proof in the source; it is NOT
formalized here. In particular, this module does not certify the whole of 037.
No finite computation or additional axioms are used.
-/

@[expose] public section

namespace MathWiki.SingletonDistribution

/-- A row is weakly increasing up to `p` and weakly decreasing afterwards. -/
def UnimodalRow (a : ℕ → ℚ) (N : ℕ) : Prop :=
  ∃ p ≤ N, (∀ k < p, a k ≤ a (k + 1)) ∧
    (∀ k, p ≤ k → k < N → a (k + 1) ≤ a k)

/-- The elementary threshold step used in source section 6. -/
theorem threshold_step_pos (m r s : ℚ)
    (hm : 0 ≤ m) (hr : 0 < r) (hs : 0 < s)
    (hstep : s ≤ r + 1) (hquad : m < r ^ 2 + 2 * r) :
    0 < 1 + (m + 1) / s - m / r := by
  have hr1 : 0 < r + 1 := by linarith
  have hcompare : (m + 1) / (r + 1) ≤ (m + 1) / s := by
    apply (div_le_div_iff₀ hr1 hs).mpr
    exact mul_le_mul_of_nonneg_left hstep (by linarith)
  have hcore : 0 < 1 + (m + 1) / (r + 1) - m / r := by
    have hidentity : 1 + (m + 1) / (r + 1) - m / r =
        (r ^ 2 + 2 * r - m) / (r * (r + 1)) := by
      field_simp
      ring
    rw [hidentity]
    exact div_pos (by linarith) (mul_pos hr hr1)
  linarith

/-- The same step with natural-number indices and two adjacent ratios. -/
theorem ratio_threshold_lt (m : ℕ) (r s : ℚ)
    (hr : 0 < r) (hs : 0 < s)
    (hstep : s ≤ r + 1) (hquad : (m : ℚ) < r ^ 2 + 2 * r) :
    (m : ℚ) - 1 + (m : ℚ) / r <
      (m : ℚ) + (m + 1 : ℚ) / s := by
  have h := threshold_step_pos (m : ℚ) r s (by positivity) hr hs hstep hquad
  linarith

/-- Any finite row with no later rise after a strict fall is weakly unimodal.
Equalities are allowed, including at the peak and along either side. -/
theorem unimodalRow_of_no_down_up (a : ℕ → ℚ) (N : ℕ)
    (hno : ∀ i j, i < j → j < N → a (i + 1) < a i →
      a j < a (j + 1) → False) : UnimodalRow a N := by
  classical
  by_cases h : ∃ k, k < N ∧ a (k + 1) < a k
  · let p := Nat.find h
    have hp : p < N ∧ a (p + 1) < a p := Nat.find_spec h
    refine ⟨p, Nat.le_of_lt hp.1, ?_, ?_⟩
    · intro k hk
      have hmin : ¬(k < N ∧ a (k + 1) < a k) := Nat.find_min h hk
      have hkN : k < N := lt_trans hk hp.1
      exact le_of_not_gt (fun hdown => hmin ⟨hkN, hdown⟩)
    · intro k hpk hkN
      rcases eq_or_lt_of_le hpk with heq | hlt
      · subst k
        exact le_of_lt hp.2
      · exact le_of_not_gt (fun hup => hno p k hlt hkN hp.2 hup)
  · refine ⟨N, le_rfl, ?_, ?_⟩
    · intro k hk
      exact le_of_not_gt (fun hdown => h ⟨k, hk, hdown⟩)
    · intro k hNk hkN
      omega

/-- Decreasing real-valued sign thresholds give the no-down-then-up criterion. -/
theorem unimodalRow_of_decreasing_sign_thresholds
    (a t : ℕ → ℚ) (N : ℕ)
    (hthreshold : ∀ i j, i < j → j < N → t j ≤ t i)
    (hdown : ∀ k < N, a (k + 1) < a k ↔ t k < 0)
    (hup : ∀ k < N, a k < a (k + 1) ↔ 0 < t k) :
    UnimodalRow a N := by
  apply unimodalRow_of_no_down_up
  intro i j hij hj hdi huj
  have hi : i < N := lt_trans hij hj
  have hti := (hdown i hi).mp hdi
  have htj := (hup j hj).mp huj
  have ht := hthreshold i j hij hj
  linarith

/-- Arithmetic form of a singleton distribution, with an arbitrary base sequence. -/
def binomialRow (b : ℕ → ℚ) (n k : ℕ) : ℚ := (Nat.choose n k : ℚ) * b (n - k)

/-- A division-free exact adjacent-step identity. It only uses the binomial
recurrence, so no positivity or nonvanishing assumptions on `b` are needed. -/
theorem binomialRow_step_mul (b : ℕ → ℚ) (n k : ℕ) :
    binomialRow b n (k + 1) * (k + 1 : ℚ) =
      (Nat.choose n k : ℚ) * (n - k : ℕ) * b (n - (k + 1)) := by
  have hrec : (Nat.choose n (k + 1) : ℚ) * (k + 1 : ℚ) =
      (Nat.choose n k : ℚ) * (n - k : ℕ) := by
    exact_mod_cast Nat.choose_succ_right_eq n k
  unfold binomialRow
  calc
    (Nat.choose n (k + 1) : ℚ) * b (n - (k + 1)) * (k + 1 : ℚ) =
        ((Nat.choose n (k + 1) : ℚ) * (k + 1 : ℚ)) * b (n - (k + 1)) := by ring
    _ = _ := by rw [hrec]

/-- The threshold from source section 1; only indices at least three are used
for the actual singleton distribution. -/
def threshold (b : ℕ → ℚ) (m : ℕ) : ℚ :=
  (m : ℚ) - 1 + (m : ℚ) * b (m - 1) / b m

/-- Exact factorization of an adjacent difference by its threshold. For the
source sequence the two factors outside the threshold are positive, giving
the sign equivalence in equation (1). -/
theorem binomialRow_step_difference (b : ℕ → ℚ) (m k : ℕ)
    (hb : b m ≠ 0) :
    (k + 1 : ℚ) * (binomialRow b (m + k) (k + 1) - binomialRow b (m + k) k) =
      (Nat.choose (m + k) k : ℚ) * b m * (threshold b m - (m + k : ℚ)) := by
  have hsub : m + k - (k + 1) = m - 1 := by omega
  have hrec := binomialRow_step_mul b (m + k) k
  simp only [Nat.add_sub_cancel_right, hsub] at hrec
  calc
    (k + 1 : ℚ) * (binomialRow b (m + k) (k + 1) - binomialRow b (m + k) k) =
        (Nat.choose (m + k) k : ℚ) * m * b (m - 1) -
          (k + 1 : ℚ) * ((Nat.choose (m + k) k : ℚ) * b m) := by
      rw [mul_sub, mul_comm (k + 1 : ℚ), hrec]
      simp only [binomialRow, Nat.add_sub_cancel_right]
    _ = _ := by
      unfold threshold
      field_simp
      ring

end MathWiki.SingletonDistribution
