# M_0: A Graph-Theoretic Metric for Mathematical Significance in Mathlib

**Ahmet Kutuk**  
**DOI:** [10.5281/zenodo.23630551](https://doi.org/10.5281/zenodo.23630551)
*Akdeniz University*  
*October 25, 2026*

## Abstract

As formal mathematics libraries like Lean's Mathlib grow beyond 270,000 theorems, identifying the most structurally significant results becomes crucial for both researchers and automated theorem provers. We introduce M_0, a significance metric derived from the dependency graph of Mathlib. M_0 combines dependency depth (D) and in-field diversity (F) to assign an importance score to every theorem. We validate M_0 against three hypotheses: P1 (important theorems score higher than basic ones), P5 (novelty correlation, which we refute), and P6 (Wiedijk's 100 theorems score 2.365× higher than random theorems). Furthermore, we present a Discovery Engine that identifies missing Wiedijk theorems and a graph-based topology of the deepest mathematical infrastructure in Mathlib.

## 1. Introduction

The formalization of mathematics in proof assistants has reached a scale where manual curation of theorem importance is no longer feasible. Mathlib, the primary library for Lean 4, contains over 272,000 theorems. Which ones are foundational? Which ones represent the deepest mathematical insights? We propose M_0, a metric that uses the topological structure of the dependency graph to answer these questions objectively.

## 2. Methodology

The M_0 score is defined as:
M(S) = D(S) × √(1+F(S)) × e^(-F(S)/50)

- **D(S)**: The longest path in the dependency DAG starting from S (measuring structural depth).
- **F(S)**: The number of distinct mathematical fields that depend on S (measuring in-field diversity).
- **Filtering**: Trivial dependencies (e.g., `inst*`, `.to*`, `Lean.*`) are excluded to prevent inflation.

## 3. Validation

We tested M_0 against three independent hypotheses:
- **P1 (Importance):** Supported. High M_0 scores correlate with foundational mathematical theorems (e.g., Fermat's Little Theorem scores approximately 3 times higher than basic arithmetic lemmas).
- **P5 (Novelty):** Refuted. Git commit age does not correlate with M_0 (ratio: 1.008). M_0 measures importance, not recency.
- **P6 (External Validation):** Supported. The 41 theorems from Wiedijk's "100 Theorems" list that exist in Mathlib score an average of 2.4 times higher M_0 than random theorems (M=127 vs 54). This provides the first external validation of the metric.

## 4. Discovery Engine and Missing Theorems

We analyzed the M_0 neighborhood of the missing Wiedijk 100 theorems. 
- **Central Limit Theorem:** Initially flagged as missing with high readiness (M approximately 417). Correction: A manual check revealed CLT was already formalized in Mathlib. This highlights a limitation of graph-based discovery: absence of evidence is not evidence of absence.
- **Puiseux's Theorem:** Identified as genuinely missing but viable for formalization (neighborhood M approximately 263). A formalization request has been submitted to the Mathlib community (Issue #45264).
- **Geometry Theorems (Ceva, Morley, Pick):** Flagged as missing with low readiness (M approximately 272), suggesting the Euclidean geometry infrastructure needs expansion first.

## 5. Epistemology: What Does M_0 Measure?

To determine if M_0 rewards abstraction or structural depth, we analyzed the classical axiom dependency of the Top 50 and Bottom 50 theorems.
- **Top 50:** 0 theorems contained classical choice keywords (Mean M: 378.83).
- **Bottom 50:** 10 theorems contained classical choice keywords (Mean M: 2.0).
- **Conclusion:** M_0 measures structural (constructive) integration depth, not classical abstraction. The highest-scoring theorems are concentrated in MeasureTheory and intervalIntegral, reflecting the deep, interconnected nature of integration theory.

## 6. Conclusion and Future Work

M_0 successfully maps the structural hierarchy of Mathlib, validates against external benchmarks (Wiedijk 100), and identifies missing infrastructure. The visualization of the Top 300 theorems reveals a dense core of measure theory and analysis. Future work includes applying M_0 to other proof assistants (Isabelle, Coq) and automating the Discovery Engine for real-time missing theorem detection.

## References
1. Wiedijk, F. The Seventeen Provers of the World. Springer, 2006.
2. Mathlib Community. Mathlib4. GitHub repository.
3. MathNetwork. MathlibGraph Dataset. HuggingFace.

---
*AI Disclosure: This whitepaper was drafted with AI assistance for structuring and language editing. All data, analysis, and validation results are original outputs of the M_0 project and were verified by the author.*