module

public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Algebra.Group.Fin.Basic
public import Mathlib.Algebra.Order.BigOperators.Ring.Finset
public import Mathlib.Data.Int.Order.Basic

/-!
# Finite cyclic autocorrelation

Source: conjecture 013, version 0.1, `conjectures/013-nonpositive-cyclic-correlation/`
(`conjectures.md`, L1 and L2). The proofs are the finite-sum expansion and change of
index described there. These are standard autocorrelation identities, not a claim
of mathematical novelty.

The algebraic identities hold on any finite additive commutative group. The final
theorems specialize to the original integer-centered permutation on `Fin n`, whose
addition is modulo `n`. A value `p i : Fin n` represents the original label `p i + 1`.
Thus `2 * (p i).val + 1 - n` is exactly `2 * label - (n + 1)` in the source.

The general existence of a permutation making *all* nonzero correlations
nonpositive (013) remains open. No finite search or computation is used here.
-/

@[expose] public section

open scoped BigOperators

namespace MathWiki
namespace CyclicCorrelation

variable {G R : Type*} [Fintype G] [AddCommGroup G] [CommRing R]

/-- Correlation of a signal with its translate by `k`. -/
def autocorrelation (x : G → R) (k : G) : R :=
  ∑ i, x i * x (i + k)

/-- The zero-shift correlation is the energy of the signal. -/
@[simp]
theorem autocorrelation_zero (x : G → R) :
    autocorrelation x 0 = ∑ i, x i ^ 2 := by
  simp [autocorrelation, pow_two]

/-- Opposite shifts have equal autocorrelation (013, L2). -/
@[simp]
theorem autocorrelation_neg (x : G → R) (k : G) :
    autocorrelation x (-k) = autocorrelation x k := by
  unfold autocorrelation
  refine Fintype.sum_equiv (Equiv.addRight (-k)) _ _ ?_
  intro i
  simp [add_assoc, mul_comm]

/-- Summing all correlations gives the square of the signal's sum (013, L1). -/
theorem sum_autocorrelation (x : G → R) :
    ∑ k, autocorrelation x k = (∑ i, x i) ^ 2 := by
  unfold autocorrelation
  rw [Finset.sum_comm]
  simp_rw [← Finset.mul_sum]
  have hshift (i : G) : ∑ k, x (i + k) = ∑ k, x k :=
    Equiv.sum_comp (Equiv.addLeft i) x
  simp_rw [hshift]
  rw [← Finset.sum_mul, pow_two]

/-- For a zero-sum signal, nonzero shifts sum to minus its energy (013, L1). -/
theorem sum_nonzero_autocorrelation [DecidableEq G] (x : G → R)
    (hzero : ∑ i, x i = 0) :
    ∑ k ∈ Finset.univ.erase 0, autocorrelation x k = -(∑ i, x i ^ 2) := by
  apply eq_neg_iff_add_eq_zero.mpr
  calc
    (∑ k ∈ Finset.univ.erase 0, autocorrelation x k) + ∑ i, x i ^ 2 =
        ∑ k, autocorrelation x k := by
      rw [← autocorrelation_zero]
      exact Finset.sum_erase_add _ _ (Finset.mem_univ 0)
    _ = 0 := by rw [sum_autocorrelation, hzero]; simp

/-- A nonzero zero-sum signal has a strictly negative nonzero shift. -/
theorem exists_negative_autocorrelation [LinearOrder R] [IsStrictOrderedRing R]
    (x : G → R) (hzero : ∑ i, x i = 0) (hne : ∃ i, x i ≠ 0) :
    ∃ k, k ≠ 0 ∧ autocorrelation x k < 0 := by
  classical
  obtain ⟨i, hi⟩ := hne
  have henergy : 0 < ∑ j, x j ^ 2 :=
    (Finset.sum_pos_iff_of_nonneg (fun j _ => sq_nonneg (x j))).mpr
      ⟨i, Finset.mem_univ i, sq_pos_of_ne_zero hi⟩
  have hsum : (∑ k ∈ Finset.univ.erase 0, autocorrelation x k) < 0 := by
    rw [sum_nonzero_autocorrelation x hzero]
    exact neg_neg_of_pos henergy
  by_contra h
  have hnonneg : 0 ≤ ∑ k ∈ Finset.univ.erase 0, autocorrelation x k := by
    apply Finset.sum_nonneg
    intro k hk
    exact le_of_not_gt (fun hneg => h ⟨k, (Finset.mem_erase.mp hk).1, hneg⟩)
  exact (not_lt_of_ge hnonneg) hsum

variable {n : ℕ}

/-- Twice-centered integer values of a permutation of the labels `1, ..., n`. -/
def centeredPermutation (p : Equiv.Perm (Fin n)) (i : Fin n) : ℤ :=
  2 * ((p i).val : ℤ) + 1 - (n : ℤ)

private theorem sum_odd_labels (n : ℕ) :
    (∑ i : Fin n, (2 * (i.val : ℤ) + 1)) = (n : ℤ) ^ 2 := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Fin.sum_univ_castSucc]
    simp only [Fin.val_castSucc, Fin.val_last]
    rw [ih]
    push_cast
    ring

/-- Centering any permutation of the labels gives a zero-sum signal (013, L1). -/
theorem sum_centeredPermutation (p : Equiv.Perm (Fin n)) :
    ∑ i, centeredPermutation p i = 0 := by
  unfold centeredPermutation
  rw [Equiv.sum_comp p (fun i : Fin n => 2 * (i.val : ℤ) + 1 - (n : ℤ))]
  rw [Finset.sum_sub_distrib, sum_odd_labels]
  simp [pow_two]

/-- At size at least two, the centered permutation is not the zero signal. -/
theorem centeredPermutation_nonzero [NeZero n] (p : Equiv.Perm (Fin n)) (hn : 2 ≤ n) :
    ∃ i, centeredPermutation p i ≠ 0 := by
  refine ⟨p.symm 0, ?_⟩
  simp only [centeredPermutation, Equiv.apply_symm_apply, Fin.val_zero,
    Nat.cast_zero, mul_zero, zero_add]
  omega

/-- The original integer-centered permutation always has negative total nonzero correlation. -/
theorem centeredPermutation_nonzero_sum_neg [NeZero n]
    (p : Equiv.Perm (Fin n)) (hn : 2 ≤ n) :
    (∑ k ∈ Finset.univ.erase 0, autocorrelation (centeredPermutation p) k) < 0 := by
  rw [sum_nonzero_autocorrelation _ (sum_centeredPermutation p)]
  obtain ⟨i, hi⟩ := centeredPermutation_nonzero p hn
  apply neg_neg_of_pos
  exact (Finset.sum_pos_iff_of_nonneg (fun j _ => sq_nonneg (centeredPermutation p j))).mpr
    ⟨i, Finset.mem_univ i, sq_pos_of_ne_zero hi⟩

/-- Every permutation of `1, ..., n`, for `n ≥ 2`, has a strictly negative cyclic shift. -/
theorem centeredPermutation_exists_negative [NeZero n]
    (p : Equiv.Perm (Fin n)) (hn : 2 ≤ n) :
    ∃ k : Fin n, k ≠ 0 ∧ autocorrelation (centeredPermutation p) k < 0 :=
  exists_negative_autocorrelation _ (sum_centeredPermutation p)
    (centeredPermutation_nonzero p hn)

end CyclicCorrelation
end MathWiki
