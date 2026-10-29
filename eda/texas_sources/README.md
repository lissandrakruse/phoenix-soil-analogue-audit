# Texas soil chemistry screening for Phoenix WCL comparisons
Retrieved 2026-10-28 from USDA NCSS Soil Characterization Database via SDA.

## Verified result
- 14,805 unique laboratory sample IDs joined to Texas sites and chemical properties.
- 3,882 samples have all eight values in the SAME chemical-properties row: saturated-paste pH, saturation-extract EC, Ca, Mg, Na, K, Cl, sulfate.
- These represent 869 pedons, with 147 distinct non-null counties; county may be missing.
- 3,604 complete samples have both latitude and longitude. 660 have coordinates, top depth <=5 cm and bottom depth > top depth (not necessarily shallow-only intervals).
- 15 samples additionally have pH, EC and all six ions in water-extract fields. These are only TWO pedons in Culberson County, in a gypsum study, not 15 independent locations: 07N0078 and 07N0079. Method stored: 4D2a2d1-22.
- No perchlorate or ammonium-ion concentration column is present in inspected lab_chemical_properties schema. NH4 in exchangeable-cation names refers to extraction reagent, not ammonium measured in the soil. Therefore NONE qualifies as complete for an all-ion Phoenix comparison including ClO4 and NH4.

## Files
- download.py: standard-library-only reproducible public POST request; query.sql saved verbatim.
- texas_raw.json: unmodified API response; JSON null means absent, not zero.
- texas_all.csv: flattened results (empty CSV cells correspond to JSON null).
- texas_complete_saturation.csv: eight-value complete cases only.
- texas_complete_geolocated.csv: complete cases with coordinates.
- texas_water_extract.csv: 15 water-extract complete samples.
- summary.json: variable availability counts and county list.
- datause.html: official usage page retrieved at download time.
- pedon34266.html: official primary characterization report for Culberson pedon 07N0078.

## Methods, units and strict limitations
Saturation ions are millimoles of charge per litre (equivalent to meq/L), NOT mmol of ions/L. For Ca2+, Mg2+ and SO4(2-), mmol ions/L = reported value / 2. Monovalent Na/K/Cl retain numeric value. EC is dS/m; depths cm; coordinates decimal degrees. Conversion does NOT make extraction methods comparable.

Phoenix WCL used a dilute water extraction, not saturation-paste extraction; the different water:soil ratio, material preparation, equilibration and detection conventions matter. Do not rank against Phoenix by raw concentration or pH without method-aware treatment. Do not mix exchangeable, total-element and soluble-extract chemistry. Values reported as 0.0 have limited reported precision and are not proof of absolute absence. Missing measurements are not nondetects. Preserve method and preparation codes.

Water-extract cations and chloride are documented as micrograms/kg, not solution molarity. The USDA Dec2025 content standard's sulfatewaterextractable definition is internally inconsistent: prose says meq/L, explicit unit says micrograms/kg. Resolve legacy method and reporting basis before using water-extract concentrations. Modern related 4D2a2 method uses 7 g soil and 35 mL water (1:5), with 23 h standing plus 1 h shaking; it must not be assumed identical to legacy 2006 method or Phoenix.

The same lab sample ID is used for chemistry joins; no cross-sample filling was performed. These are measured points/horizons, not city averages. County names are not city names. Dataset coverage is not a probability sample of Texas. Some records have missing location, zero-length depths, unusual prep codes or copied pedon identifiers; retain/examine these before modeling.

Example county availability (eight-variable complete rows/pedons): Lubbock 67/20; Harris 58/13; El Paso 1/1; Travis, Dallas, Bexar, Tarrant 0/0. Absence here means no complete eight-variable case in this downloaded query, not no soil data of any kind.

## Example measured row
85P03348; pedon 85P0647; El Paso County; 31.9127769, -106.5175018; 25–35 cm; pH 7.8; EC 0.50 dS/m; Ca 4.8, Mg 0.5, Na 0.5, K 0.0, Cl 0.3, SO4 1.5 meq/L. Historical methods preserved in CSV. Not a surface or city-representative sample.

## Primary sources / reproducibility
- https://ncsslabdatamart.sc.egov.usda.gov/querypage.aspx
- https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest (POST JSON query + format JSON+COLUMNNAME)
- https://nasis.sc.egov.usda.gov/NasisReportsWebSite/limsreport.aspx?report_name=SDA-chemical-properties-by-state (official join example; this download does NOT retain its carbon/depth restrictions)
- https://www.nrcs.usda.gov/sites/default/files/2025-12/NCSS-SCD%20Data%20Content%20Standard.pdf (units and data definitions; printed pp38,40,41,44,45,66)
- https://www.nrcs.usda.gov/sites/default/files/2022-10/SSIR42-v6-pt1.pdf (methods)
- https://ncsslabdatamart.sc.egov.usda.gov/datause.aspx (cite NCSS Soil Characterization Database; user responsible for accuracy and applicability)
- https://catalog.data.gov/dataset/ncss-soil-characterization-database (official metadata public-domain license)

## Perchlorate follow-on candidate, NOT joined to NCSS
Jackson et al., Texas Tech / TCEQ, 2004, Distribution and Potential Sources of Perchlorate in the High Plains Region of Texas:
https://www.clu-in.org/download/contaminantfocus/perchlorate/final%20report.pdf
Main report says sediment water extracts were analyzed for perchlorate plus cations/anions (Chapter 3; printed pp42,46–47,51,55), referring full ion data to Appendix B. The retrieved main report ends at printed p170 without Appendix B. Therefore joint row-level completeness for pH/EC/all six ions/ClO4/NH4 is UNVERIFIED. Groundwater tables must NOT substitute for soil chemistry. This is a relevant unresolved source, not evidence that full Texas data are impossible.

## County inventory
county_coverage.csv is alphabetically sorted coverage, not a chemical-similarity ranking.
