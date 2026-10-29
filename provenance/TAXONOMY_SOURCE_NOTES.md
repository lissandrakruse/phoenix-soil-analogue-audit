# Texas NCSS pedon soil-name and taxonomy supplement
Retrieved 2026-10-28 23:48 UTC. Supplemental only; original chemistry files and their hashes unchanged.

## Source and exact join
Public USDA SDA endpoint: https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest
Official join/field example: https://nasis.sc.egov.usda.gov/NasisReportsWebSite/limsreport.aspx?report_name=SDA-chemical-properties-by-state
Official field definitions (printed pp68,74,78): https://www.nrcs.usda.gov/sites/default/files/2025-12/NCSS-SCD%20Data%20Content%20Standard.pdf
License: public domain, per https://catalog.data.gov/dataset/ncss-soil-characterization-database

Run download_taxonomy.py to query lab_combine_nasis_ncss joined to lab_area by state_key, TX. query.sql is exact executed SQL; taxonomy_raw.json is unmodified full-state response. texas_pedon_taxonomy.csv filters those rows to exact pedon_key values in the original texas_all.csv (14,805 chemistry samples). There is exactly one supplement row per pedon_key; all 2,165 baseline pedon keys match. JOIN chemistry.pedon_key = taxonomy.pedon_key, many samples to one pedon. Do NOT join by county, coordinates, names or similar-looking user IDs. Raw query can contain additional Texas pedons without chemistry rows, deliberately excluded from final supplement.

## Field interpretation and display
samp_* = sampled-as name/classification; corr_* = correlated name/classification; SSL_* = laboratory classification. Preserve all three independently, together with class_type and classdate. Dates indicate assigned classifications, not necessarily collection date. Do not claim corr_* is guaranteed today's current taxonomic status. Preserve verbatim taxonomy and source capitalization/spelling; no translated, standardized or inferred series names have been inserted.

*_name is a soil/taxon name. Only label a record 'series' when its corresponding *_class_type says series (case insensitive). Some explicitly are taxadjunct, variant, family or taxon above family; missing class_type must remain unknown. *_classification_name is the reported Soil Taxonomy subgroup + family long name, not a series name. taxorder, taxsuborder, taxgrtgroup and taxsubgrp give reported levels separately.

Suggested display: show 'Correlated soil name' if corr_name is populated, with class_type and classdate; otherwise show sampled-as name with that label; if both missing and SSL_name present show lab-assigned name labeled accordingly. Show historical sampled-as name separately if different. For classification use the matching source when available; if another source supplies it, label that source independently so a synthesized name/classification pair is not mistaken for a single official determination. This is a display rule, not a new scientific classification.

Empty CSV cell = missing reported value. Explicit UI text: 'Not reported'. Any-source name is available for 2,037/2,165 pedons, corresponding to 14,166/14,805 chemistry rows; 639 sample rows have no reported name in these three sources. Any-source long classification is available for 1,938 pedons / 13,453 chemistry rows. Detailed individual-field completeness and class-type counts: summary.json.

This supplement does not alter chemistry, coordinates, depth, source sample IDs, measurement completeness, extraction compatibility or absence of perchlorate/ammonium. No ranking or simulator mutation was performed by this retrieval.
