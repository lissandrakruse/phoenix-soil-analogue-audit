"""Original exploratory profile analysis. No full-similarity claim or probability."""
from pathlib import Path
import itertools,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
D=ROOT/'inputs'
O=ROOT/'outputs';O.mkdir(exist_ok=True)
manifest=json.loads((D/'checksums.json').read_text())
for name,h in manifest.items():
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==h,name
def rank_ties(values):
 return pd.Series(np.round(np.asarray(values,dtype=float),12)).rank(method='min').to_numpy()
s=pd.read_csv(D/'texas_all.csv',dtype={'labsampnum':'string','pedon_key':'string'})
t=pd.read_csv(D/'texas_pedon_taxonomy.csv',dtype={'pedon_key':'string'})
s=s.merge(t[['pedon_key','samp_name','corr_name','SSL_name']],on='pedon_key',validate='many_to_one')
l=pd.read_csv(D/'texas_sample_localities.csv',dtype={'labsampnum':'string','place_geoid':'string'})
s=s.merge(l[['labsampnum','place_geoid','place_label','locality_status']],on='labsampnum',validate='one_to_one')
qc=pd.read_csv(D/'sample_qc_flags.csv',dtype={'labsampnum':'string'})
s=s.merge(qc[['labsampnum','duplicate_pedon_depth','negative_any_chemistry','ph_outside_0_14','locality_within_100m_boundary']],on='labsampnum',validate='one_to_one')
methods=['ph_saturated_paste_method','electrical_cond_satx_method','ca_satx_method','mg_satx_method','na_satx_method','k_satx_method','cl_satx_method','so4_satx_method']
s['method_signature']=s[methods].fillna('not_reported').astype(str).agg('|'.join,axis=1)
p=pd.read_csv(D/'phoenix_reference_endpoint_ledger.csv')
p=p[p['sample'].isin(['Rosy Red','Sorceress 1','Sorceress 2'])].copy();p.to_csv(O/'phoenix_reference_endpoint_ledger.csv',index=False)
fields=['ca_satx','mg_satx','na_satx','k_satx','cl_satx','so4_satx']; ions=['Ca2+','Mg2+','Na+','K+','Cl-','SO4_total'];charge=np.array([2,2,1,1,1,2])
s['complete8']=s[['ph_saturated_paste','electrical_conductivity_satx']+fields].notna().all(axis=1)
s['texas_source_available_dimensions']=s[['ph_saturated_paste','electrical_conductivity_satx']+fields].notna().sum(axis=1)
all_source=s.copy()
rows=[];summaries=[];front=[]
for cohort in ['complete_eight_panel','maximal_profile_availability']:
 s=all_source.loc[all_source.complete8].copy() if cohort=='complete_eight_panel' else all_source.copy()
 s['east_longitude_in_texas_source']=s.longitude_decimal_degrees.gt(0)
 s['valid_depth']=s.hzn_bot.gt(s.hzn_top)&s.hzn_top.ge(0)
 strata={'all_depths':pd.Series(True,index=s.index),'valid_depth_no_duplicate_interval':s.valid_depth&~s.duplicate_pedon_depth,'strict_horizon_within_0_5cm':s.valid_depth&s.hzn_bot.le(5),'horizon_overlaps_0_5cm':s.valid_depth&s.hzn_top.lt(5)&s.hzn_bot.gt(0)}
 clr=lambda a: np.log(a)-np.log(a).mean(axis=-1,keepdims=True)
 for dim,label in [(4,'cation4'),(5,'cation4_plus_Cl_conditional'),(6,'six_ions_mixed_endpoint_conditional')]:
  valid=s[fields[:dim]].gt(0).all(axis=1)
  for st,sm in strata.items():
   z=s.loc[valid&sm].copy();x=z[fields[:dim]].to_numpy()/charge[:dim]; a=clr(x)
   for name in ['Rosy Red','Sorceress 1','Sorceress 2']:
    ref=p[(p['sample']==name)&p.analyte.isin(ions[:dim])].set_index('analyte').reindex(ions[:dim])
    v=ref.value.to_numpy()
    if not np.isfinite(v).all() or not (v>0).all():
     summaries.append(dict(cohort=cohort,profile=label,stratum=st,reference=name,status='reference_endpoint_unavailable',n_rows=len(z)));continue
    d=np.linalg.norm(a-clr(v),axis=1)
    q=z[['labsampnum','pedon_key','samp_name','corr_name','SSL_name','county_name','hzn_top','hzn_bot','place_geoid','place_label','locality_status','texas_source_available_dimensions','latitude_decimal_degrees','longitude_decimal_degrees','east_longitude_in_texas_source','method_signature','duplicate_pedon_depth','negative_any_chemistry','ph_outside_0_14','locality_within_100m_boundary']+fields+['ph_saturated_paste','electrical_conductivity_satx']].copy()
    q['cohort']=cohort;q['profile']=label;q['stratum']=st;q['reference']=name;q['distance']=d;q['rank_sample']=rank_ties(d).astype(int)
    # Rank pedons by best observed horizon only, explicitly no average/synthetic vector.
    best=q.groupby('pedon_key').distance.min();prank=pd.Series(rank_ties(best),index=best.index);q['rank_pedon_best_observed_horizon']=q.pedon_key.map(prank).astype(int)
    q['n_scored_horizons_this_pedon']=q.groupby('pedon_key').labsampnum.transform('size')
    q['availability_label']='Texas source availability only, NOT paired comparable endpoints';q['requested_dimensions']=10;q['profile_dimensions']=dim;q['independent_logratio_dimensions']=dim-1
    q['ClO4_status']='not_measured';q['NH4_status']='not_measured';q['full_similarity_status']='not_identifiable';q['protocol_equivalence']='unvalidated'
    q['sulfate_endpoint_status']='excluded' if dim<6 else 'conditional_total_titrated_sulfate_mixed_with_earlier_ISE_interval_not_joint_equilibrium_vector'
    lo=v-ref.uncertainty_minus.to_numpy();hi=v+ref.uncertainty_plus.to_numpy()
    ok=np.isfinite(lo).all() and np.isfinite(hi).all() and (lo>0).all()
    q['rank_tie_policy']='round distance to 12 decimals; competition rank';q['scenario_interpretation']='finite marginal-error corner scenarios only; NOT CI or continuous-box bounds';q['pedon_selection_warning']='best observed horizon favors more sampled horizons';q['reference_missing_requested_endpoints']={'Rosy Red':'measured EC','Sorceress 1':'sulfate; NH4 numeric result','Sorceress 2':'reliable pH; Mg upper error unresolved'}[name]
    q['reference_sensitivity_status']='deterministic_marginal_error_corners_NOT_confidence_interval' if ok else 'unresolved_Mg_upper_error_point_only'
    if ok:
     ds=[];rs=[];prs=[]
     for bits in itertools.product([0,1],repeat=dim):
      r=np.where(bits,hi,lo);dd=np.linalg.norm(a-clr(r),axis=1);ds.append(dd);rs.append(rank_ties(dd))
      b=pd.DataFrame({'p':q.pedon_key.to_numpy(),'d':dd}).groupby('p').d.min();b=pd.Series(rank_ties(b),index=b.index);prs.append(q.pedon_key.map(b).to_numpy())
     q['scenario_distance_min']=np.min(ds,axis=0);q['scenario_distance_max']=np.max(ds,axis=0)
     q['scenario_rank_min']=np.min(rs,axis=0);q['scenario_rank_max']=np.max(rs,axis=0)
     q['scenario_pedon_rank_min']=np.min(prs,axis=0);q['scenario_pedon_rank_max']=np.max(prs,axis=0)
    # Separate descriptive contrasts; no scalar mix, imputation or same-protocol claim.
    ph=p[(p['sample']==name)&p.analyte.eq('pH')&p.quantity.eq('pH')].value.iloc[0]
    ec=p[(p['sample']==name)&p.analyte.eq('EC_25C')].value.iloc[0]/1000
    q['descriptive_pH_difference_method_confounded']=q.ph_saturated_paste-ph
    q['descriptive_EC_ratio_method_confounded']=q.electrical_conductivity_satx/ec
    for j,ion in enumerate(ions[:dim]):q['clr_residual_'+ion]=a[:,j]-clr(v)[j]
    rows.append(q)
    leaders=q.sort_values(['rank_sample','labsampnum']).drop_duplicates('pedon_key').head(10);front.append(leaders)
    summaries.append(dict(cohort=cohort,profile=label,stratum=st,reference=name,status='computed_exploratory_only',n_rows=len(q),n_pedons=q.pedon_key.nunique(),excluded_missing_or_nonpositive=int((sm&~valid).sum()),excluded_missing=int((sm&s[fields[:dim]].isna().any(axis=1)).sum()),excluded_observed_nonpositive=int((sm&s[fields[:dim]].notna().all(axis=1)&s[fields[:dim]].le(0).any(axis=1)).sum()),best_sample=q.sort_values(['rank_sample','labsampnum']).iloc[0]['labsampnum'],minimum_distance=float(d.min()),n_corner_scenarios=2**dim if ok else 0))
    assert np.allclose(clr(x*13),a)
    assert q.requested_dimensions.eq(10).all() and q.full_similarity_status.eq('not_identifiable').all()
r=pd.concat(rows,ignore_index=True);r.to_csv(O/'profile_distances_all_strata_EXPLORATORY.csv.gz',index=False,compression={'method':'gzip','mtime':0})
pd.concat(front,ignore_index=True).to_csv(O/'closest_observed_profiles_by_distinct_pedon_EXPLORATORY.csv',index=False)
pd.DataFrame(summaries).to_csv(O/'profile_run_summary.csv',index=False)
# Within exactly the same scored sample set, assess 4 vs6 and reference sensitivity.
a=r[r.stratum.eq('all_depths')&r.cohort.eq('complete_eight_panel')];piv=a.pivot(index='labsampnum',columns=['profile','reference'],values='distance');piv.corr(method='spearman').to_csv(O/'rank_sensitivity_correlations.csv')
print(pd.DataFrame(summaries).to_string(index=False));print('PASS',len(r),'distance rows; raw inputs unchanged; no full match classification')
