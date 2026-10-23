module

import MathWiki

/-!
Public API and source-convention checks for 013, version 0.1.
Run from the repository root:
  .\scripts\lake.ps1 env lean -DwarningAsError=true conjectures/013-nonpositive-cyclic-correlation/check_lean.lean
-/

open MathWiki.CyclicCorrelation
open scoped BigOperators

-- The source's permutation (5, 4, 2, 3, 1), with labels reduced by one.
private def sourceExample : Equiv.Perm (Fin 5) where
  toFun i := match i.val with
    | 0 => 4
    | 1 => 3
    | 2 => 1
    | 3 => 2
    | _ => 0
  invFun i := match i.val with
    | 0 => 4
    | 1 => 2
    | 2 => 3
    | 3 => 1
    | _ => 0
  left_inv := by decide
  right_inv := by decide

example : autocorrelation (centeredPermutation sourceExample) 1 = -12 := by decide
example : autocorrelation (centeredPermutation sourceExample) 2 = -8 := by decide

example {n : ℕ} [NeZero n] (p : Equiv.Perm (Fin n)) (hn : 2 ≤ n) :
    ∃ k : Fin n, k ≠ 0 ∧ autocorrelation (centeredPermutation p) k < 0 :=
  centeredPermutation_exists_negative p hn

example {G : Type*} [AddCommGroup G] [Fintype G] (x : G → ℤ)
    (hzero : ∑ i, x i = 0) (hne : ∃ i, x i ≠ 0) :
    ∃ k, k ≠ 0 ∧ autocorrelation x k < 0 :=
  exists_negative_autocorrelation x hzero hne

#print axioms sum_autocorrelation
#print axioms autocorrelation_neg
#print axioms sum_nonzero_autocorrelation
#print axioms exists_negative_autocorrelation
#print axioms sum_centeredPermutation
#print axioms centeredPermutation_nonzero_sum_neg
#print axioms centeredPermutation_exists_negative
