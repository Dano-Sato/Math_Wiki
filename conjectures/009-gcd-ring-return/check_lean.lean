import MathWiki

/-!
Public-import and assumption checks for 009 v0.2.
The finite example below is the original three-cell, period-three orbit.
Its `decide` proofs only certify that explicitly bounded example.
The general theorems are proved in MathWiki.Dynamics.GcdRing.
-/

open MathWiki.GcdRing

def threeCycle (t i : ZMod 3) : ℕ :=
  if i = t - 1 then 3 else 2

example : IsOrbit threeCycle := by unfold IsOrbit; decide

example : ∀ t i, 0 < threeCycle t i := by decide

example : ∀ k : ℕ, (∃ t i, threeCycle t i = k) ↔ 2 ≤ k ∧ k ≤ 3 := by
  apply (two_iff_interval_support threeCycle (by unfold IsOrbit; decide) (by decide) 3
    (by decide) (by decide)).mp
  decide

example {p n : ℕ} [NeZero p] [NeZero n]
    (x : ZMod p → ZMod n → ℕ) (hx : IsOrbit x)
    (hpos : ∀ t i, 0 < x t i) (M : ℕ)
    (hupper : ∀ t i, x t i ≤ M) (hmax : ∃ t i, x t i = M)
    (htwo : ∃ t i, x t i = 2) :
    ∀ k : ℕ, (∃ t i, x t i = k) ↔ 2 ≤ k ∧ k ≤ M :=
  (two_iff_interval_support x hx hpos M hupper hmax).mp htwo

#print axioms exists_eq_of_reachable
#print axioms periodic_intermediate_value
#print axioms orbit_intermediate_value
#print axioms orbit_two_le
#print axioms two_iff_interval_support
#print axioms orbit_pairs_mem_prune
#print axioms orbit_pairs_mem_prune_iterate
#print axioms not_isOrbit_of_diagonal
#print axioms not_isOrbit_of_prune_diagonal
