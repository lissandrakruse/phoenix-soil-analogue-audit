# Texas soil sample localities — coordinate-based screening

These files associate the **reported coordinates**, not independently verified physical sample locations, with frozen official 2025 Census place boundaries. They are coverage counts, never a chemical-similarity ranking or city-average chemistry.

## Reproduce with public data, no credentials

1. Obtain `texas_all.csv` with the parent folder's `download.py` and `query.sql` (USDA SDA public endpoint). The preserved snapshot has SHA256 `cefb7158c23921b5c98cdd6f5a5949a8b39a1b4f82f1d0ae5b71388042b483b6`. Live USDA data can change.
2. Install: `python -m pip install -r requirements-localities.txt`
3. Run: `python build_localities.py --input /path/to/texas_all.csv --output /path/to/output`
4. The script uses the included original Census zip if present; otherwise downloads the official public zip and verifies its SHA256 before processing. Input/output hashes and software versions are saved in `locality_validation.json`.

Boundary: https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_48_place.zip
SHA256: `5a0c4d49641f69028ee9f5c343bf09936ec00a378e5e6393115b106bab935e13`
Downloaded 2026-10-28. Frozen vintage: legal names/boundaries as of 2025-01-01, **not necessarily boundaries at sampling time or the latest 2026 vintage**. This is full TIGER/Line detail, not simplified cartographic boundaries. Source release: https://www.census.gov/geographies/mapping-files/2025/geo/tiger-line-file.html

## Schema and semantics

`texas_sample_localities.csv`: one row per unique `labsampnum`, all 14,805 input samples preserved. Read sample IDs/GEOIDs as strings. Left-join only by `labsampnum` and validate one-to-one; do not join on city, county or pedon alone. Coordinate strings and source county are retained unchanged. `complete_eight_parameters=1` means all eight saturation chemistry fields occur in that same source row. It does NOT mean complete Phoenix comparability.

`locality_status`: `inside` = strictly inside exactly one place polygon; `outside` = outside all mapped Texas places; `missing` = latitude and/or longitude absent; `ambiguous` = point on a boundary or overlapping multiple places; `invalid_coordinates` = nonfinite/out-of-world coordinates. No ambiguous or invalid cases occurred in this snapshot. `outside` is not the nearest city and does not assert which unincorporated community is present. Most Texas territory is outside a Census place. The join does not independently validate Texas state membership for points outside every place. Missing coordinates are never filled from county centroids or nearest cities.

`place_type`: `incorporated_place` from Census MTFCC G4110; `census_designated_place` from G4210. A CDP is a statistical settlement, NOT an incorporated city. `place_label` preserves official city/town/village/CDP suffix, `place_name` is its unsuffixed name, `place_geoid` is Census GEOID. `county_name` is the original USDA county field and is NOT a computed county assignment; municipalities can cross counties.

`boundary_distance_m` = approximate planar distance to the nearest place boundary (EPSG:3083 Texas Centric Albers), for caution only. It never assigns a nearest city. `within_100m_boundary` is a sensitivity-review flag, NOT an accuracy estimate or confidence interval. A value 0 does NOT guarantee accurate locality. `assignment_basis` is always coordinate-based screening; `coordinate_accuracy_quantified=0` everywhere.

`texas_locality_coverage.csv`: alphabetical coverage by coordinate-inside Census place; sample/pedon counts plus complete-eight counts. Pedons/horizons are not independent geographic replicates; counts do not measure city coverage quality. Repeated sample depths are retained, not promoted to independent sites.

## CRS, coordinate precision and uncertainty — essential

NCSS December-2025 content standard defines standardized decimal-degree coordinates as WGS84 (printed p72 and pp163–164): https://www.nrcs.usda.gov/sites/default/files/2025-12/NCSS-SCD%20Data%20Content%20Standard.pdf
The query uses `lab_combine_nasis_ncss.latitude_decimal_degrees`/`longitude_decimal_degrees`. We operationally assume EPSG:4326, transforming with pyproj to the shapefile's embedded NAD83 EPSG:4269 before PIP. Per-record source datum/accuracy were NOT returned by the original query, and the standard does not establish independent accuracy of each legacy combined-table row.

USDA metadata explicitly warns location accuracy is unquantified, older records may be county centroids, and missing original datums may be NAD27 before 1990 or WGS84 after 1995: https://catalog.data.gov/dataset/ncss-soil-characterization-database
Seven stored decimal places must not be interpreted as centimetre accuracy. We do not infer original datum from date or reproject an already-standardized coordinate a second time. Date-based datum ambiguity, source positional errors and historical annexations remain unresolved. Therefore **display candidate city/settlement from reported coordinates, never “verified sample belongs to city.”** Even records far from a boundary may have inaccurate coordinates.

## Validation

All 1,863 place geometries valid; no silent geometry repairs. Input sample IDs unique; all 14,805 rows retained. 12,673 rows have both coordinates; 2,132 missing. Coordinate-inside: 796 samples in 64 places. Complete-eight: 3,882 rows = 109 inside 18 places + 3,495 outside + 278 missing. The 3,604 geolocated complete samples are fully retained. There are 307 all-sample and 25 complete-eight records within 100 m of any place boundary (inside OR outside). These are horizons, not 307 independent sites. Full run summary/hashes: `locality_validation.json`.

## Public data and licensing provenance

USDA Data.gov catalog marks the NCSS distribution public-domain: https://catalog.data.gov/dataset/ncss-soil-characterization-database
Census describes TIGER as a public-domain source: https://www.census.gov/newsroom/archives/2014-pr/cb14-208.html
Census boundaries are statistical mapping products, not legal land descriptions or a survey. Preserve agency attribution and uncertainty when redistributing. No private records, paid geocoder, account or API token is used in this join.
