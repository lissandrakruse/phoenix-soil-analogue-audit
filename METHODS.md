# Quantitative redesign: exploratory profiles versus full similarity

## Recommended product
Produce a full *analysis* of every requested parameter, but never imply a full *measured match* where coordinates of that chemical vector are missing. Use an endpoint coverage table plus quantitative common-variable panels, not a single invented percentage. Keep observed distances and reference sensitivity visible for every sample. No similarity cutoff is calibrated by these data.

### 1. Primary relative cation profile
For same-row positive saturation-extract Ca, Mg, Na, K, convert meq/L to mmol ions/L by dividing Ca and Mg by two. This is a dimensional correction, not extraction harmonization. Compare the four-part subcomposition against each separately identified Phoenix Table 7 sample.

clr(x)_j = ln(x_j) - mean_k ln(x_k)
d_A(x,r) = sqrt(sum_j [clr(x)_j-clr(r)_j]^2).

Distance is dimensionless; zero means exactly identical *four-cation ratios*, not identical soil, concentration or extraction. No % similarity transformation is justified. Ratios remove a common multiplicative scale; ion-selective dissolution, adsorption, complexation and carbonate precipitation remain. Four cations are a declared subcomposition; omitted perchlorate, ammonium and anions are not implicitly zero. Use natural logarithms and no undocumented standardization.

If a value is zero/nonpositive or missing, do not silently add a pseudocount. Report excluded counts. Only censored measurements with documented detection limits support censored interval treatment. Source rounded zero is not a known limit.

### 2. Other endpoint panels, not hidden composite weights
- Add chloride to the profile only as a separately labeled five-ion sensitivity analysis: Phoenix Table7 chloride includes selected experiment intervals/reagent effects, so this is not pure-water chemistry reconstruction.
- Sulfate must retain its independently titrated endpoint and time context; do not silently combine modeled free sulfate (e.g. 3.9 mM) with experimental ISE concentration vectors. A six-ion profile is conditional until sulfate reference endpoint is justified.
- Display pH differences and EC ratios numerically in original comparable dimensions, explicitly as method-confounded descriptive contrasts. pH is already logarithmic; do not log it or mix arbitrary z-scores with ion ratios. mS/cm and dS/m are dimensionally equal, but extraction ratio/temperature differences persist. Rosy Red measured EC absent: do not fill from a different Phoenix sample.
- ClO4/NH4: unavailable in current USDA data, therefore unknown contributions. NH4 Phoenix estimates are also qualified; Sorceress1 ND has no numeric censoring limit. No imputation, zero, surrogate reagent value or average from another site.

### 3. Reference and sampling sensitivity
Evaluate Rosy Red, Sorceress1, Sorceress2 point references separately. S2 Mg upper uncertainty is malformed in original Table7 and remains unresolved, so do not manufacture its distribution. Do not interpret published propagated errors as 95% CIs. RR/S1 marginal error endpoints support deterministic sensitivity scenarios only; independent corner combinations are a deliberately conservative scenario set, not a joint confidence region. Monte Carlo is not calibrated without covariance/distribution assumptions and cannot repair Texas's absent measurement uncertainty or method bias.

Report all three point distances, reference-dependent ranks, and scenario rank ranges. If rankings change substantially, say so. Bootstrap only at pedon level for coverage summaries; repeated horizons are not independent samples. Do not bootstrap three Phoenix measurements into a reliable population covariance or use a Mahalanobis significance claim.

Depth strata: strictly contained 0–5 cm horizons separately from horizons merely overlapping 0–5 cm, and all depths. Do not relabel intervals beginning at 0 cm but ending at 100 cm as surface analogs. No depth-overlap weighting estimates a 0–5 cm chemistry without homogeneity assumptions. County and Census place summarize sampled points, not entire areas.

### 4. Identifiability of full similarity
No full pH/EC/Ca/Mg/Na/K/Cl/SO4/ClO4/NH4 matched-method comparison is supported by current Texas data. Even perfect measured-subvector similarity places no useful upper bound on full mismatch when missing components and extraction bias are unbounded. A complete vector alone would still require a purpose-defined equivalence tolerance.

Minimum next data: same physical sample, documented WCL-like extraction or a paired-method bridge covering relevant mineralogies, mass/extractant ratio, time, temperature, pCO2, blanks, replicates, detection/quantification limits, all requested endpoints, method error and covariance. Assess free-ion versus total dissolved endpoints and titration chemistry explicitly. Calibrate a decision rule against independently measured analog controls rather than declaring 'within one order of magnitude' a universal similarity criterion.

## Primary evidence checked
- Kounaves et al. 2010 JGR Table7 and sections 4,6: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2009JE003424 . Actual experimental reductions used in prototype, not equilibrium table values.
- Stroble et al. 2013 requested article DOI https://doi.org/10.1016/j.icarus.2012.08.040 . Abstract and author bibliography verified, but full article not retrieved: ScienceDirect returned403; author/LPI links also lead to publisher. Do NOT claim full text read or all final tables extracted.
- Public author conference precursor: https://www.lpi.usra.edu/meetings/polar2011/pdf/6003.pdf . Uses WCL spare/testbed, approximately1g/25mL, one-hour room-temperature leach and modified calibrant. Table1 explicitly equilibrium species; not interchangeable with Table7 measured reductions. Final2013 abstract compares depth averages and reports markedly different perchlorate; it is not validation of a complete all-parameter equivalence threshold.
- Author research account: https://planetary.chem.tufts.edu/AntarcticDV.html . Contextual corroboration of comparisons, not individual-row source table.

## Final portable study structure
Both complete-eight-panel and maximal-profile-availability cohorts are analyzed separately: 3,172 versus 4,251 positive four-cation rows. The four depth/QC strata are all depths, valid depth without repeated pedon intervals, entire horizon within 0–5 cm, and horizon overlapping 0–5 cm. No 0–5 cm fraction is inferred from an overlapping measurement.

The outputs contain 124,117 profile/cohort/stratum/reference records, not independent samples. `texas_source_available_dimensions` counts available Texas source endpoints only, not jointly validated Phoenix endpoints. All rows retain missing ClO4/NH4, unvalidated protocol equivalence and unknown full-similarity status.

`scenario_*` fields summarize finite marginal-error corner scenarios, not confidence intervals or guaranteed continuous-box bounds. Unknown Texas measurement uncertainty and extraction bias remain outside these scenarios. Ranks use full-precision distances rounded to 12 decimal places for deterministic competition ranking; unrounded distances remain stored. Tied leader selection uses sample ID order. Pedons are ordered by their closest actually observed horizon; this favors more intensively sampled pedons and is not an unbiased pedon population inference.

Four-cation profiles are primary. Five-ion profiles add chloride as sensitivity. Six-ion profiles use the separate titrated sulfate endpoints, deliberately mixing chemical endpoints; they are visually secondary sensitivity results, not simultaneous equilibrium solution chemistry. Sorceress 1 is not scored for six ions. Sorceress 2 point estimates remain separate and its unresolved Mg upper uncertainty prevents corner scenarios.

`run_profiles.py`, `make_profile_figures.py` and `test_profiles.py` use bundled relative paths. SHA-256 verifies frozen inputs. Root README gives reproduction commands and file inventory. No external data access occurs during analysis. Scientific conclusions remain limited to relative profiles under stated analytical choices, not complete Texas–Mars equivalence.
