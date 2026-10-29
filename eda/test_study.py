import unittest,json,gzip,hashlib
from pathlib import Path
import pandas as pd,numpy as np
from study_inputs import load_records,SAT,WATER
R=Path(__file__).resolve().parent;O=R/'outputs'
class StudyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.f=pd.read_csv(O/'samples_wide.csv.gz',low_memory=False,dtype={'labsampnum':str,'pedon_key':str})
 def test_sample_provenance(self):
  src=load_records();self.assertEqual(len(self.f),14805);self.assertEqual(self.f.labsampnum.nunique(),14805);self.assertEqual(set(self.f.labsampnum),{x['labsampnum'] for x in src})
  out=self.f.set_index('labsampnum')
  for r in src:
   for k in SAT+WATER:
    x=out.loc[r['labsampnum'],k]
    if r[k] is None:self.assertTrue(pd.isna(x))
    else:self.assertEqual(x,r[k])
 def test_complete_gate(self):self.assertEqual(int(self.f[SAT].notna().all(axis=1).sum()),3882);self.assertEqual(int(self.f[WATER].notna().all(axis=1).sum()),15)
 def test_qc(self):
  self.assertEqual(int(self.f[SAT+WATER].lt(0).any(axis=1).sum()),123);self.assertEqual(int((~self.f.depth_valid).sum()),175);self.assertEqual(int(self.f.duplicate_pedon_depth.sum()),277)
 def test_tidy_units_status(self):
  d=pd.read_csv(O/'measurements_long.csv.gz',low_memory=False);self.assertEqual(len(d),14805*16);self.assertFalse(d.duplicated(['labsampnum','field']).any());self.assertEqual(set(d.loc[d.field=='ca_satx','unit']),{'mmol charge/L (meq/L)'});self.assertEqual(int((d.status=='negative_requires_review').sum()),126);self.assertTrue(d.loc[d.value.isna(),'status'].eq('missing').all());self.assertTrue(d.loc[d.value.eq(0),'status'].eq('reported_zero_not_proven_absence').all())
 def test_bootstrap(self):
  d=pd.read_csv(O/'pedon_bootstrap_descriptives.csv');self.assertEqual(len(d),16);self.assertTrue(d.replicates.eq(2000).all());self.assertTrue((d['bootstrap_percentile_2.5']<=d.estimate).all());self.assertTrue((d['bootstrap_percentile_97.5']>=d.estimate).all())
 def test_inventory(self):
  d=pd.read_csv(O/'partial_ion_inventory.csv');self.assertEqual(len(d),3882);self.assertTrue(d.inventory_status.str.contains('not valid charge balance').all());self.assertTrue(np.allclose(d.measured_cation_charge_meqL-d.measured_anion_charge_meqL,d.observed_charge_difference_meqL))
 def test_sensitivity(self):
  d=pd.read_csv(O/'qc_sensitivity_descriptives.csv');self.assertEqual(d.loc[d.subset=='complete_nonnegative','layers'].unique().tolist(),[3759]);self.assertTrue(d.groupby('subset').size().eq(8).all())
 def test_geographic_flag(self):
  self.assertEqual(int(self.f.east_longitude_in_texas_source.sum()),14);self.assertEqual(set(self.f.loc[self.f.east_longitude_in_texas_source,'pedon_key']),{'21213'})
 def test_input_hashes(self):
  for path,h in json.loads((O/'source_sha256.json').read_text()).items():self.assertEqual(hashlib.sha256((R/path).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main(verbosity=2)
