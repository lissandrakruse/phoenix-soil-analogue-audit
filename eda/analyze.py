"""Reproducible descriptive NCSS Texas study; no Phoenix matching or imputation."""
from pathlib import Path
import json,hashlib,platform,itertools,os
os.environ.setdefault("MPLCONFIGDIR",str(Path(__file__).resolve().parent/".mplcache"))
os.environ.setdefault("XDG_CACHE_HOME",str(Path(__file__).resolve().parent/".cache"))
import numpy as np
import pandas as pd
from scipy.stats import spearmanr,rankdata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from study_inputs import load_records,SAT,WATER
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
SEED=20261029;B=2000;rng=np.random.default_rng(SEED)
LABELS=dict(zip(SAT,['Saturation-paste pH','Saturation-extract EC','Calcium','Magnesium','Sodium','Potassium','Chloride','Sulfate']))
UNITS=dict(zip(SAT,['pH','dS/m']+['mmol charge/L (meq/L)']*6))
def method(k):return 'electrical_cond_satx_method' if k=='electrical_conductivity_satx' else (('ph_water_extract_method' if k=='ph_water_extract' else 'water_extract_method') if k in WATER else k+'_method')
def save(df,name):df.to_csv(OUT/name,index=False,compression={'method':'gzip','mtime':0} if name.endswith('.gz') else None)
rows=load_records();flat=[]
for r in rows:
 d={k:v for k,v in r.items() if k not in ['soil','locality']};d.update({'soil_'+k:v for k,v in r['soil'].items() if k!='original'});d.update({'locality_'+k:v for k,v in r['locality'].items()});flat.append(d)
f=pd.DataFrame(flat);f['eight_complete']=f[SAT].notna().all(axis=1);f['water_eight_complete']=f[WATER].notna().all(axis=1)
f['depth_valid']=f.hzn_top.notna()&f.hzn_bot.notna()&(f.hzn_bot>f.hzn_top)&(f.hzn_top>=0);f['depth_mid_cm']=(f.hzn_top+f.hzn_bot)/2
f['depth_band']=np.select([~f.depth_valid,f.hzn_top.eq(0)&f.hzn_bot.le(10),f.hzn_top.lt(10),f.depth_mid_cm.le(30),f.depth_mid_cm.le(100)],['invalid_or_missing','surface_0_to_10','crosses_or_starts_below_surface','midpoint_10_to_30','midpoint_30_to_100'],default='midpoint_over_100')
f['coordinates_present']=f.latitude_decimal_degrees.notna()&f.longitude_decimal_degrees.notna();f['coordinates_range_valid']=f.latitude_decimal_degrees.between(-90,90)&f.longitude_decimal_degrees.between(-180,180)
f['east_longitude_in_texas_source']=f.longitude_decimal_degrees.gt(0)
f['negative_any_chemistry']=f[SAT+WATER].lt(0).any(axis=1);f['ph_outside_0_14']=f.ph_saturated_paste.notna()&~f.ph_saturated_paste.between(0,14)
f['duplicate_pedon_depth']=f.duplicated(['pedon_key','hzn_top','hzn_bot'],keep=False)
f['method_signature']=f[[method(k) for k in SAT]].fillna('UNREPORTED').astype(str).agg('|'.join,axis=1)
save(f,'samples_wide.csv.gz')
long=[]
for k in SAT+WATER:
 cols=['labsampnum','pedon_key','site_key','pedlabsampnum','county_name','hzn_top','hzn_bot','prep_code','eight_complete','soil_name','soil_basis']
 x=f[cols].copy();x['field']=k;x['value']=f[k];x['method_code']=f[method(k)];x['extraction']='saturation_paste_or_extract' if k in SAT else 'water_extract';x['unit']=UNITS.get(k,'pH' if k=='ph_water_extract' else 'dS/m' if k=='ec_water_extract' else 'UNRESOLVED: ug/kg vs meq/L' if k=='sulfate_water_extractable' else 'ug/kg');x['status']=np.select([x.value.isna(),x.value.lt(0),x.value.eq(0)],['missing','negative_requires_review','reported_zero_not_proven_absence'],default='reported_numeric');x['detection_limit_known']=False;long.append(x)
save(pd.concat(long,ignore_index=True),'measurements_long.csv.gz')
complete=f[f.eight_complete].copy()
coverage=[]
for group in ['county_name','pedon_key','depth_band','prep_code','soil_basis']:
 for key,g in f.groupby(group,dropna=False):
  coverage.append({'group_type':group,'group':key,'layers':len(g),'pedons':g.pedon_key.nunique(),'eight_complete':int(g.eight_complete.sum()),'complete_fraction':float(g.eight_complete.mean()),**{k+'_measured':int(g[k].notna().sum()) for k in SAT}})
save(pd.DataFrame(coverage),'coverage_by_group.csv')
patterns=f[SAT].notna().astype(int).astype(str).agg(''.join,axis=1).value_counts().rename_axis('presence_pattern_in_SAT_order').reset_index(name='layers');save(patterns,'missingness_patterns.csv')
# Zero and negative values are preserved. Log plots exclude nonpositive observations explicitly.
stats=[]
for name,data in [('all_available',f),('eight_complete',complete)]:
 for k in SAT:
  a=data[k].dropna();q=a.quantile([.01,.05,.25,.5,.75,.95,.99]);stats.append({'population':name,'field':k,'unit':UNITS[k],'measured':len(a),'missing':int(data[k].isna().sum()),'zero':int(a.eq(0).sum()),'negative':int(a.lt(0).sum()),'min':a.min(),'q01':q.loc[.01],'q05':q.loc[.05],'q25':q.loc[.25],'median':q.loc[.5],'q75':q.loc[.75],'q95':q.loc[.95],'q99':q.loc[.99],'max':a.max(),'mean':a.mean(),'sd':a.std(),'skew':a.skew(),'positive_only_log10_skew':np.log10(a[a>0]).skew() if k!=SAT[0] else np.nan})
summary=pd.DataFrame(stats);save(summary,'descriptive_distributions.csv')
method_stats=[]
for k in SAT:
 for (code,prep),g in f.groupby([method(k),'prep_code'],dropna=False):
  a=g[k].dropna()
  if len(a):method_stats.append({'field':k,'method_code':code,'prep_code':prep,'n':len(a),'pedons':g.loc[a.index].pedon_key.nunique(),'median':a.median(),'q25':a.quantile(.25),'q75':a.quantile(.75),'zero':int(a.eq(0).sum()),'unit':UNITS[k]})
save(pd.DataFrame(method_stats),'distributions_by_method_preparation.csv');save(complete.groupby(['method_signature','prep_code'],dropna=False).agg(layers=('labsampnum','size'),pedons=('pedon_key','nunique')).reset_index(),'complete_method_signatures.csv')
# Descriptive bootstrap of equal-weight pedon medians, not statewide inference.
boot=[]
for pop,d in [('all_available',f),('eight_complete',complete)]:
 for k in SAT:
  v=d.groupby('pedon_key')[k].median().dropna().to_numpy();draw=np.empty(B)
  for i in range(B):draw[i]=np.median(rng.choice(v,size=len(v),replace=True))
  boot.append({'population':pop,'field':k,'pedons_with_measurement':len(v),'estimand':'median of observed pedon-specific medians','estimate':np.median(v),'bootstrap_percentile_2.5':np.quantile(draw,.025),'bootstrap_percentile_97.5':np.quantile(draw,.975),'replicates':B,'seed':SEED,'interpretation':'empirical pedon-resampling stability; not representative Texas confidence interval'})
save(pd.DataFrame(boot),'pedon_bootstrap_descriptives.csv')
# Complete-case layer rank associations, depth-adjusted residual ranks, and equal-weight pedon median associations.
cor=[];ped=complete.groupby('pedon_key')[SAT].median()
for a,b in itertools.combinations(SAT,2):
 layer=spearmanr(complete[a],complete[b]).statistic;pc=spearmanr(ped[a],ped[b]).statistic
 d=complete[complete.depth_valid];z=np.column_stack([np.ones(len(d)),rankdata(d.depth_mid_cm)]);x=rankdata(d[a]);y=rankdata(d[b]);rx=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ry=y-z@np.linalg.lstsq(z,y,rcond=None)[0];partial=np.corrcoef(rx,ry)[0,1]
 cor.append({'field_a':a,'field_b':b,'layer_n':len(complete),'layer_spearman':layer,'pedon_n':len(ped),'pedon_median_spearman':pc,'valid_depth_layers':len(d),'depth_partial_rank_correlation':partial,'warning':'pooled methods; no causal interpretation or independent-layer p-values'})
save(pd.DataFrame(cor),'correlations.csv')
method_corr=[]
for (sig,prep),g in complete.groupby(['method_signature','prep_code'],dropna=False):
 if g.pedon_key.nunique()<20:continue
 gp=g.groupby('pedon_key')[SAT].median()
 for a,b in itertools.combinations(SAT,2):method_corr.append({'signature':sig,'prep_code':prep,'field_a':a,'field_b':b,'pedons':len(gp),'spearman_pedon_medians':spearmanr(gp[a],gp[b]).statistic})
save(pd.DataFrame(method_corr),'correlations_by_method_preparation.csv')
# Partial observed ion inventory, NOT electroneutrality or validated charge-balance error.
complete['measured_cation_charge_meqL']=complete[['ca_satx','mg_satx','na_satx','k_satx']].sum(axis=1)
complete['measured_anion_charge_meqL']=complete[['cl_satx','so4_satx']].sum(axis=1)
complete['observed_charge_difference_meqL']=complete.measured_cation_charge_meqL-complete.measured_anion_charge_meqL
complete['inventory_status']='partial: bicarbonate/carbonate and other ions absent; not valid charge balance'
save(complete[['labsampnum','pedon_key','hzn_top','hzn_bot','measured_cation_charge_meqL','measured_anion_charge_meqL','observed_charge_difference_meqL','inventory_status']],'partial_ion_inventory.csv')
strata=[]
for (basis,name,classtype),g in f.groupby(['soil_basis','soil_name','soil_classType'],dropna=False):
 strata.append({'basis':basis,'name':name,'class_type':classtype,'layers':len(g),'pedons':g.pedon_key.nunique(),'complete':int(g.eight_complete.sum()),**{k+'_median':(g[k].dropna().median() if g[k].notna().any() else np.nan) for k in SAT}})
save(pd.DataFrame(strata),'soil_name_strata.csv')
# Sensitivity: nonnegative chemistry and valid depths; no values are clipped/imputed.
sensitivity=[];sensitivity_corr=[]
for label,g in [('complete_raw',complete),('complete_nonnegative',complete[~complete.negative_any_chemistry]),('complete_nonnegative_valid_depth',complete[~complete.negative_any_chemistry & complete.depth_valid]),('complete_nonnegative_valid_depth_unique_interval',complete[~complete.negative_any_chemistry & complete.depth_valid & ~complete.duplicate_pedon_depth])]:
 gp=g.groupby('pedon_key')[SAT].median()
 for k in SAT:sensitivity.append({'subset':label,'field':k,'layers':len(g),'pedons':len(gp),'layer_median':g[k].median(),'pedon_median_of_medians':gp[k].median()})
 for a,b in itertools.combinations(SAT,2):sensitivity_corr.append({'subset':label,'field_a':a,'field_b':b,'pedons':len(gp),'spearman_pedon_medians':spearmanr(gp[a],gp[b]).statistic})
save(pd.DataFrame(sensitivity),'qc_sensitivity_descriptives.csv');save(pd.DataFrame(sensitivity_corr),'qc_sensitivity_correlations.csv')
# QC flags never identify genuine repeats without provenance.
qc=f[['labsampnum','pedon_key','hzn_top','hzn_bot','depth_valid','coordinates_present','coordinates_range_valid','east_longitude_in_texas_source','duplicate_pedon_depth','negative_any_chemistry','ph_outside_0_14','locality_within_100m_boundary','locality_assignment_basis','locality_coordinate_accuracy_quantified']];save(qc,'sample_qc_flags.csv')
coord=f[f.coordinates_present].groupby(['latitude_decimal_degrees','longitude_decimal_degrees']).agg(layers=('labsampnum','size'),pedons=('pedon_key','nunique')).reset_index();save(coord,'coordinate_clusters.csv')
save(f.groupby(['pedon_key','hzn_top','hzn_bot'],dropna=False).agg(rows=('labsampnum','size'),sample_ids=('labsampnum',lambda s:'|'.join(s))).query('rows>1').reset_index(),'repeated_pedon_depth_groups.csv')
# Figures use observed data only and explicitly label units/populations.
plt.rcParams.update({'font.size':9,'figure.dpi':150})
fig,ax=plt.subplots(figsize=(9,4));ax.barh([LABELS[k] for k in SAT],[f[k].notna().mean()*100 for k in SAT],color='#246b78');ax.set(xlabel='Recorded measurements (% of 14,805 layers)',title='Texas NCSS: chemistry availability, not population coverage',xlim=(0,100));fig.tight_layout();fig.savefig(OUT/'measurement_availability.png');plt.close(fig)
fig,axes=plt.subplots(2,4,figsize=(14,7))
for ax,k in zip(axes.flat,SAT):
 base=f[k].dropna();base=base if k==SAT[0] else np.log10(base[base>0]);bins=np.histogram_bin_edges(base,bins=35)
 for pop,d,color in [('All measured',f,'#246b78'),('Eight-field complete',complete,'#bd7437')]:
  x=d[k].dropna();x=x if k==SAT[0] else np.log10(x[x>0]);ax.hist(x,bins=bins,density=True,alpha=.45,label=pop,color=color)
 ax.set(title=LABELS[k],xlabel=UNITS[k] if k==SAT[0] else 'log10('+UNITS[k]+'); positive only',ylabel='Density')
axes[0,0].legend(fontsize=7);fig.suptitle('Raw pH and positive-value log distributions; zeros excluded only from log plot');fig.tight_layout();fig.savefig(OUT/'distributions.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(7,6));im=ax.imshow(ped.corr(method='spearman'),vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks(range(8),[LABELS[k] for k in SAT],rotation=60,ha='right');ax.set_yticks(range(8),[LABELS[k] for k in SAT]);ax.set_title('Spearman: medians within 869 complete-panel pedons\nPooled methods; associations are not causal');fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(OUT/'pedon_correlations.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(9,6));g=f[f.coordinates_present];ax.scatter(g.longitude_decimal_degrees,g.latitude_decimal_degrees,s=5,c='#b7c2c6',alpha=.3,label='All recorded points');g=complete[complete.coordinates_present];ax.scatter(g.longitude_decimal_degrees,g.latitude_decimal_degrees,s=6,c='#246b78',alpha=.5,label='Eight-field complete');ax.set(xlabel='Reported longitude (degrees)',ylabel='Reported latitude (degrees)',title='Texas NCSS reported coordinates — no city or land-access claim');ax.legend();fig.tight_layout();fig.savefig(OUT/'recorded_coordinate_coverage_raw.png');ax.set_xlim(-107,-93);ax.set_ylim(25,37);ax.set_title('Regional zoom — 14 source rows with positive longitude lie outside view\nOriginal coordinates retained; not sign-corrected or city-validated');fig.tight_layout();fig.savefig(OUT/'recorded_coordinate_coverage.png');plt.close(fig)
qcsummary={'rows':len(f),'unique_samples':f.labsampnum.nunique(),'pedons':f.pedon_key.nunique(),'complete_rows':len(complete),'complete_pedons':complete.pedon_key.nunique(),'invalid_or_missing_depth_rows':int((~f.depth_valid).sum()),'negative_chemistry_rows':int(f.negative_any_chemistry.sum()),'ph_outside_0_14':int(f.ph_outside_0_14.sum()),'repeated_pedon_depth_rows':int(f.duplicate_pedon_depth.sum()),'unique_coordinate_pairs':len(coord),'coordinate_pairs_shared_by_multiple_pedons':int(coord.pedons.gt(1).sum()),'water_complete':int(f.water_eight_complete.sum()),'method_signatures_complete':complete.method_signature.nunique(),'soil_name_missing':int(f.soil_name.isna().sum()),'east_longitude_rows':int(f.east_longitude_in_texas_source.sum()),'near_boundary_complete':int(complete.locality_within_100m_boundary.eq('1').sum())}
(OUT/'qc_summary.json').write_text(json.dumps(qcsummary,indent=2));print(json.dumps(qcsummary,indent=2))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'texas_sources').rglob('*')) if p.is_file()};(OUT/'source_sha256.json').write_text(json.dumps(manifest,indent=2))
(OUT/'run_metadata.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'seed':SEED,'bootstrap_replicates':B,'input_rows':len(f),'scipy':__import__('scipy').__version__,'matplotlib':matplotlib.__version__},indent=2))
# Data-driven English report.
s=summary[summary.population=='all_available'].set_index('field');bs=pd.DataFrame(boot);co=pd.DataFrame(cor);ec=SAT[1];top=co.reindex(co.pedon_median_spearman.abs().sort_values(ascending=False).index).head(5)
lines=['# Texas NCSS soil-data study','', '## Scope and main findings',f'- {len(f):,} laboratory layers from {f.pedon_key.nunique():,} pedons; {len(complete):,} layers from {complete.pedon_key.nunique():,} pedons contain all eight saturation-panel variables. These are convenience/archive observations, not a representative Texas survey.',f'- EC is measured in {int(s.loc[ec,"measured"]):,} layers. Median {s.loc[ec,"median"]:.3g} dS/m; 5th–95th percentiles {s.loc[ec,"q05"]:.3g}–{s.loc[ec,"q95"]:.3g}; maximum {s.loc[ec,"max"]:.3g}. These describe archived extracts, not site-wide salinity.',f'- Saturation-paste pH median {s.loc[SAT[0],"median"]:.3g}, 5th–95th percentiles {s.loc[SAT[0],"q05"]:.3g}–{s.loc[SAT[0],"q95"]:.3g}. pH is only one part of chemistry.',f'- {qcsummary["method_signatures_complete"]} distinct eight-field method-code signatures occur among complete panels; pooled summaries cannot establish method equivalence.',f'- {qcsummary["negative_chemistry_rows"]} rows contain negative reported ion values (2 Ca, 62 Na, 62 K values, with overlapping rows). Their origin is unresolved; they are not interpreted as physical negative concentrations or silently set to zero. QC-excluded sensitivity outputs are provided.',f'- {qcsummary["invalid_or_missing_depth_rows"]} layers have missing/invalid thickness; {qcsummary["repeated_pedon_depth_rows"]} rows share a pedon/depth interval with another sample. These are flags, not proof of laboratory replication.',f'- {qcsummary["coordinate_pairs_shared_by_multiple_pedons"]} coordinate pairs are shared by multiple pedons; repeated coordinates do not prove independent sites or duplicate chemistry.','', '## Units, zeros and measurement status','Saturation ions retain mmol charge/L (meq/L), EC dS/m, and depths cm. No ion-to-molar conversion or cross-extraction harmonization is performed. Reported zeros remain zeros; they are not assumed true absence or replaced with half a detection limit. Detection-limit/censoring metadata are unavailable for these rows. Missing values remain null. Negative or impossible-pH values are flagged, not silently deleted. Log figures use positive values only and are not imputations. Water-extract observations remain separate; sulfate unit documentation is unresolved.','', '## Design and missingness','Coverage tables stratify by pedon, county, depth band, preparation and soil-name basis. Complete-case analyses may select particular methods, locations and profiles. Missingness patterns are tabulated, but no MCAR/MAR assumption or statewide extrapolation is made. Counties are not cities. Soil classification is selected from one labelled basis; names can be series, family, variant or taxadjunct. Detailed alternatives remain in the source snapshot.','', '## Depth, clustering and uncertainty','Raw complete panels retain reported negatives; separate sensitivity tables exclude negative chemistry, then invalid depth, then repeated pedon/depth intervals. These filters are documented analytical choices, not proof that flagged records are erroneous. Layer Spearman correlations are compared with depth-partial rank correlations and correlations of pedon medians. No independent-layer significance tests are reported. Depth adjustment is descriptive, not causal; it does not remove geology, management, method or site confounding. Method/preparation-stratified pedon correlations are supplied for groups with at least 20 pedons (a stability/display threshold, not a scientific compatibility threshold).','The bootstrap resamples equal-weight observed pedon medians 2,000 times (fixed seed 20261029), reporting the median of pedon medians and empirical percentile stability intervals. It does not estimate a representative statewide parameter, account for shared-location clusters, or include measurement uncertainty. Layer-weighted and pedon-weighted estimands differ.','', '### Strongest pooled pedon-median associations (descriptive)']
for _,r in top.iterrows():lines.append(f'- {r.field_a} vs {r.field_b}: Spearman {r.pedon_median_spearman:.3f}; layer {r.layer_spearman:.3f}; depth-partial rank {r.depth_partial_rank_correlation:.3f}.')
lines+=['','## Recorded distributions by variable','| Field | Measured layers | Median | 5th–95th percentile | Reported zeros | Negative values |','|---|---:|---:|---:|---:|---:|']
for k in SAT:
 a=s.loc[k];lines.append(f'| {LABELS[k]} ({UNITS[k]}) | {int(a.measured)} | {a["median"]:.3g} | {a.q05:.3g}–{a.q95:.3g} | {int(a.zero)} | {int(a.negative)} |')
lines+=['','## Ionic inventory, not charge balance','This is a full analysis of the downloaded chemistry panel, not every possible soil property: texture, mineralogy, organic carbon and bulk elemental composition were not included in this frozen query. The six saturation ions permit observed cation-charge and observed chloride+sulfate-charge sums in the same sample. Bicarbonate/carbonate and other ions are missing. The reported difference is a partial inventory diagnostic, NOT charge-balance error; no accept/reject tolerance is imposed and no electroneutrality claim is made.','', '## Spatial interpretation','Fourteen layers in Ochiltree pedon 21213 (two complete) report longitude +100.997083 at latitude 36.278332, inconsistent with a Texas location. They remain unchanged and flagged; a regional zoom and raw-coordinate inventory figure are both supplied. Recorded coordinates are plotted without interpolation. Census place assignments are exploratory coordinate-to-2025-boundary joins, not validated historical sample-city identity. Old coordinates can be approximate/centroids; accuracy is unquantified. Near-boundary flags, missing coordinates and outside-place cases remain. No result is assigned to an entire city, county or accessible collecting site.','', '## Phoenix comparison boundary','This study does not calculate Phoenix similarity. Missing ClO4 and NH4, extraction differences and unresolved method/unit details prevent a validated full-parameter match. No synthetic tolerances, ranking or crop-suitability model is introduced.','', '## Reproduce','Run `python analyze.py`, then `python test_study.py`. Dependencies are recorded in requirements.txt. Input public queries/scripts, frozen compressed snapshots and SHA-256 provenance are bundled. See outputs for tidy measurements, all-layer flags, distributions, method strata, missingness, soil strata, correlations and bootstrap results.']
(ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n')
