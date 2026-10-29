# Verification

Nine tests passed: exact source sample/measurement preservation, complete-case counts, QC-negative/depth/interval flags, all 16 tidy-field units/statuses, bootstrap estimand/counts, incomplete charge-inventory identity, QC-sensitivity exclusion counts, positive-longitude flags, and input hashes.

All five PNG figures were visually inspected (availability, distributions, pedon correlations, raw coordinates, regional zoom); labels and units are legible. Coordinate inspection revealed the 14 east-longitude records, which are now explicitly flagged rather than silently corrected.

Two full runs use the fixed seed 20261029. Refer to run_metadata.json for the authoritative seed. Output reproducibility is verified against first_run_hashes.json; validation results are recorded separately. This study never interprets bootstrap stability intervals as Texas-population confidence intervals.

Coverage is the full downloaded chemistry query, not every soil variable. The original UI/repositories were not modified and no external publication was performed.
