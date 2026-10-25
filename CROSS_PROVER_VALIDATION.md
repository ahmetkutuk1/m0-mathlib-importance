# Cross-Prover Validation of M_0

**Project:** M_0 — A Graph-Theoretic Metric for Mathematical Significance  
**Author:** Ahmet Kütük (Akdeniz Üniversitesi)  
**Date:** 2026-10-25

---

## 1. Purpose

M_0 was originally proposed and validated on Mathlib (Ring 1–5). Its universality claim rests on whether the same formula produces consistent rankings across different proof assistants and libraries. This document summarises all cross-prover tests performed to date.

---

## 2. Datasets

| Dataset | Prover | Nodes | Edges | Source |
|---|---|---|---|---|
| Mathlib (original, Ring 1–5) | Lean 4 | ~272K | ~8.4M | Original extraction (**scores lost**) |
| Isabelle AFP (Ring 6) | Isabelle | — | — | `afp_m0_scores.json` |
| coq-ext-lib (Ring 7) | Coq | 10,573 | 27,679 | `pile-of-rocq` v2 |
| coq-mathcomp (Ring 8) | Coq | 15,654 | 67,162 | `phanerozoic/Coq-MathComp`, filtered |
| MathNetwork MathlibGraph (independent) | Lean 4 | 308,129 | 8,436,366 | `MathNetwork/MathlibGraph`, commit `534cf0b` |

---

## 3. Cross-Prover Correlation Table

| Comparison | Common names | Spearman ρ (raw) | Spearman ρ (filtered) | Notes |
|---|---|---|---|---|
| Coq ext-lib ↔ Coq mathcomp | 43 → 19 | 0.16 (p=0.30) | **0.64 (p=0.005)** | Filter: M>0 on both sides |
| Mathlib (independent) ↔ Coq mathcomp | 16 → 12 | 0.34 | **0.58** | Filter: M>0 on both sides |
| Mathlib (independent) ↔ Coq ext-lib | — | — | — | Not computed (very small overlap expected) |
| Isabelle AFP ↔ any | — | — | — | Single-library; no cross-library overlap available |

**Key observation:** In both comparisons, the raw correlation is weak, but filtering to names with non-zero M in both libraries raises the correlation to ρ ≈ 0.6. This pattern is consistent across two independent cross-library comparisons.

---

## 4. Qualitative Pattern (Consistent Across Libraries)

Across Mathlib, Isabelle AFP, coq-ext-lib, and coq-mathcomp, the top of the M_0 ranking is dominated by:

1. **Foundational logic / equality:** `f_equal`, `eq_sym`, `Eq.trans`, `congr`
2. **Order / set theory:** `le_trans`, `lt_trans`, `subsetP`, `setP`, `subset_trans`
3. **Algebraic infrastructure:** `add_comm`, `mul_comm`, `mulr0`, `mulr1`, `mulrC`
4. **Bridges (frequent but shallow):** `subsetP`, `mxE`, `eq_bigr`

Deep mathematics (analysis, geometry, number theory) appears far below the top. This is consistent with M_0's known behaviour (Ring 3 — Epistemology: M_0 rewards structural/constructive analysis, not classical abstraction).

---

## 5. Mathlib Independent Replication (MathNetwork)

The `MathNetwork/MathlibGraph` dataset provides an independently extracted Mathlib dependency graph (commit `534cf0b`, 2 February 2026), with `in_degree`, `out_degree`, `pagerank`, `betweenness` precomputed.

M_0 was recomputed on this graph using `D = in_degree` and `F = out_degree`.

### 5.1 Key finding: synthesized edges dominate

The MathNetwork graph includes **compiler-synthesized edges** (typeclass resolution, coercions, instance projections). The original Ring 1–5 extraction likely included only explicit dependencies. This difference has a large effect:

**Unfiltered Top 5 (all kinds):**

1. `Semiring.toNonAssocSemiring` [abbrev] — M=155,733, D=56,019
2. `OfNat.ofNat` [abbrev] — M=124,670, D=89,936
3. `DFunLike.coe` [abbrev] — M=108,896, D=65,437
4. `Membership.mem` [abbrev] — M=105,722, D=63,530
5. `Semiring.toMonoidWithZero` [abbrev] — M=93,373, D=30,397

**Filtered Top 5 (theorem only):**

1. `of_eq_true` — M=81,212, D=48,801
2. `Eq.trans` — M=58,686, D=58,686
3. `eq_self` — M=48,487, D=34,978
4. `congrFun'` — M=45,516, D=45,516
5. `Eq.symm` — M=42,542, D=42,542

Even after filtering to theorems, the top is still dominated by foundational equality infrastructure. This is qualitatively consistent with the original Ring 1–5 finding (that M_0 rewards foundational structural lemmas), but the specific ordering differs from what was originally reported.

### 5.2 Honest limitation

The original Ring 1–5 scores are **lost**. The MathNetwork recomputation produces a qualitatively similar profile but cannot reproduce the specific numerical claims (P6 = 2.365×, exact top-300 ordering). These should be treated as original findings pending independent replication.

---

## 6. Interpretation

### 6.1 What M_0 measures

M_0 measures **structural role in a dependency graph**. It rewards:

- High in-degree (many theorems depend on this one)
- Moderate out-degree (this one depends on a few things)
- Penalizes high out-degree (heavily dependent on others)

This is a **structural centrality** measure, not a measure of mathematical depth. Basic equality lemmas, order lemmas, and algebraic identities dominate because they are used everywhere. Deep theorems (e.g., the Fundamental Theorem of Calculus, the Prime Number Theorem) have low in-degree and do not appear at the top.

### 6.2 What M_0 does not measure

M_0 does **not** measure:

- Conceptual depth or mathematical significance in the human sense
- Historical importance or pedagogical value
- Difficulty of proof
- Generality or abstraction level

### 6.3 Data quality sensitivity

M_0 is **highly sensitive** to:

- Whether synthesized edges are included (MathNetwork vs. original Ring 1–5)
- Whether non-theorem nodes (tactics, notations, definitions, constructors) are filtered
- Whether name matching is type-aware (the `eq_refl` problem in Coq-Coq comparison)

This sensitivity is not a flaw of the metric per se, but a limitation on its applicability: **M_0 requires a clean, theorem-only dependency graph to produce meaningful cross-library comparisons.**

---

## 7. Conclusion

Across four datasets (Mathlib original, Isabelle AFP, coq-ext-lib, coq-mathcomp) and two independent cross-library comparisons (Coq-Coq, Mathlib-Coq), M_0 exhibits:

1. **Consistent qualitative pattern:** foundational logic, order theory, and algebraic infrastructure at the top; deep mathematics below.
2. **Weak raw cross-library correlation** (ρ ≈ 0.16–0.34), but **strong filtered correlation** (ρ ≈ 0.58–0.64) when non-theorem nodes and one-sided zeros are removed.
3. **High sensitivity to data quality:** synthesized edges, tactic/notation nodes, and name-type mismatches all distort the ranking.

**Honest positioning:** M_0 is a **structural-role indicator** for formal library dependency graphs, not a universal measure of mathematical significance. Its cross-library consistency (ρ ≈ 0.6 on clean data) supports its use as a diagnostic tool for identifying foundational infrastructure, but its sensitivity to data quality means it cannot be applied naively to heterogeneous dependency graphs.

---

## 8. Limitations and Future Work

1. **Sample size:** Cross-library comparisons used 12–19 common names. This is a pilot-scale result; larger overlap is needed for robust statistical claims.
2. **Lost scores:** Ring 1–5 Mathlib scores were not preserved. Independent recomputation is qualitatively consistent but not numerically identical.
3. **Synthesized edges:** The effect of compiler-synthesized edges on M_0 has not been systematically quantified.
4. **Alternative centrality measures:** `pagerank`, `betweenness`, and `dag_layer` are available in MathNetwork and could be compared with M_0's D×F formulation in future work.
5. **Domain-specific weighting:** A domain-aware M_0 (e.g., weighting by module or namespace) might reduce the dominance of foundational infrastructure and surface domain-specific depth.

---

## 9. Files

See `COQ_RESULTS.md` Section 6 for the full file list. Key files:

- `coq_m0_v2_scores.json` — Ring 7 final scores
- `coq_mathcomp_filtered_m0.json` — Ring 8 final scores
- `mathlib_m0_independent.json` — Independent MathNetwork recomputation
- `compare_extlib_mathcomp.py` — Coq-Coq correlation
- `compare_mathlib_mathcomp.py` — Mathlib-Coq correlation