module

public import Mathlib.Data.ZMod.Basic
public import Mathlib.Logic.Relation
public import Mathlib.Data.Nat.GCD.Basic
import Lean.Elab.Tactic.Omega

/-!
# Intermediate values on periodic nearest-neighbour orbits

Source: conjecture 009, version 0.2, L4 and L5,
`conjectures/009-gcd-ring-return/conjectures.md`.

The source's threshold-propagation proof is formalized via a directed path on
the space-time torus. It only needs the two upper bounds `next ≤ parent + 1`.
Consequently the support of a periodic gcd-plus-one orbit has no internal gaps,
and containing 2 is equivalent to having support `{2, ..., M}`.
The general pair-pruning invariant and the diagonal-only exclusion criterion
are also proved. The concrete bound-1000 Python computation is not certified here.
This does NOT prove that a general periodic orbit contains 2 (conjecture 009).
Time and position are `ZMod p` and `ZMod n`; both moduli must be positive.
No finite computation or additional axioms are used.
-/

@[expose] public section

namespace MathWiki
namespace GcdRing

/-- Discrete intermediate values along a directed path whose upward jumps are at most one. -/
theorem exists_eq_of_reachable {α : Type*} {r : α → α → Prop}
    (f : α → ℕ) (hstep : ∀ a b, r a b → f b ≤ f a + 1)
    {a b : α} (hpath : Relation.ReflTransGen r a b) {k : ℕ}
    (ha : f a ≤ k) (hb : k ≤ f b) : ∃ c, f c = k := by
  induction hpath with
  | refl => exact ⟨a, Nat.le_antisymm ha hb⟩
  | @tail b c hab hbc ih =>
      by_cases hkb : k ≤ f b
      · exact ih hkb
      · have hbound := hstep b c hbc
        exact ⟨c, by omega⟩

variable {p n : ℕ} [NeZero p] [NeZero n]

private def causalEdge (a b : ZMod p × ZMod n) : Prop :=
  b = (a.1 + 1, a.2) ∨ b = (a.1 + 1, a.2 - 1)

omit [NeZero p] [NeZero n] in
private theorem reach_add_time (a : ZMod p × ZMod n) (k : ℕ) :
    Relation.ReflTransGen causalEdge a (a.1 + (k : ZMod p), a.2) := by
  induction k with
  | zero => simpa using (Relation.ReflTransGen.refl (r := causalEdge) (a := a))
  | succ k ih =>
      apply ih.tail
      left
      simp [Nat.cast_add, add_assoc]

omit [NeZero n] in
private theorem reach_time (a : ZMod p × ZMod n) (t : ZMod p) :
    Relation.ReflTransGen causalEdge a (t, a.2) := by
  have h := reach_add_time a (t - a.1).val
  simpa using h

omit [NeZero n] in
private theorem reach_left (a : ZMod p × ZMod n) :
    Relation.ReflTransGen causalEdge a (a.1, a.2 - 1) := by
  have hdiag : causalEdge a (a.1 + 1, a.2 - 1) := Or.inr rfl
  exact (Relation.ReflTransGen.single hdiag).trans
    (reach_time (a.1 + 1, a.2 - 1) a.1)

omit [NeZero n] in
private theorem reach_sub_position (a : ZMod p × ZMod n) (k : ℕ) :
    Relation.ReflTransGen causalEdge a (a.1, a.2 - (k : ZMod n)) := by
  induction k with
  | zero => simpa using (Relation.ReflTransGen.refl (r := causalEdge) (a := a))
  | succ k ih =>
      have h := ih.trans (reach_left (a.1, a.2 - (k : ZMod n)))
      simpa [Nat.cast_add, sub_sub] using h

private theorem reach_any (a b : ZMod p × ZMod n) :
    Relation.ReflTransGen causalEdge a b := by
  have hpos : Relation.ReflTransGen causalEdge a (a.1, b.2) := by
    simpa using reach_sub_position a (a.2 - b.2).val
  exact hpos.trans (reach_time (a.1, b.2) b.1)

/-- A doubly periodic nearest-neighbour array with no upward jumps larger than
one has no gaps in the union of its values. No gcd assumption is needed. -/
theorem periodic_intermediate_value (x : ZMod p → ZMod n → ℕ)
    (hself : ∀ t i, x (t + 1) i ≤ x t i + 1)
    (hright : ∀ t i, x (t + 1) i ≤ x t (i + 1) + 1)
    (ta tb : ZMod p) (ia ib : ZMod n) (k : ℕ)
    (ha : x ta ia ≤ k) (hb : k ≤ x tb ib) :
    ∃ t i, x t i = k := by
  have hedge : ∀ a b : ZMod p × ZMod n,
      causalEdge a b → x b.1 b.2 ≤ x a.1 a.2 + 1 := by
    intro a b hab
    rcases hab with h | h
    · subst b
      exact hself a.1 a.2
    · subst b
      simpa using hright a.1 (a.2 - 1)
  obtain ⟨c, hc⟩ := exists_eq_of_reachable (fun a => x a.1 a.2)
    hedge (reach_any (ta, ia) (tb, ib)) ha hb
  exact ⟨c.1, c.2, hc⟩

/-- The exact synchronous gcd-plus-one update on a periodic space-time torus. -/
def IsOrbit (x : ZMod p → ZMod n → ℕ) : Prop :=
  ∀ t i, x (t + 1) i = Nat.gcd (x t i) (x t (i + 1)) + 1

/-- Every integer between two values in a positive periodic gcd orbit occurs. -/
theorem orbit_intermediate_value (x : ZMod p → ZMod n → ℕ)
    (hx : IsOrbit x) (hpos : ∀ t i, 0 < x t i)
    (ta tb : ZMod p) (ia ib : ZMod n) (k : ℕ)
    (ha : x ta ia ≤ k) (hb : k ≤ x tb ib) :
    ∃ t i, x t i = k := by
  apply periodic_intermediate_value x ?_ ?_ ta tb ia ib k ha hb
  · intro t i
    rw [hx t i]
    exact Nat.add_le_add_right (Nat.gcd_le_left _ (hpos t i)) 1
  · intro t i
    rw [hx t i]
    exact Nat.add_le_add_right (Nat.gcd_le_right _ (hpos t (i + 1))) 1

omit [NeZero p] [NeZero n] in
/-- Positivity and periodicity make every value at least two. -/
theorem orbit_two_le (x : ZMod p → ZMod n → ℕ)
    (hx : IsOrbit x) (hpos : ∀ t i, 0 < x t i) (t : ZMod p) (i : ZMod n) :
    2 ≤ x t i := by
  have h := hx (t - 1) i
  have hg := Nat.gcd_pos_of_pos_left (x (t - 1) (i + 1)) (hpos (t - 1) i)
  simp only [sub_add_cancel] at h
  omega

/-- 009 and its former strengthening 009-1 are equivalent for an orbit whose
maximum `M` is attained: containing 2 already fills the whole interval. -/
theorem two_iff_interval_support (x : ZMod p → ZMod n → ℕ)
    (hx : IsOrbit x) (hpos : ∀ t i, 0 < x t i) (M : ℕ)
    (hupper : ∀ t i, x t i ≤ M) (hmax : ∃ t i, x t i = M) :
    (∃ t i, x t i = 2) ↔
      ∀ k : ℕ, (∃ t i, x t i = k) ↔ 2 ≤ k ∧ k ≤ M := by
  constructor
  · rintro ⟨ta, ia, ha⟩ k
    constructor
    · rintro ⟨t, i, rfl⟩
      exact ⟨orbit_two_le x hx hpos t i, hupper t i⟩
    · rintro ⟨hk, hM⟩
      obtain ⟨tb, ib, hb⟩ := hmax
      apply orbit_intermediate_value x hx hpos ta tb ia ib k
      · omega
      · omega
  · intro h
    apply (h 2).mpr
    obtain ⟨t, i, hi⟩ := hmax
    have htwo := orbit_two_le x hx hpos t i
    exact ⟨le_rfl, by omega⟩

/-- One exact round of pair pruning: retain a pair only when it has a
predecessor triple whose two overlapping pairs are also admitted. -/
def prunePairs (E : ℕ → ℕ → Prop) (c d : ℕ) : Prop :=
  E c d ∧ ∃ a b e, E a b ∧ E b e ∧
    c = Nat.gcd a b + 1 ∧ d = Nat.gcd b e + 1

omit [NeZero p] [NeZero n] in
/-- Every pruning round preserves all pairs of a periodic orbit.
This is the soundness argument of the bounded-alphabet certificate, not an
assertion that pruning terminates for every alphabet. -/
theorem orbit_pairs_mem_prune (x : ZMod p → ZMod n → ℕ)
    (hx : IsOrbit x) (E : ℕ → ℕ → Prop)
    (hE : ∀ t i, E (x t i) (x t (i + 1))) :
    ∀ t i, prunePairs E (x t i) (x t (i + 1)) := by
  intro t i
  refine ⟨hE t i, x (t - 1) i, x (t - 1) (i + 1),
    x (t - 1) (i + 1 + 1), hE (t - 1) i, hE (t - 1) (i + 1), ?_, ?_⟩
  · simpa using hx (t - 1) i
  · simpa using hx (t - 1) (i + 1)

omit [NeZero p] [NeZero n] in
/-- Pair preservation holds after any finite number of exact pruning rounds. -/
theorem orbit_pairs_mem_prune_iterate (x : ZMod p → ZMod n → ℕ)
    (hx : IsOrbit x) (E : ℕ → ℕ → Prop)
    (hE : ∀ t i, E (x t i) (x t (i + 1))) (r : ℕ) :
    ∀ t i, (prunePairs^[r] E) (x t i) (x t (i + 1)) := by
  induction r with
  | zero => exact hE
  | succ r ih =>
      simpa only [Function.iterate_succ_apply'] using
        orbit_pairs_mem_prune x hx (prunePairs^[r] E) ih

omit [NeZero n] in
/-- A periodic gcd-plus-one orbit cannot have equal adjacent values at all times. -/
theorem not_isOrbit_of_diagonal (x : ZMod p → ZMod n → ℕ)
    (hdiag : ∀ t i, x t i = x t (i + 1)) : ¬IsOrbit x := by
  intro hx
  have hinc (t : ZMod p) (i : ZMod n) : x (t + 1) i = x t i + 1 := by
    rw [hx t i, ← hdiag t i, Nat.gcd_self]
  have hlinear (k : ℕ) : x (0 + (k : ZMod p)) 0 = x 0 0 + k := by
    induction k with
    | zero => simp
    | succ k ih =>
        have h := hinc (0 + (k : ZMod p)) 0
        calc
          x (0 + ((k + 1 : ℕ) : ZMod p)) 0 = x (0 + (k : ZMod p)) 0 + 1 := by
            simpa [Nat.cast_add, add_assoc] using h
          _ = x 0 0 + (k + 1) := by rw [ih]; omega
  have h := hlinear p
  simp only [ZMod.natCast_self, add_zero] at h
  have hp := NeZero.ne p
  omega

omit [NeZero n] in
/-- A diagonal-only pruning result excludes every periodic orbit whose pairs
were initially admitted. The concrete alphabet certificate remains separate. -/
theorem not_isOrbit_of_prune_diagonal (x : ZMod p → ZMod n → ℕ)
    (E : ℕ → ℕ → Prop) (hE : ∀ t i, E (x t i) (x t (i + 1))) (r : ℕ)
    (hdiag : ∀ a b, (prunePairs^[r] E) a b → a = b) : ¬IsOrbit x := by
  intro hx
  apply not_isOrbit_of_diagonal x ?_ hx
  intro t i
  exact hdiag _ _ (orbit_pairs_mem_prune_iterate x hx E hE r t i)

end GcdRing
end MathWiki
