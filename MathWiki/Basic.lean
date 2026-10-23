module

public import Mathlib.Data.Finset.Card

/-!
# Finite counting foundations

Small infrastructure for counting objects satisfying a decidable property.
These are elementary wrappers around Mathlib, not original research results.
-/

@[expose] public section

namespace MathWiki

variable {α : Type*}

/-- Number of elements of a finite set satisfying `p`. -/
def countWhere (s : Finset α) (p : α → Prop) [DecidablePred p] : ℕ :=
  (s.filter p).card

/-- Filtering a finite set cannot increase its cardinality. -/
theorem countWhere_le_card (s : Finset α) (p : α → Prop) [DecidablePred p] :
    countWhere s p ≤ s.card :=
  Finset.card_le_card (Finset.filter_subset _ _)

@[simp]
theorem countWhere_true (s : Finset α) : countWhere s (fun _ => True) = s.card := by
  simp [countWhere]

@[simp]
theorem countWhere_false (s : Finset α) : countWhere s (fun _ => False) = 0 := by
  simp [countWhere]

end MathWiki
