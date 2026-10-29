# Texas soil chemistry × Phoenix: numerical profile study

This is an original, reproducible analysis of public USDA NCSS Texas records and separately qualified published Phoenix WCL endpoints. It performs substantive multivariate numerical profile comparisons, distributions, correlations, quality-control and sensitivity analyses. **It does not establish full ten-endpoint Texas–Phoenix similarity.**

## Reproduce offline
Use Python3.12 and `pip install -r requirements.txt` beforehand. No account/token/network is required during analysis.

```
python restore_inputs.py
python run_profiles.py
python make_profile_figures.py
python test_profiles.py
python eda/analyze.py
python eda/test_study.py
```

`Texas_Phoenix_Numerical_Study.ipynb` presents these analyses. Its runner copies the supplied package to a writable working directory before executing; this supports read-only Kaggle inputs. Immutable public inputs are under `inputs/` and verified against `inputs/checksums.json`. Output source coordinates/chemistry are unchanged, while derived profiles are explicitly labeled. A package-level manifest records every shipped file; the publisher should generate a new manifest after any notebook execution or edits.

## What is computed
- Four-cation molar subcomposition Aitchison distance to Rosy Red, Sorceress1 and Sorceress2, separately.
- Five-ion chloride sensitivity and **visually secondary, conditional mixed-endpoint six-ion** sensitivity. Later titrated sulfate is not a contemporaneous ISE concentration vector.
- Complete-eight-panel cohort versus maximal profile availability:3,172 versus4,251 positive four-cation rows; these are different cohorts, not inconsistent totals.
- All-depth, valid-depth/nonduplicate, strictly0–5cm-contained and0–5cm-overlapping horizons. Overlap does not imply a shallow-only measurement.
- Distinct-pedon closest observed horizons, with sampling-density bias exposed; no synthetic pedon/city chemical means.
- Finite marginal-error corner scenarios—not probabilities, confidence intervals or exhaustive continuous-box bounds. Unknown source error, covariance and extraction bias are not estimated.
- Exact distances retained; ranks use values rounded to12 decimal places with competition ranking (`min`) to make numerical ties deterministic.
- pH differences and EC ratios only as separate **method-confounded descriptive contrasts**, never combined into arbitrary overall scores.

## Reading results
`texas_source_available_dimensions` counts available Texas source endpoints only, not jointly validated Phoenix comparison endpoints. An8/10 value is neither80% similarity nor80% method comparability. Texas ClO4/NH4 are absent. RosyRed measured EC is absent; Sorceress1 sulfate is absent; Sorceress2 pH is unreliable and its Mg upper uncertainty is unresolved. NH4 estimates have additional qualifications. These gaps remain explicit.

A distance of zero means identical declared relative ion profiles—not equal absolute concentration, identical extraction, equivalent soil, habitability or agronomic performance. No acceptance threshold or percent-similarity transformation is justified. Ion ratios remove only common multiplicative scaling; they do not fix selective dissolution, precipitation, adsorption or complexation. All-profile closest rows can be several metres deep. Source names are USDA contexts, not automatically verified current series names. Official Census place assignments are coordinate-based screening, not independently verified historic sampling municipalities.

## Files for interpretation
- `outputs/shallow_closest_profiles_full_values_and_location.csv`: IDs, soil names, depth, original joint chemistry, coordinates, county, Census locality/status, source-availability and unknown-full-similarity flags.
- `outputs/profile_distances_all_strata_EXPLORATORY.csv.gz`: all124,117 computed profile/cohort/stratum/reference records, not124,117 independent samples.
- `outputs/profile_run_summary.csv`: counts/exclusions and unavailable-reference groups.
- `outputs/*png`: distributions, shallow cation profile shape, reference scenario ranks and secondary endpoint sensitivity.
- `eda/`: original all14,805-layer statistical analysis, missingness, methods, quality flags, correlations and plots.
- `METHODS.md`: endpoint decisions and evidence limits.

## Sources and rights
USDA NCSS/Kellogg Soil Survey Laboratory public source: https://ncsslabdatamart.sc.egov.usda.gov/querypage.aspx ; public-domain distribution metadata: https://catalog.data.gov/dataset/ncss-soil-characterization-database . Units/methods: https://www.nrcs.usda.gov/sites/default/files/2025-12/NCSS-SCD%20Data%20Content%20Standard.pdf and https://www.nrcs.usda.gov/sites/default/files/2022-10/SSIR42-v6-pt1.pdf . Snapshot retrieved2026-10-28; live refresh can change results.

Phoenix primary measurements: Kounaves et al.(2010), *Wet Chemistry experiments on the2007 Phoenix Mars Scout Lander mission: Data analysis and results*, JGR115,E00E10, https://doi.org/10.1029/2009JE003424 (Table7, pH/EC sections). Separate sulfate: Kounaves et al.(2010), *Soluble sulfate in the martian soil at the Phoenix landing site*, GRL37,L09201, https://doi.org/10.1029/2010GL042613 (Table1). Context: Hecht et al.(2009), *Detection of perchlorate and the soluble chemistry of martian soil at the Phoenix lander site*, https://doi.org/10.1126/science.1172466 . Archive provenance, not ingested telemetry: NASA PDS calibrated/derived MECA bundle https://doi.org/10.17189/1518770 . Numeric reference ledger contains published experimental reductions, not a new raw-telemetry analysis.

Comparative context: Stroble et al.(2013), https://doi.org/10.1016/j.icarus.2012.08.040 . Only publisher abstract/author account were accessible; no claim of full-text table extraction. Public primary conference precursor: https://www.lpi.usra.edu/meetings/polar2011/pdf/6003.pdf . Its equilibrium table is not substituted for measured experimental endpoints.

Census2025 Texas places: https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_48_place.zip ; vintage documentation: https://www.census.gov/geographies/mapping-files/2025/geo/tiger-line-file.html . Legal boundaries/names as of2025-01-01, not necessarily sampling-time boundaries. Positional accuracy is unquantified; suspicious positive Texas longitudes are flagged without correction.

New code: Apache2.0. USDA/Census data retain public-source provenance; cited publications are not relicensed or redistributed in full. No NASA/USDA/Census endorsement. No Brazilian datasets, private credentials, third-party upstream application code or complete copyrighted PDFs are included.

## Archive-expansion compatibility revision
Kaggle automatically expanded the three EDA source gzip files during dataset ingestion. An actual diagnostic run confirmed the missing gzip path while exact plain CSV files were present. The loader now accepts either the original gzip (checking its compressed hash) or, only when gzip is absent, the exact plain CSV (checking original uncompressed byte count and SHA-256). It never bypasses content checks or repairs source values.

Notebook setup omits bundled example output directories when copying inputs, then clears only generated output directories inside its dedicated writable run tree. It verifies source inputs early, prints subprocess stderr on failure, and asserts all 35 outputs were freshly generated. Local compatibility validation covers both original gzip and expanded-only CSV inputs. Actual Kaggle success must still be verified by the publisher; local validation is not a platform-execution claim.

## Compact GitHub distribution
This independent repository contains only newly authored analysis code and public-source data. Before opening the notebook or running scripts, run `python restore_inputs.py`; it decompresses exact frozen inputs and verifies every original SHA-256. No scientific input values or notebook results were changed for packaging.

Large regenerable outputs and the duplicate Census base64 archive are omitted, as listed in `PUBLICATION_PROVENANCE.json`. `python run_profiles.py` regenerates the full profile table; `python eda/analyze.py` regenerates long measurements and quality flags. Census polygons are unnecessary for ordinary profile analysis because frozen locality assignments are included; to independently regenerate localities, first run `python provenance/restore_census_archive.py` (official network download, SHA-256 checked), then follow the locality source notes. No private repository history is included.
