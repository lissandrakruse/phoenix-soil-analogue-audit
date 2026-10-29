from pathlib import Path
import json
R=Path(__file__).resolve().parent
cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s})
def code(s):cells.append({'cell_type':'code','metadata':{},'source':s,'outputs':[],'execution_count':None})
md('''# Texas soils × Phoenix WCL: numerical profile study
## Observed chemistry, multivariate distances and sensitivity—not an invented full-match percentage
We analyze all **14,805 Texas source layers**, then compare declared common-ion relative profiles. Results distinguish a complete-eight-panel selection from maximal profile availability. Missing ClO4/NH4 and incompatible or unvalidated extraction prevent a full ten-endpoint equivalence conclusion. The computations below do more than count coverage, while preserving that distinction.''')
code('''from pathlib import Path
import os, shutil, subprocess, sys, json
import pandas as pd
from IPython.display import display, Image
# Set TEXAS_STUDY_ROOT only if more than one package is attached.
roots = [Path(os.environ['TEXAS_STUDY_ROOT'])] if os.environ.get('TEXAS_STUDY_ROOT') else [Path.cwd()]
if Path('/kaggle/input').exists() and not os.environ.get('TEXAS_STUDY_ROOT'):
    roots += [p.parent for p in Path('/kaggle/input').rglob('run_profiles.py')]
roots = list(dict.fromkeys(p.resolve() for p in roots if (p/'inputs'/'checksums.json').exists() and (p/'run_profiles.py').exists()))
assert len(roots)==1, 'Set TEXAS_STUDY_ROOT to the intended numerical-study package.'
source = roots[0]
WORK = Path('/kaggle/working/texas_numerical_study') if Path('/kaggle/working').exists() else Path('/tmp/texas_numerical_study_kaggle_v2_run')
assert WORK.resolve()!=source.resolve()
shutil.copytree(source,WORK,dirs_exist_ok=True,ignore=shutil.ignore_patterns('outputs','__pycache__','.cache','.mplcache'))
# Only generated directories inside this dedicated writable run tree are cleared.
for generated in [WORK/'outputs',WORK/'eda/outputs']:
    if generated.exists(): shutil.rmtree(generated)

OUT=WORK/'outputs'
def run(script):
    result=subprocess.run([sys.executable,str(WORK/script)],cwd=WORK,capture_output=True,text=True,check=False)
    print(result.stdout); print(result.stderr); result.check_returncode()
print('Frozen public input package copied to writable working directory.')
if (WORK/'restore_inputs.py').exists():
    run('restore_inputs.py')
import hashlib
for name,expected in json.loads((WORK/'inputs/checksums.json').read_text()).items():
    assert hashlib.sha256((WORK/'inputs'/name).read_bytes()).hexdigest()==expected,name
print('Early input-integrity checks passed; Python:',sys.version)''')
md('''## 1. Full soil inventory and statistical context
The EDA preserves original units, methods, sample IDs and missing values. Negative source concentrations are flagged, not clipped. Repeated horizons and shared coordinates do not become independent geographic replicates. Correlations describe this selected archive, not causal relationships or Texas-wide representativeness.''')
code('''run('eda/analyze.py')
run('eda/test_study.py')
display(pd.read_csv(WORK/'eda/outputs/descriptive_distributions.csv').head(16))
display(Image(filename=str(WORK/'eda/outputs/distributions.png')))''')
md('''## 2. Quantitative common-ion profiles
For each same-row positive ion vector, convert saturation meq/L to mmol ions/L (Ca, Mg, sulfate divide by two). This fixes dimensions, **not extraction equivalence**. Compute `clr(x)=ln(x)-mean(ln(x))`, then the Euclidean distance between CLR vectors. Four-cation profiles are primary; chloride is sensitivity; six-ion calculations are **secondary mixed-endpoint sensitivity**, because later titrated total sulfate is not contemporaneous with the earlier ISE chemistry. We never manufacture missing reference endpoints.

A zero distance means equal declared ratios only. There is no validated acceptance threshold, no overall percentage, and no pH/EC contribution to an arbitrary composite score. All rank calculations use distances rounded to 12 decimals (competition/min rank); full-precision distances remain exported.''')
code('''run('run_profiles.py')
run('test_profiles.py')
run('make_profile_figures.py')
summary=pd.read_csv(OUT/'profile_run_summary.csv')
display(summary[(summary.reference=='Rosy Red') & (summary.stratum=='all_depths')])
display(Image(filename=str(OUT/'profile_distance_distributions.png')))''')
md('''## 3. Closest observed shallow profiles—with complete context
These are closest **observed four-cation profiles** in the stated cohort, not complete Mars analogs. The strict shallow stratum contains the entire measured horizon within 0–5 cm; separate outputs retain overlapping and all-depth intervals. We show one closest observed horizon per pedon, never a synthetic average. This selection favors pedons with more sampled horizons; exported counts expose that limitation.

Soil names retain USDA source contexts. Census places are coordinate-based assignments to 2025 boundaries, not verified historical municipalities. Coordinates may be uncertain even far from a boundary.''')
code('''closest=pd.read_csv(OUT/'shallow_closest_profiles_full_values_and_location.csv',dtype={'labsampnum':'string','pedon_key':'string','place_geoid':'string'})
columns=['labsampnum','pedon_key','samp_name','corr_name','hzn_top','hzn_bot','county_name','latitude_decimal_degrees','longitude_decimal_degrees','place_label','locality_status','texas_source_available_dimensions','reference_missing_requested_endpoints','distance','scenario_rank_min','scenario_rank_max']
display(closest[columns].head(10))
chemistry=['labsampnum','ph_saturated_paste','electrical_conductivity_satx','ca_satx','mg_satx','na_satx','k_satx','cl_satx','so4_satx','ClO4_status','NH4_status','joint_values_units','status']
display(closest[chemistry].head(10))
display(Image(filename=str(OUT/'shallow_cation_profiles.png')))''')
md('''## 4. Robustness rather than false precision
The finite corner scenarios use published marginal reference-error endpoints without assuming a probability distribution or known covariance. Their extrema are **not confidence intervals or guaranteed bounds over every interior value**. They omit unknown Texas measurement errors and extraction bias. Sorceress 2's malformed Mg upper uncertainty is not silently repaired.

`texas_source_available_dimensions` is Texas source availability only—not paired comparable endpoints. Rosy Red lacks measured EC; Sorceress 1 lacks sulfate; Sorceress 2 lacks reliable pH. All Texas rows lack measured ClO4/NH4. pH and EC contrasts, where present, remain method-confounded descriptive values.''')
code('''display(Image(filename=str(OUT/'shallow_rank_scenarios.png')))
# Visually secondary endpoint-choice diagnostic, not a uniform full-match scale.
display(Image(filename=str(OUT/'secondary_endpoint_rank_sensitivity.png')))
display(pd.read_csv(OUT/'rank_sensitivity_correlations.csv',header=[0,1],index_col=0))''')
md('''## 5. What the numerical study can and cannot conclude
Closest profiles depend on depth, selected endpoints, reference sample and uncertainty scenarios. The results support prioritizing **further measurements**, not declaring a location or soil fully Phoenix-like. Missing chemical dimensions and an unvalidated extraction bridge make the full ten-endpoint question unidentifiable from these data. The remedy is paired-method, same-sample measurements with all endpoints, blanks, replicates, detection limits and purpose-defined equivalence tolerances.

### Primary sources and project provenance
- [USDA NCSS database](https://ncsslabdatamart.sc.egov.usda.gov/querypage.aspx), [official metadata/public-domain provenance](https://catalog.data.gov/dataset/ncss-soil-characterization-database), [December 2025 content standard](https://www.nrcs.usda.gov/sites/default/files/2025-12/NCSS-SCD%20Data%20Content%20Standard.pdf), [laboratory methods](https://www.nrcs.usda.gov/sites/default/files/2022-10/SSIR42-v6-pt1.pdf).
- Kounaves et al. (2010), [WCL data analysis and results, JGR Table 7](https://doi.org/10.1029/2009JE003424); separate [titrated sulfate, GRL Table 1](https://doi.org/10.1029/2010GL042613).
- [Hecht et al. (2009)](https://doi.org/10.1126/science.1172466), contextual Phoenix findings; [NASA PDS calibrated/derived MECA archive](https://doi.org/10.17189/1518770), provenance only—not ingested raw telemetry.
- [Stroble et al. (2013)](https://doi.org/10.1016/j.icarus.2012.08.040): abstract and author account checked; full text unavailable. [Public primary 2011 conference precursor](https://www.lpi.usra.edu/meetings/polar2011/pdf/6003.pdf). Its modeled equilibrium values are not substituted for measured JGR endpoints.
- [Census 2025 Texas places](https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_48_place.zip), [boundary vintage documentation](https://www.census.gov/geographies/mapping-files/2025/geo/tiger-line-file.html).

Original standalone project code is Apache 2.0. Government source data retain their provenance; papers are cited, not redistributed in full. No private Brazilian dataset, credentials, upstream application modules or agency endorsement is included. See README, METHODS, provenance and manifests for reproduction details.''')
code('''import hashlib
for name,expected in json.loads((WORK/'inputs/checksums.json').read_text()).items():
    assert hashlib.sha256((WORK/'inputs'/name).read_bytes()).hexdigest()==expected
print('PASS: immutable inputs verified; EDA and numerical profile tests passed. Full similarity remains unknown.')
print('Outputs:',OUT)
assert len([p for p in OUT.iterdir() if p.is_file()])==10
assert len([p for p in (WORK/'eda/outputs').iterdir() if p.is_file()])==25
assert len(pd.read_csv(OUT/'profile_distances_all_strata_EXPLORATORY.csv.gz'))==124117
print('PASS: 35 fresh output files; no bundled example outputs reused.')
''')
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'cells':cells}
(R/'Texas_Phoenix_Numerical_Study.ipynb').write_text(json.dumps(nb,indent=1))
print('Built notebook:',len(cells),'cells')
