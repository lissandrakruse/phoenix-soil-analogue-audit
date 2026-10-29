# Validation record — 2026-10-29

- All six notebook code cells passed twice via sequential Python execution. This is not a Jupyter-kernel/Kaggle execution claim.
- All nine EDA tests passed; 25 deterministic EDA output files reproduced byte-for-byte.
- Profile tests passed: positivity/missing endpoint rules, depth strata, unique cohort/sample keys, scale/permutation invariance, pairwise-logratio identity and deterministic 12-decimal rank policy.
- Independent reviewer recomputed all 124,117 distances in 64 groups with the equivalent pairwise-logratio formula: maximum absolute discrepancy 1.78e-15. Sample and pedon ranks matched exactly under the documented tie policy.
- Ten profile output files reproduced byte-for-byte across two final executions, including compressed CSV and four figures.
- Primary cation-profile and scenario-rank figures visually inspected; independent reviewer checked all four figures for clipping/legibility.
- Source chemistry and coordinates remain unchanged. All five bundled analysis inputs are SHA-256 verified before running.
- Full ten-endpoint similarity is not identified; tests validate computation and provenance, not scientific equivalence.

No external publication performed. Final archive excludes Python and matplotlib caches. The package manifest covers files actually shipped.

## Archive-expansion compatibility revision
Actual Kaggle diagnostic evidence established that `eda/texas_sources/texas_all.csv.gz` was absent after automatic archive expansion, while the exact plain CSV existed. The updated loader supports original gzip or expanded-only CSV with original byte count and SHA-256 enforcement. Four integrity tests additionally reject corrupt gzip, corrupt plain CSV and absent sources; a bad gzip is never silently bypassed using a valid plain file. Scientific calculations are unchanged.

Notebook setup skips bundled outputs and clears only its generated output directories, verifies inputs early, prints complete subprocess error diagnostics, and asserts 10 fresh profile outputs plus 25 fresh EDA outputs. The notebook is validated locally in both archive modes; this is not a claim of a successful Kaggle rerun.
