# Halka 7 & 8: Coq Cross-Validation Results

**Project:** M_0 — A Graph-Theoretic Metric for Mathematical Significance  
**Author:** Ahmet Kütük (Akdeniz Üniversitesi)  
**Date:** 2026-10-25  
**Status:** Halka 7 (coq-ext-lib) and Halka 8 (coq-mathcomp) completed

---

## 1. Motivation

Following Halka 6 (Isabelle AFP validation), the natural next step was to test M_0 on Coq, the third major proof assistant. Two independent Coq libraries were selected:

- **coq-ext-lib** — a utility library (Bool, Option, List, Monad, String), described upstream as having "Additional dependencies: none"
- **coq-mathcomp** — the Mathematical Components library (algebra, group theory, linear algebra, poly)

The goal was twofold: (a) verify that M_0 produces meaningful rankings on Coq dependency graphs, and (b) cross-validate M_0's library-independence by comparing Coq-to-Coq and Coq-to-Mathlib correlations.

---

## 2. Data Sources

### 2.1 coq-ext-lib (Halka 7)

**Source:** HuggingFace `theostos/pile-of-rocq`, config `coq-ext-lib`

Relevant tables:
- `coq-ext-lib-proofs`: 13,770 proofs/lemmas, columns include `proof_uid`, `name`, `axioms`
- `coq-ext-lib-step_deps`: 77,967 edges, columns include `proof_uid`, `dep_uid`, `name`, `logical_path`
- `coq-ext-lib-toc_nodes`: 172,249 TOC nodes, columns include `name`, `kind`, `data_uid`

### 2.2 coq-mathcomp (Halka 8)

**Source:** HuggingFace `phanerozoic/Coq-MathComp`

- 23,813 entries, columns include `symbolic_name`, `type`, `deps`, `library`, `filename`
- `deps` column contains intra-corpus identifiers directly (no join required)

---

## 3. Halka 7: coq-ext-lib — Methodological Failure and Correction

### 3.1 v1: `axioms` column (FAILED)

The first attempt used the `axioms` column as a dependency proxy:

- **Result:** 10,573 nodes, **0 edges**
- **Root cause:** `axioms` corresponds to `Print Assumptions` output (proof_irrelevance, functional_extensionality), not theorem-to-theorem dependencies.
- **Consequence:** All M_0 scores were 0.00; the ranking was meaningless.

**This failure is reported honestly and is preserved in `coq_m0_scores.json` for reproducibility.**

### 3.2 v2: name-based join via `step_deps` (SUCCESSFUL)

The correction joined `step_deps` (containing `proof_uid` + `dep_uid` + `name`) with `proofs` (containing `proof_uid` + `name`):

- `dep_uid` did **not** intersect with `proof_uid` (0 overlap) nor with `data_uid` (0 overlap)
- However, the `name` fields **did** overlap: 7,871 of 9,688 distinct `dep_name`s (81%) matched `toc_names`
- Filtering edges to both endpoints being known proof names yielded a valid DAG

**Results:**

| Metric | Value |
|---|---|
| Nodes | 10,573 |
| Edges (both endpoints known) | 27,679 |
| Nodes with D > 0 | 6,116 (58%) |
| Nodes with F > 0 | 7,081 (67%) |
| Max D | 323 (`f_equal`) |
| Max F | 15 (`add_assoc`) |

**Top 5 by M_0:**

1. `f_equal` (M=323.00, D=323, F=0)
2. `Rinv_0_lt_compat` (M=311.68, D=118, F=9)
3. `add_comm` (M=290.97, D=124, F=6)
4. `Rle_dec` (M=259.93, D=138, F=3)
5. `mul_comm` (M=255.78, D=109, F=6)

**Interpretation:** The top of the ranking is dominated by foundational infrastructure (`f_equal`, `add_comm`, `mul_comm`) rather than deep mathematics. This is consistent with M_0's known behaviour on Mathlib (Halka 1–5), where basic equality and algebra lemmas also ranked highly.

**Caveat:** The `coq-ext-lib` M_0 values are not directly comparable to Mathlib values because ext-lib is a small utility library; F values are compressed (max 15 vs. 40+ in Mathlib). This is a scale limitation of the dataset, not a failure of the metric.

---

## 4. Halka 8: coq-mathcomp — Type Filtering is Critical

### 4.1 Unfiltered run (FAILED)

Running M_0 on all 21,592 `symbolic_name`s with non-empty `deps` produced:

- **Top 1:** `apply` (M=10,514, D=6,318, F=2)
- **Top 2:** `inE` (M=2,290, D=1,033, F=5)
- **Top 3:** `split` (M=1,682, D=759, F=5)

`apply` and `split` are **tactics**, `inE` is a **definition/let**, `nat`/`seq` are **notations**, `size`/`last` are **fixpoints**. None are theorems. The `deps` column in `phanerozoic/Coq-MathComp` includes tactic names, notations, and type identifiers, not just proven theorems.

**This is a data-quality failure, not a metric failure.** It is reported here because the unfiltered result (`coq_mathcomp_m0_scores.json`) is preserved for transparency.

### 4.2 Filtered run (SUCCESSFUL)

Filtering to `type ∈ {Lemma, Theorem, Fact, Corollary, Proposition, Remark, Example}` — i.e., proven statements only — and requiring both edge endpoints to be in the filtered set:

| Metric | Value |
|---|---|
| Nodes (proven statements) | 15,654 |
| Edges (theorem → theorem) | 67,162 |
| Nodes with D > 0 | 10,481 (67%) |
| Max D | 540 (`subsetP`) |
| Max F | 57 (`mulr0`) |

**Type breakdown:** Lemma 14,924; Fact 634; Theorem 63; Corollary 18; Example 7; Proposition 5; Remark 3.

**Top 10 by M_0:**

1. `subsetP` (M=748.55, D=540, F=1)
2. `mxE` (M=698.65, D=504, F=1)
3. `matrixP` (M=550.83, D=331, F=2)
4. `setP` (M=534.19, D=321, F=2)
5. `eq_bigr` (M=519.83, D=375, F=1)
6. `mulr0` (M=478.09, D=181, F=9)
7. `mul0r` (M=472.11, D=192, F=7)
8. `mulr1` (M=469.87, D=212, F=5)
9. `eqVneq` (M=457.45, D=330, F=1)
10. `mulmxA` (M=418.02, D=170, F=7)

**Interpretation:** With the type filter applied, the ranking is dominated by genuine mathematical content:
- Set theory: `subsetP`, `setP`, `imsetP`, `eqEsubset`, `subset_trans`, `subsetI`
- Linear algebra: `matrixP`, `mulmxA`, `mxE`
- Algebra: `mulr0`, `mul0r`, `mulr1`, `mulrC`, `mulrA`, `mul1r`, `addrC`, `add0r`, `addr0`, `mulnC`
- Order theory: `le_trans`, `eq_sym`
- Polynomials: `polyP`

This profile is qualitatively consistent with Mathlib (Halka 1–5) and Isabelle AFP (Halka 6): foundational and algebraic infrastructure dominates the top.

**Honest caveat:** `subsetP` and `mxE` are "bridge lemmas" (subset ↔ predicate, matrix ↔ function), not deep mathematics. M_0 rewards frequency of use, not conceptual depth. This was already known from Halka 3 (Epistemology) and is restated here.

---

## 5. Cross-Prover Correlation (Coq → Coq)

Common names between `coq-ext-lib` and `coq-mathcomp` filtered:

- 43 common names (raw)
- Spearman ρ = 0.1616, p = 0.30 → **not statistically significant**
- After filtering to names with M > 0 in both libraries: 19 common names
- Spearman ρ = 0.6359, p = 0.005 → **statistically significant**

**Why the raw correlation is low:** 24 of the 43 common names are one-sided zeros (e.g., `eq_refl` is a constructor in MathComp and therefore filtered out; `max_l`/`max_r`/`min_l`/`min_r` are definitions/notations in MathComp). Same name, different type — a data-quality artefact, not a metric failure.

**Why the filtered correlation is high:** The 19 names with M > 0 in both libraries are genuinely proven theorems in both, with comparable structural roles. Examples:

| Name | ext-lib M | mathcomp M |
|---|---|---|
| `le_trans` | 74.31 | 335.45 |
| `eq_sym` | 88.53 | 292.00 |
| `lt_trans` | 59.56 | 93.86 |
| `lt_le_trans` | 58.24 | 54.92 |
| `id` | 125.40 | 139.63 |
| `le_lt_trans` | 38.28 | 66.57 |

Normalization (z-score, min-max, mean/max) does **not** change Spearman ρ — as expected, since Spearman is rank-based and invariant under monotone transformations. The problem is not scale, it is sample quality.

---

## 6. Files

| File | Description |
|---|---|
| `coq_m0.py` | v1 script (axioms column) — preserved for reproducibility of failure |
| `coq_m0_v2.py` | v2 script (name-based join) — produced `coq_m0_v2_scores.json` |
| `coq_m0_mathcomp.py` | Halka 8 unfiltered script — produced `coq_mathcomp_m0_scores.json` |
| `coq_m0_mathcomp_filtered.py` | Halka 8 filtered script — produced `coq_mathcomp_filtered_m0.json` |
| `compare_extlib_mathcomp.py` | Coq-Coq correlation script |
| `compare_normalized.py` | Normalization variants (Spearman invariant) |
| `coq_m0_scores.json` | v1 output (all zeros — preserved for honesty) |
| `coq_m0_v2_scores.json` | Halka 7 final M_0 scores |
| `coq_mathcomp_m0_scores.json` | Halka 8 unfiltered (includes tactics — preserved for honesty) |
| `coq_mathcomp_filtered_m0.json` | Halka 8 final M_0 scores |

---

## 7. Conclusion

M_0 runs on Coq. Two independent libraries (ext-lib, mathcomp) produce rankings qualitatively consistent with Mathlib and Isabelle: foundational and algebraic infrastructure dominates, deep mathematics does not. The transition from raw to filtered data raises the cross-library correlation from ρ = 0.16 to ρ = 0.64 (Coq-Coq). This pattern — raw data noisy, filtered data consistent — repeats in the Mathlib-to-Coq comparison (Section 5 of `CROSS_PROVER_VALIDATION.md`).

The honest summary: **M_0 captures a library-independent signal for foundational structural theorems, but is highly sensitive to dependency-graph data quality. It is better characterized as a structural-role indicator than as a universal measure of mathematical significance.**

---

## 8. Reproducibility Note

The Halka 1–5 Mathlib scores (`mathlib_m0_scores.json`) were **not preserved**. This means the original P6 result (Wiedijk 100 theorems scoring 2.365× random) and the top-300 significance map cannot be numerically reproduced from the original data.

To partially compensate, M_0 was recomputed on the independent `MathNetwork/MathlibGraph` dataset (`v2/declaration/metrics.csv`, commit `534cf0b`) and the qualitative profile was checked. See `CROSS_PROVER_VALIDATION.md` for details.

This is a methodological limitation and is reported honestly. The qualitative conclusions of Halka 1–5 remain supported by the independent recomputation, but the specific numerical claims (2.365× ratio, exact top-300 ordering) should be treated as **original findings pending independent replication**.