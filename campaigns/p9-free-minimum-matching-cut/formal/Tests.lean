import Challenge
open P9FreeMinimumMatchingCut
example : cutWitness (⟨2, [(0,1)]⟩, 0) [false,true] = false := by native_decide
example : cutWitness (⟨2, [(0,1)]⟩, 1) [false,true] = true := by native_decide
