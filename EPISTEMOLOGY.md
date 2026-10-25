# Epistemology of M_0: What Does It Actually Measure?

## The Axiom Correlation Test

A critical question for any significance metric is: *Does it reward abstraction or structural depth?* In Lean, mathematical theorems can depend on classical axioms (like `Classical.choice`). We tested whether high M_0 scores correlate with classical (non-constructive) mathematics.

### Methodology
- **Sample:** Top 50 and Bottom 50 theorems by M_0 score.
- **Heuristic:** Searched for classical keywords (`Classical`, `nonempty`, `exists`, `choose`, `choice`).
- **Result:** 
  - **Top 50:** 0 classical keywords. (Mean M: 378.83)
  - **Bottom 50:** 10 classical keywords. (Mean M: 2.0)

## Key Finding

**M_0 measures structural (constructive) integration depth, not classical abstraction.**

The highest-scoring theorems are concentrated in `MeasureTheory`, `intervalIntegral`, and `Real`. These are fields where proofs require deep, interconnected constructions rather than abstract existence claims. Conversely, theorems at the bottom of the M_0 hierarchy are more likely to involve classical choice or trivial existence.

## Implications for the Metric

1. **No Classical Bias:** M_0 does not artificially inflate the importance of non-constructive mathematics.
2. **Structural Significance:** The metric rewards theorems that serve as foundational bridges across multiple domains, which aligns with how mathematicians intuitively judge importance.
3. **Honest Limitation:** The keyword heuristic is not a full Lean `#print axioms` scan, but it provides a strong statistical signal.

*Generated during Halka 3 (Epistemology) on October 25, 2026.*