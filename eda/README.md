# Texas soil study — reproducible descriptive analysis

This standalone study preserves the existing simulator and Brazil/Texas releases unchanged. It analyzes the complete downloaded Texas NCSS chemistry panel (14,805 samples), not every soil property in the national database, and does not implement Phoenix similarity.

Run:
```sh
python -m pip install -r requirements.txt
python eda/analyze.py
python eda/test_study.py
```
Read REPORT.md and outputs/. Raw input snapshots, public download queries/scripts and checksum files are in texas_sources/. Local build needs no network. Figures and report are English. All sample IDs, units, method/preparation codes and source-negative/zero/missing values are preserved. No synthetic tolerances, no imputation, no city-wide averages or suitability ranks.

Key output contracts:
- samples_wide.csv.gz: one row per exact laboratory sample, original chemistry plus soil-name basis, geography and QC flags.
- measurements_long.csv.gz: one sample × each of16 source variables, including missing entries; extraction, original unit, method code and status retained.
- partial_ion_inventory.csv: partial measured-charge sums, never a validated full ionic balance.
- qc_sensitivity_*.csv: raw complete cases versus documented exclusions; no values repaired.
- pedon_bootstrap_descriptives.csv: stability intervals for median of observed pedon medians, not Texas-population confidence intervals.
- source_sha256.json and run_metadata.json: input provenance and environment/seed.

The study code is new; The standalone public-input loader was authored for this research and has no private upstream dependency. Public source data attribution: USDA NCSS Soil Characterization Database and US Census TIGER/Line2025. The source taxonomy/locality READMEs retain precise caveats and public data links. Existing vendor trabalho code is not copied into this study.
