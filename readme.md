# Conditional Predicate Implications

There is a ground set $U$.
There is a set $Φ$ of predicates on $U$ (functions from $U$ to `bool`).
We are given a set of implications, i.e., results of the form
$a(u) ⟹ b(u) ∀ u ∈ U$, where $a, b ∈ Φ$.
We would like to infer more predicate implications using transitive closure
and then display all such predicate implications (ideally as a Hasse diagram).

This is useful to visualize, e.g., implications between fairness notions
in [fair allocation](https://en.wikipedia.org/wiki/Fair_division).
Here the ground set is the set of all allocations across all fair division instances,
and the predicates are fairness notions.

We look at a more complicated version of this problem, where the implications are conditional.
Formally, we are given a set family $Σ ⊆ 2^U$.
Each implication of the form $a(u) ⟹ b(u) ∀ u ∈ S$, where $a, b ∈ Φ$ and $S ∈ Σ$.

This finds applications in fair allocation since many results are conditional,
i.e., envy-freeness implies proportionality only for sub-additive valuations.
We would like to infer all conditional predicates using transitive closure,
and given a set $S ∈ Σ$, display all predicate implications conditional on $S$.