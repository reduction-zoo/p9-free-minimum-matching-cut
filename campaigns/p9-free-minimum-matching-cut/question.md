# 3P3-free Minimum Matching Cut → P9-free Minimum Matching Cut

Category: Complexity open

## Source

The source gives a connected graph with no induced disjoint union of three three-vertex paths, and a bound k. Its outputs are nonempty matching cuts of size at most k, or NO-SOLUTION.

## Target

Given a connected graph and integer k, ask for a nonempty matching cut of at most k edges, or NO-SOLUTION. The source excludes three disjoint induced three-vertex paths and the target excludes an induced nine-vertex path. This is a threshold problem, not an exact-optimum output contract.

## Required result

Construct deterministic polynomial-time maps F and G: F sends every legal source instance to a legal target instance, and G(x,y) is a valid source output for every valid output y of F(x). Preserve the stated threshold, domain and promises. The requested complexity conclusion is NP-hardness for the stated target problem.

## Acceptance

Give explicit construction and recovery algorithms, a general proof for every legal input and every valid target output, and polynomial runtime and encoding-size bounds. Specify finite output encodings and handle NO-SOLUTION outputs when applicable. Tests compare recovered source outputs with independent source solutions.

## Why it matters

The question refines the structural boundary for finding small matching separators.

## Difficulty

A gadget must control cut size as well as matching-cut feasibility and induced paths.

## Literature context

This question concerns a bound on the size of a matching cut, rather than existence alone. Results for other cut predicates do not resolve it.

Literature checked 2026-09-14. This summarizes the archived literature search on the date above. Unpublished, unindexed and overlooked work remains outside coverage; no new novelty assessment was performed.

## References

- [Finding Minimum Matching Cuts in H-free Graphs](https://arxiv.org/html/2502.18942v2): - R6: Finding Minimum Matching Cuts in H-free Graphs, v2, February 19, 2026, Theorem 17 and conclusion. The ordinary Matching Cut and Minimum Matching Cut statements are different.

Fixed from board record `website/questions/p9-free-minimum-matching-cut.json` in board checkout at 6c7d3bd9c0a8f595279969a9c0a4d1853a3f5c17; the record was copied from the current working tree.
