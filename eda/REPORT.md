# Texas NCSS soil-data study

## Scope and main findings
- 14,805 laboratory layers from 2,165 pedons; 3,882 layers from 869 pedons contain all eight saturation-panel variables. These are convenience/archive observations, not a representative Texas survey.
- EC is measured in 5,778 layers. Median 1.07 dS/m; 5th–95th percentiles 0.3–12.2; maximum 143. These describe archived extracts, not site-wide salinity.
- Saturation-paste pH median 7.6, 5th–95th percentiles 5–8.3. pH is only one part of chemistry.
- 10 distinct eight-field method-code signatures occur among complete panels; pooled summaries cannot establish method equivalence.
- 123 rows contain negative reported ion values (2 Ca, 62 Na, 62 K values, with overlapping rows). Their origin is unresolved; they are not interpreted as physical negative concentrations or silently set to zero. QC-excluded sensitivity outputs are provided.
- 175 layers have missing/invalid thickness; 277 rows share a pedon/depth interval with another sample. These are flags, not proof of laboratory replication.
- 47 coordinate pairs are shared by multiple pedons; repeated coordinates do not prove independent sites or duplicate chemistry.

## Units, zeros and measurement status
Saturation ions retain mmol charge/L (meq/L), EC dS/m, and depths cm. No ion-to-molar conversion or cross-extraction harmonization is performed. Reported zeros remain zeros; they are not assumed true absence or replaced with half a detection limit. Detection-limit/censoring metadata are unavailable for these rows. Missing values remain null. Negative or impossible-pH values are flagged, not silently deleted. Log figures use positive values only and are not imputations. Water-extract observations remain separate; sulfate unit documentation is unresolved.

## Design and missingness
Coverage tables stratify by pedon, county, depth band, preparation and soil-name basis. Complete-case analyses may select particular methods, locations and profiles. Missingness patterns are tabulated, but no MCAR/MAR assumption or statewide extrapolation is made. Counties are not cities. Soil classification is selected from one labelled basis; names can be series, family, variant or taxadjunct. Detailed alternatives remain in the source snapshot.

## Depth, clustering and uncertainty
Raw complete panels retain reported negatives; separate sensitivity tables exclude negative chemistry, then invalid depth, then repeated pedon/depth intervals. These filters are documented analytical choices, not proof that flagged records are erroneous. Layer Spearman correlations are compared with depth-partial rank correlations and correlations of pedon medians. No independent-layer significance tests are reported. Depth adjustment is descriptive, not causal; it does not remove geology, management, method or site confounding. Method/preparation-stratified pedon correlations are supplied for groups with at least 20 pedons (a stability/display threshold, not a scientific compatibility threshold).
The bootstrap resamples equal-weight observed pedon medians 2,000 times (fixed seed 20261029), reporting the median of pedon medians and empirical percentile stability intervals. It does not estimate a representative statewide parameter, account for shared-location clusters, or include measurement uncertainty. Layer-weighted and pedon-weighted estimands differ.

### Strongest pooled pedon-median associations (descriptive)
- na_satx vs cl_satx: Spearman 0.854; layer 0.879; depth-partial rank 0.853.
- electrical_conductivity_satx vs so4_satx: Spearman 0.773; layer 0.835; depth-partial rank 0.826.
- electrical_conductivity_satx vs cl_satx: Spearman 0.771; layer 0.848; depth-partial rank 0.846.
- na_satx vs so4_satx: Spearman 0.757; layer 0.768; depth-partial rank 0.726.
- cl_satx vs so4_satx: Spearman 0.716; layer 0.730; depth-partial rank 0.682.

## Recorded distributions by variable
| Field | Measured layers | Median | 5th–95th percentile | Reported zeros | Negative values |
|---|---:|---:|---:|---:|---:|
| Saturation-paste pH (pH) | 4197 | 7.6 | 5–8.3 | 0 | 0 |
| Saturation-extract EC (dS/m) | 5778 | 1.07 | 0.3–12.2 | 7 | 0 |
| Calcium (mmol charge/L (meq/L)) | 5347 | 4.2 | 0.4–30 | 24 | 2 |
| Magnesium (mmol charge/L (meq/L)) | 5350 | 1 | 0.1–17 | 92 | 0 |
| Sodium (mmol charge/L (meq/L)) | 5644 | 4.4 | 0.2–104 | 84 | 62 |
| Potassium (mmol charge/L (meq/L)) | 5569 | 0.2 | 0–1.6 | 861 | 62 |
| Chloride (mmol charge/L (meq/L)) | 4738 | 2.3 | 0.2–77.7 | 56 | 0 |
| Sulfate (mmol charge/L (meq/L)) | 4683 | 2.4 | 0.3–67.3 | 46 | 0 |

## Ionic inventory, not charge balance
This is a full analysis of the downloaded chemistry panel, not every possible soil property: texture, mineralogy, organic carbon and bulk elemental composition were not included in this frozen query. The six saturation ions permit observed cation-charge and observed chloride+sulfate-charge sums in the same sample. Bicarbonate/carbonate and other ions are missing. The reported difference is a partial inventory diagnostic, NOT charge-balance error; no accept/reject tolerance is imposed and no electroneutrality claim is made.

## Spatial interpretation
Fourteen layers in Ochiltree pedon 21213 (two complete) report longitude +100.997083 at latitude 36.278332, inconsistent with a Texas location. They remain unchanged and flagged; a regional zoom and raw-coordinate inventory figure are both supplied. Recorded coordinates are plotted without interpolation. Census place assignments are exploratory coordinate-to-2025-boundary joins, not validated historical sample-city identity. Old coordinates can be approximate/centroids; accuracy is unquantified. Near-boundary flags, missing coordinates and outside-place cases remain. No result is assigned to an entire city, county or accessible collecting site.

## Phoenix comparison boundary
This study does not calculate Phoenix similarity. Missing ClO4 and NH4, extraction differences and unresolved method/unit details prevent a validated full-parameter match. No synthetic tolerances, ranking or crop-suitability model is introduced.

## Reproduce
Run `python analyze.py`, then `python test_study.py`. Dependencies are recorded in requirements.txt. Input public queries/scripts, frozen compressed snapshots and SHA-256 provenance are bundled. See outputs for tidy measurements, all-layer flags, distributions, method strata, missingness, soil strata, correlations and bootstrap results.
