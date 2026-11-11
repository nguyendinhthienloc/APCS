# Forgets to return v to the parent after finishing a subtree in α-β

While tracing the 4-ply practice tree (Lesson 6), the student went down the tree correctly but forgot to pass each finished node's value back up and update the parent's v and α/β. Without that step, sibling subtrees inherit stale bounds and the cuts come out wrong. They earlier assumed α-β could be done row by row, like minimax, so the down-then-up rhythm of depth-first recursion is not automatic yet.

**Implications**: Drill the per-node routine (enter → children → return v → parent updates). In future trees, check traces specifically for missing "return" steps. Keep "back up / return" (α-β) separate from "back-propagation" (MCTS) in the wording, since the names are close.
