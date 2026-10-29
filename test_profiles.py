import numpy as np,pandas as pd
from pathlib import Path
clr=lambda a:np.log(a)-np.log(a).mean(axis=-1,keepdims=True)
d=lambda x,r:np.linalg.norm(clr(x)-clr(r),axis=-1)
x=np.array([[1.,2.,3.,4.],[7.,2.,.5,6.]])
r=np.array([.55,2.9,1.4,.36])
assert np.allclose(d(x,r),d(13*x,7*r))
assert np.allclose(d(x,r),d(x[:,::-1],r[::-1]))
assert np.allclose(d(x,x),0)
# Pairwise logratio identity: equivalent Aitchison definition.
z=np.log(x/r);pair=(z[:,:,None]-z[:,None,:])**2
assert np.allclose(d(x,r)**2,pair.sum(axis=(1,2))/(2*x.shape[1]))
p=Path(__file__).resolve().parent
q=pd.read_csv(p/'outputs'/'profile_distances_all_strata_EXPLORATORY.csv.gz')
assert q[['labsampnum','cohort','profile','stratum','reference']].duplicated().sum()==0
assert (q.distance>=0).all() and np.isfinite(q.distance).all()
assert q.full_similarity_status.eq('not_identifiable').all()
assert q.protocol_equivalence.eq('unvalidated').all()
assert q.requested_dimensions.eq(10).all() and q.loc[q.cohort.eq('complete_eight_panel'),'texas_source_available_dimensions'].eq(8).all()
assert not ((q.reference=='Sorceress 1')&q.profile.str.startswith('six')).any()
assert q.loc[q.reference.eq('Sorceress 2'),'scenario_rank_min'].isna().all()
assert q.loc[q.reference.eq('Rosy Red'),'descriptive_EC_ratio_method_confounded'].isna().all()
assert q.loc[q.reference.eq('Sorceress 2'),'descriptive_pH_difference_method_confounded'].isna().all()
assert q.loc[q.stratum.eq('strict_horizon_within_0_5cm'),'hzn_bot'].le(5).all()
assert not q.loc[q.stratum.eq('valid_depth_no_duplicate_interval'),'duplicate_pedon_depth'].any()
print('PASS profile math, invariance, missing endpoints, strata, keys, status and no full-match assertions:',len(q))

assert len(q[q.cohort.eq('maximal_profile_availability') & q.profile.eq('cation4') & q.reference.eq('Rosy Red') & q.stratum.eq('all_depths')])==4251
for _,g in q.groupby(['cohort','profile','reference','stratum']):
 expected=pd.Series(np.round(g.distance.to_numpy(),12)).rank(method='min').to_numpy()
 assert np.array_equal(expected,g.rank_sample.to_numpy())
print('PASS maximal cohort and documented tie policy')
