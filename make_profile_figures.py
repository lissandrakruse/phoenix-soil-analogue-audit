from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/texas_profile_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd,numpy as np
R=Path(__file__).resolve().parent;O=R/'outputs'
d=pd.read_csv(O/'profile_distances_all_strata_EXPLORATORY.csv.gz');lead=pd.read_csv(O/'closest_observed_profiles_by_distinct_pedon_EXPLORATORY.csv')
plt.rcParams.update({'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False})
base=d[d.cohort.eq('complete_eight_panel')&d.reference.eq('Rosy Red')&d.profile.eq('cation4')]
fig,ax=plt.subplots(figsize=(9,4.8))
for name,label in [('all_depths','All depths'),('strict_horizon_within_0_5cm','Entire horizon within 0–5 cm')]:
 vals=np.sort(base.loc[base.stratum.eq(name),'distance']);ax.plot(vals,np.arange(1,len(vals)+1)/len(vals),label=f'{label} (n={len(vals):,})')
ax.set(xlabel='Four-cation log-ratio distance (not % similarity)',ylabel='Fraction of scored sample rows',title='Measured cation profile distances to Rosy Red\nComplete-eight-panel cohort');ax.legend();fig.tight_layout();fig.savefig(O/'profile_distance_distributions.png');plt.close(fig)
z=lead[lead.cohort.eq('complete_eight_panel')&lead.reference.eq('Rosy Red')&lead.profile.eq('cation4')&lead.stratum.eq('strict_horizon_within_0_5cm')].head(8)
fig,ax=plt.subplots(figsize=(10,5.5));y=np.arange(len(z));ax.hlines(y,z.scenario_rank_min,z.scenario_rank_max,color='#297c84',lw=3);ax.scatter(z.rank_sample,y,color='#ad532f',zorder=3,label='Point-reference rank');ax.set_yticks(y,z.labsampnum+' · '+z.samp_name.fillna('Not reported'));ax.invert_yaxis();ax.set(xlabel='Sample rank within strict shallow cohort',title='Reference-error scenarios change shallow-profile rankings\nComplete-eight-panel cohort · Rosy Red reference');ax.legend();fig.text(.02,.01,'Finite scenarios only—not confidence intervals or exhaustive bounds; extraction bias is unquantified.',fontsize=9);fig.tight_layout(rect=(0,.04,1,1));fig.savefig(O/'shallow_rank_scenarios.png');plt.close(fig)
# Profile shape of closest distinct pedons, normalized within only four cations.
fig,ax=plt.subplots(figsize=(9,5));ref=np.array([.55,2.9,1.4,.36]);ax.plot(['Ca','Mg','Na','K'],ref/ref.sum(),marker='o',color='black',lw=2.5,label='Phoenix Rosy Red (JGR Table 7)')
for _,row in z.head(4).iterrows():
 x=row[['ca_satx','mg_satx','na_satx','k_satx']].to_numpy(float)/[2,2,1,1];ax.plot(['Ca','Mg','Na','K'],x/x.sum(),marker='o',label=f'{row.labsampnum} · {row.samp_name}')
ax.set(ylabel='Molar fraction within Ca + Mg + Na + K only',title='Closest shallow cation profiles: relative shape, not soil equivalence\nComplete-eight-panel cohort · Rosy Red reference');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(O/'shallow_cation_profiles.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5));a=d[d.cohort.eq('complete_eight_panel')&d.reference.eq('Rosy Red')&d.stratum.eq('all_depths')];p=a.pivot(index='labsampnum',columns='profile',values='rank_sample').dropna();ax.scatter(p.cation4,p.six_ions_mixed_endpoint_conditional,s=4,alpha=.25);ax.set(xlabel='Four-cation sample rank',ylabel='Conditional mixed-endpoint six-ion rank',title='Endpoint sensitivity—not full-similarity validation\nComplete-eight-panel cohort · Rosy Red reference');fig.tight_layout();fig.savefig(O/'secondary_endpoint_rank_sensitivity.png');plt.close(fig)
# Public-facing table contains explicit source availability and missing-endpoint status.
z=lead[lead.cohort.eq('complete_eight_panel')&lead.reference.eq('Rosy Red')&lead.profile.eq('cation4')&lead.stratum.eq('strict_horizon_within_0_5cm')].copy()
z['joint_values_units']='Ca/Mg/Na/K/Cl/SO4 raw meq/L; EC dS/m; pH original';z['status']='Exploratory 4-cation profile only; full 10-endpoint similarity unknown'
z.to_csv(O/'shallow_closest_profiles_full_values_and_location.csv',index=False)
print('PASS four profile figures and full-values shallow table')
