module

public import Mathlib.Data.Rat.Defs
public import Mathlib.Data.Nat.Choose.Basic
public import Mathlib.Data.Finset.Powerset
public import Mathlib.Data.Fintype.Card
public import Mathlib.GroupTheory.SpecificGroups.Cyclic.Subgroup
import Mathlib.Data.Nat.Cast.Order.Ring
import Mathlib.Algebra.Order.GroupWithZero.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
# Log-concavity of a single forbidden binomial proportion

Source: conjecture 026, version 0.2, L1, `conjectures/026-cyclic-generation-logconcavity/conjectures.md`.
This module formalizes the binomial-ratio recurrence, its elementary bounds, and the
resulting log-concavity theorem for `1 - choose(m,k)/choose(n,k)` when `2*m ≤ n`.
It also proves strict log-concavity of `choose(n,k) - choose(m,k)` and the general
product lemma used for that deduction. The identification of this arithmetic count
with generating subsets of a cyclic group is left to the source's subgroup argument.
-/

@[expose] public section

namespace MathWiki
namespace CyclicGeneration

def forbiddenRatio (n m k : ℕ) : ℚ :=
  (Nat.choose m k : ℚ) / Nat.choose n k

/-- The probability of avoiding the unique maximal proper subgroup in the
prime-power cyclic-group argument, expressed through its binomial ratio. -/
def escapeProbability (n m k : ℕ) : ℚ := 1 - forbiddenRatio n m k

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

private theorem forbiddenRatios_bounds (m n k : ℕ)
    (hk2 : 2 ≤ k) (hkm : k ≤ m) (h2m : 2 * m ≤ n) (hmn : m < n) :
    0 ≤ ((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ) ∧
    ((m - k : ℕ) : ℚ) / ((n - k : ℕ) : ℚ) ≤
      ((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ) ∧
    ((m - k + 1 : ℕ) : ℚ) / ((n - k + 1 : ℕ) : ℚ) ≤ 1 / 2 := by
  have hkn : k < n := lt_of_le_of_lt hkm hmn
  have hd0 : 0 < ((n - k : ℕ) : ℚ) := by
    have hp := Nat.sub_pos_of_lt hkn
    exact_mod_cast hp
  have hd1 : 0 < ((n - k + 1 : ℕ) : ℚ) := by positivity
  have hMsub : ((m - k : ℕ) : ℚ) = (m : ℚ) - k := Nat.cast_sub hkm
  have hNsub : ((n - k : ℕ) : ℚ) = (n : ℚ) - k :=
    Nat.cast_sub (le_of_lt hkn)
  have hMplus : ((m - k + 1 : ℕ) : ℚ) = (m : ℚ) - k + 1 := by
    rw [Nat.cast_add, Nat.cast_one, hMsub]
  have hNplus : ((n - k + 1 : ℕ) : ℚ) = (n : ℚ) - k + 1 := by
    rw [Nat.cast_add, Nat.cast_one, hNsub]
  constructor
  · exact div_nonneg (by positivity) (le_of_lt hd0)
  constructor
  · rw [div_le_div_iff₀ hd0 hd1]
    rw [hMsub, hNsub, hMplus, hNplus]
    have hmnq : (m : ℚ) < n := by exact_mod_cast hmn
    have hprod : ((m : ℚ) - k + 1) * ((n : ℚ) - k) -
        ((m : ℚ) - k) * ((n : ℚ) - k + 1) = (n : ℚ) - m := by ring
    linarith [hprod, hmnq]
  · rw [div_le_iff₀ hd1]
    rw [hMplus, hNplus]
    norm_num
    have h2mq : 2 * (m : ℚ) ≤ n := by exact_mod_cast h2m
    have hk1q : (1 : ℚ) ≤ k := by
      have : 1 ≤ k := by omega
      exact_mod_cast this
    nlinarith [h2mq, hk1q]

/-- The prime-power proof's inner-index step for the binomial failure fraction.
Assume the two exact binomial ratios have the bounds proved in conjecture 026, L1.
Then the corresponding escape probabilities satisfy the log-concavity inequality. -/
theorem forbiddenRatio_escape_logConcave_at
    (m n k : ℕ) (hk2 : 2 ≤ k) (hkm : k ≤ m)
    (h2m : 2 * m ≤ n) (hmn : m < n) :
    (1 - forbiddenRatio n m k) ^ 2 ≥
      (1 - forbiddenRatio n m (k - 1)) * (1 - forbiddenRatio n m (k + 1)) := by
  have hk : 0 < k := by omega
  have hklt : k < n := lt_of_le_of_lt hkm hmn
  obtain ⟨hs, hsr, hr⟩ := forbiddenRatios_bounds m n k hk2 hkm h2m hmn
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

private theorem forbiddenRatio_eq_zero_of_lt (n m k : ℕ)
    (hmk : m < k) (hkn : k ≤ n) : forbiddenRatio n m k = 0 := by
  have hnum : Nat.choose m k = 0 := Nat.choose_eq_zero_of_lt hmk
  have hden : (Nat.choose n k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos hkn
    exact_mod_cast (Nat.ne_of_gt hp)
  simp [forbiddenRatio, hnum]

private theorem forbiddenRatio_nonneg (n m k : ℕ) : 0 ≤ forbiddenRatio n m k := by
  unfold forbiddenRatio
  exact div_nonneg (by positivity) (by positivity)

/-- For `2m ≤ n`, the escape probabilities `1 - choose(m,k)/choose(n,k)`
form a log-concave sequence on all internal indices. This generalizes the
single-forbidden-subgroup calculation in conjecture 026, L1. -/
theorem escapeProbability_logConcave
    (n m : ℕ) (hm : 1 ≤ m) (h2m : 2 * m ≤ n) :
    ∀ k, 2 ≤ k → k < n →
      escapeProbability n m k ^ 2 ≥
        escapeProbability n m (k - 1) * escapeProbability n m (k + 1) := by
  have hmn : m < n := by omega
  intro k hk2 hkn
  by_cases hkm : k ≤ m
  · have hstep := forbiddenRatio_escape_logConcave_at m n k hk2 hkm h2m hmn
    simpa [escapeProbability] using hstep
  · by_cases hboundary : k = m + 1
    · have hkplus : k + 1 ≤ n := by omega
      have hmidzero : forbiddenRatio n m k = 0 :=
        forbiddenRatio_eq_zero_of_lt n m k (by omega) (by omega)
      have hnextzero : forbiddenRatio n m (k + 1) = 0 :=
        forbiddenRatio_eq_zero_of_lt n m (k + 1) (by omega) hkplus
      have hprev : k - 1 = m := by omega
      rw [escapeProbability, escapeProbability, escapeProbability,
        hmidzero, hnextzero, hprev]
      have hc : 0 ≤ forbiddenRatio n m m := forbiddenRatio_nonneg n m m
      norm_num
      nlinarith
    · have htail : m + 2 ≤ k := by omega
      have hmidzero : forbiddenRatio n m k = 0 :=
        forbiddenRatio_eq_zero_of_lt n m k (by omega) (by omega)
      have hprevzero : forbiddenRatio n m (k - 1) = 0 :=
        forbiddenRatio_eq_zero_of_lt n m (k - 1) (by omega) (by omega)
      have hnextzero : forbiddenRatio n m (k + 1) = 0 :=
        forbiddenRatio_eq_zero_of_lt n m (k + 1) (by omega)
          (by omega)
      simp [escapeProbability, hmidzero, hprevzero, hnextzero]

/-- The binomial coefficient row is strictly log-concave at every internal index.
This direct proof uses the two adjacent `choose_succ_right_eq` recurrences. -/
theorem choose_strictLogConcave (n k : ℕ) (hk2 : 2 ≤ k) (hkn : k < n) :
    (Nat.choose n k) ^ 2 > Nat.choose n (k - 1) * Nat.choose n (k + 1) := by
  let A := Nat.choose n k
  let B := Nat.choose n (k - 1)
  let C := Nat.choose n (k + 1)
  have hk1 : k - 1 + 1 = k := by omega
  have hdiff : n - (k - 1) = n - k + 1 := by omega
  have hrec1 : A * k = B * (n - k + 1) := by
    have hr := Nat.choose_succ_right_eq n (k - 1)
    rw [hk1, hdiff] at hr
    simpa [A, B] using hr
  have hrec2 : C * (k + 1) = A * (n - k) := by
    simpa [A, C] using Nat.choose_succ_right_eq n k
  have hratio : (n - k + 1) * (k + 1) = (n - k) * k + (n + 1) := by
    calc
      (n - k + 1) * (k + 1) = (n - k) * k + ((n - k) + k + 1) := by ring
      _ = (n - k) * k + (n + 1) := by
        rw [Nat.sub_add_cancel (le_of_lt hkn)]
  have hA : 0 < A := Nat.choose_pos (by omega)
  have hB : 0 < B := Nat.choose_pos (by omega)
  have hterm : 0 < A * B * (n + 1) := by positivity
  have hfactor : 0 < k * (k + 1) := Nat.mul_pos (by omega) (by omega)
  have hmul : B * C * (k * (k + 1)) < A ^ 2 * (k * (k + 1)) := by
    have hident : A ^ 2 * (k * (k + 1)) =
        B * C * (k * (k + 1)) + A * B * (n + 1) := by
      calc
        A ^ 2 * (k * (k + 1)) = (A * k) * (A * (k + 1)) := by ring
        _ = (B * (n - k + 1)) * (A * (k + 1)) := by rw [hrec1]
        _ = A * B * ((n - k + 1) * (k + 1)) := by ring
        _ = A * B * ((n - k) * k + (n + 1)) := by rw [hratio]
        _ = A * B * (n - k) * k + A * B * (n + 1) := by ring
        _ = B * (A * (n - k)) * k + A * B * (n + 1) := by ring
        _ = B * (C * (k + 1)) * k + A * B * (n + 1) := by rw [← hrec2]
        _ = B * C * (k * (k + 1)) + A * B * (n + 1) := by ring
    rw [hident]
    exact Nat.lt_add_of_pos_right hterm
  exact (Nat.mul_lt_mul_right hfactor).mp hmul

/-- Multiplying a positive log-concave sequence by a strictly log-concave
sequence preserves strict log-concavity. This is the final product step in 026, L1. -/
theorem strictLogConcave_mul_at
    (a b : ℕ → ℚ) (k : ℕ)
    (ha : a k ^ 2 > a (k - 1) * a (k + 1))
    (hb : b k ^ 2 ≥ b (k - 1) * b (k + 1))
    (hbprev : 0 < b (k - 1)) (hbnext : 0 < b (k + 1)) :
    (a k * b k) ^ 2 >
      (a (k - 1) * b (k - 1)) * (a (k + 1) * b (k + 1)) := by
  have hprod : 0 < b (k - 1) * b (k + 1) := mul_pos hbprev hbnext
  have hleft := mul_lt_mul_of_pos_right ha hprod
  have hright := mul_le_mul_of_nonneg_left hb (sq_nonneg (a k))
  calc
    (a k * b k) ^ 2 = (a k ^ 2) * (b k ^ 2) := by ring
    _ > (a (k - 1) * a (k + 1)) *
        (b (k - 1) * b (k + 1)) := lt_of_lt_of_le hleft hright
    _ = (a (k - 1) * b (k - 1)) * (a (k + 1) * b (k + 1)) := by ring

private theorem choose_lt_choose_of_pos {m n k : ℕ}
    (hmn : m < n) (hk : 0 < k) (hkn : k ≤ n) :
    Nat.choose m k < Nat.choose n k := by
  have hmle : m ≤ n - 1 := by omega
  have hstep : Nat.choose (n - 1) k < Nat.choose ((n - 1) + 1) k := by
    have hk1 : k - 1 + 1 = k := by omega
    have hpascal := Nat.choose_succ_succ' (n - 1) (k - 1)
    rw [hk1] at hpascal
    have hpos : 0 < Nat.choose (n - 1) (k - 1) := Nat.choose_pos (by omega)
    rw [hpascal]
    exact Nat.lt_add_of_pos_left hpos
  have hn : (n - 1) + 1 = n := by omega
  rw [hn] at hstep
  exact lt_of_le_of_lt (Nat.choose_le_choose k hmle) hstep

private theorem escapeProbability_pos
    (n m k : ℕ) (hmn : m < n) (hk : 0 < k) (hkn : k ≤ n) :
    0 < escapeProbability n m k := by
  have hchoose := choose_lt_choose_of_pos hmn hk hkn
  have hden : 0 < (Nat.choose n k : ℚ) := by
    have hp := Nat.choose_pos hkn
    exact_mod_cast hp
  have hratio : forbiddenRatio n m k < 1 := by
    unfold forbiddenRatio
    rw [div_lt_iff₀ hden]
    norm_num
    exact_mod_cast hchoose
  unfold escapeProbability
  linarith

/-- Arithmetic count proxy for the `k`-subsets not contained in a fixed
`m`-element forbidden set. -/
def generatingCountProxy (n m k : ℕ) : ℚ :=
  (Nat.choose n k : ℚ) * escapeProbability n m k

theorem generatingCountProxy_eq_choose_sub
    (n m k : ℕ) (hkn : k ≤ n) :
    generatingCountProxy n m k =
      (Nat.choose n k : ℚ) - Nat.choose m k := by
  have hden : (Nat.choose n k : ℚ) ≠ 0 := by
    have hp := Nat.choose_pos hkn
    exact_mod_cast (Nat.ne_of_gt hp)
  unfold generatingCountProxy escapeProbability forbiddenRatio
  field_simp [hden]

/-- Under `m ≥ 1` and `2m ≤ n`, the arithmetic sequence
`choose(n,k) - choose(m,k)` is strictly log-concave on internal indices.
For prime powers, this is the sequence in L1 after the unique-maximal-subgroup
counting argument identifies it with the number of generating subsets. -/
theorem generatingCountProxy_strictLogConcave
    (n m : ℕ) (hm : 1 ≤ m) (h2m : 2 * m ≤ n) :
    ∀ k, 2 ≤ k → k < n →
      generatingCountProxy n m k ^ 2 >
        generatingCountProxy n m (k - 1) * generatingCountProxy n m (k + 1) := by
  have hmn : m < n := by omega
  intro k hk2 hkn
  have hchooseNat := choose_strictLogConcave n k hk2 hkn
  have hchoose : (Nat.choose n k : ℚ) ^ 2 >
      (Nat.choose n (k - 1) : ℚ) * Nat.choose n (k + 1) := by
    exact_mod_cast hchooseNat
  have hprob := escapeProbability_logConcave n m hm h2m k hk2 hkn
  have hprobPrev : 0 < escapeProbability n m (k - 1) :=
    escapeProbability_pos n m (k - 1) hmn (by omega) (by omega)
  have hprobNext : 0 < escapeProbability n m (k + 1) :=
    escapeProbability_pos n m (k + 1) hmn (by omega) (by omega)
  have hproduct := strictLogConcave_mul_at
    (fun j => (Nat.choose n j : ℚ)) (escapeProbability n m) k
    hchoose hprob hprobPrev hprobNext
  simpa [generatingCountProxy] using hproduct

/-- The `k`-element subsets of a finite type that are not contained in a
fixed forbidden finset. -/
def notContainedKSubsets {α : Type*} [Fintype α] [DecidableEq α]
    (S : Finset α) (k : ℕ) : Finset (Finset α) :=
  Finset.univ.powersetCard k \ S.powersetCard k

/-- Counting `k`-subsets outside a fixed forbidden finset gives the difference
of the two corresponding binomial coefficients. This identifies the arithmetic
proxy above with an actual finite-set count. -/
theorem notContainedKSubsets_card {α : Type*} [Fintype α] [DecidableEq α]
    (S : Finset α) (k : ℕ) :
    (notContainedKSubsets S k).card =
      Nat.choose (Fintype.card α) k - Nat.choose S.card k := by
  have hsub : S.powersetCard k ⊆ Finset.univ.powersetCard k :=
    Finset.powersetCard_mono (Finset.subset_univ S)
  rw [notContainedKSubsets, Finset.card_sdiff_of_subset hsub,
    Finset.card_powersetCard, Finset.card_powersetCard]
  simp

private theorem notContainedKSubsets_card_cast_eq_proxy
    {α : Type*} [Fintype α] [DecidableEq α]
    (S : Finset α) (k : ℕ) (hkn : k ≤ Fintype.card α) :
    ((notContainedKSubsets S k).card : ℚ) =
      generatingCountProxy (Fintype.card α) S.card k := by
  rw [notContainedKSubsets_card,
    generatingCountProxy_eq_choose_sub (Fintype.card α) S.card k hkn]
  have hchoose : Nat.choose S.card k ≤ Nat.choose (Fintype.card α) k :=
    Nat.choose_le_choose k (Finset.card_le_univ S)
  rw [Nat.cast_sub hchoose]

/-- For a fixed forbidden set of size `m`, the number of `k`-subsets that
escape it is strictly log-concave when `m ≥ 1` and `2m ≤ |α|`. -/
theorem notContainedKSubsets_strictLogConcave
    {α : Type*} [Fintype α] [DecidableEq α] (S : Finset α)
    (hm : 1 ≤ S.card) (h2m : 2 * S.card ≤ Fintype.card α) :
    ∀ k, 2 ≤ k → k < Fintype.card α →
      ((notContainedKSubsets S k).card : ℚ) ^ 2 >
        ((notContainedKSubsets S (k - 1)).card : ℚ) *
          ((notContainedKSubsets S (k + 1)).card : ℚ) := by
  intro k hk2 hkn
  have hproxy := generatingCountProxy_strictLogConcave
    (Fintype.card α) S.card hm h2m k hk2 hkn
  have hcurr := notContainedKSubsets_card_cast_eq_proxy S k (by omega)
  have hprev := notContainedKSubsets_card_cast_eq_proxy S (k - 1) (by omega)
  have hnext := notContainedKSubsets_card_cast_eq_proxy S (k + 1) (by omega)
  calc
    ((notContainedKSubsets S k).card : ℚ) ^ 2 =
        generatingCountProxy (Fintype.card α) S.card k ^ 2 := by rw [hcurr]
    _ > generatingCountProxy (Fintype.card α) S.card (k - 1) *
        generatingCountProxy (Fintype.card α) S.card (k + 1) := hproxy
    _ = ((notContainedKSubsets S (k - 1)).card : ℚ) *
        ((notContainedKSubsets S (k + 1)).card : ℚ) := by rw [hprev, hnext]

/-- In a finite additive group of prime cardinality, a finite set generates
the whole group exactly when it contains a nonzero element. -/
theorem closure_eq_top_iff_exists_ne_zero
    {G : Type*} [AddCommGroup G] [Nontrivial G]
    [Fact (Nat.card G).Prime] (S : Finset G) :
    AddSubgroup.closure (S : Set G) = ⊤ ↔ ∃ x ∈ S, x ≠ 0 := by
  constructor
  · intro htop
    by_contra h
    have hzero : ∀ x ∈ S, x = 0 := by
      intro x hx
      by_contra hx0
      exact h ⟨x, hx, hx0⟩
    have hle : AddSubgroup.closure (S : Set G) ≤ ⊥ := by
      apply (AddSubgroup.closure_le (⊥ : AddSubgroup G)).2
      intro x hx
      simpa using hzero x hx
    rw [htop] at hle
    have htopbot : (⊤ : AddSubgroup G) ≤ ⊥ := by
      exact hle
    exact (bot_ne_top : (⊥ : AddSubgroup G) ≠ ⊤) (le_antisymm bot_le htopbot)
  · rintro ⟨x, hx, hx0⟩
    have hxclosure : x ∈ AddSubgroup.closure (S : Set G) :=
      AddSubgroup.subset_closure hx
    have hne : AddSubgroup.closure (S : Set G) ≠ ⊥ := by
      intro hbot
      have : x = 0 := by simpa [hbot] using hxclosure
      exact hx0 this
    rcases AddSubgroup.eq_bot_or_eq_top_of_prime_card
        (AddSubgroup.closure (S : Set G)) with hbot | htop
    · exact (hne hbot).elim
    · exact htop

/-- The `k`-element generating subsets of a finite group of prime order are
exactly the `k`-subsets not contained in `{0}`. -/
noncomputable def generatingKSubsets
    {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] (k : ℕ) :
    Finset (Finset G) := by
  classical
  exact (Finset.univ.powersetCard k).filter
    (fun A : Finset G => AddSubgroup.closure (A : Set G) = ⊤)

theorem generatingKSubsets_eq_notContained
    {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] [Nontrivial G]
    [Fact (Nat.card G).Prime] (k : ℕ) :
    generatingKSubsets (G := G) k =
      notContainedKSubsets ({0} : Finset G) k := by
  classical
  ext A
  simp [generatingKSubsets, notContainedKSubsets,
    closure_eq_top_iff_exists_ne_zero, Finset.subset_iff]
  intro hcard
  constructor
  · rintro ⟨x, hx, hx0⟩ hall
    simpa [hcard] using hx0 (hall hx)
  · intro hnot
    by_contra hno
    have hall : ∀ ⦃x : G⦄, x ∈ A → x = 0 := by
      intro x hx
      by_contra hx0
      exact hno ⟨x, hx, hx0⟩
    exact (hnot hall) hcard

/-- The generating-subset counts of a finite additive group of prime
cardinality are strictly log-concave at every internal index. -/
theorem generatingKSubsets_strictLogConcave
    {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] [Nontrivial G]
    [Fact (Nat.card G).Prime] (hcard : 2 ≤ Fintype.card G) :
    ∀ k, 2 ≤ k → k < Fintype.card G →
      ((generatingKSubsets (G := G) k).card : ℚ) ^ 2 >
        ((generatingKSubsets (G := G) (k - 1)).card : ℚ) *
          ((generatingKSubsets (G := G) (k + 1)).card : ℚ) := by
  have hlog := notContainedKSubsets_strictLogConcave
    ({0} : Finset G) (by simp) (by simpa using hcard)
  intro k hk2 hkn
  simpa only [generatingKSubsets_eq_notContained] using hlog k hk2 hkn

end CyclicGeneration
end MathWiki
