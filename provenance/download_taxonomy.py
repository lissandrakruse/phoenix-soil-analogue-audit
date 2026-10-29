import urllib.request,json,csv,pathlib,hashlib,collections
from datetime import datetime, timezone
p=pathlib.Path(__file__).parent
fields=['cnn.pedon_key','cnn.site_key','cnn.pedlabsampnum','cnn.upedonid']
for prefix in ['samp','corr','SSL']:
 fields += ['cnn.'+prefix+'_'+s for s in ['name','class_type','classdate','classification_name','taxorder','taxsuborder','taxgrtgroup','taxsubgrp']]
q='SELECT '+','.join(fields)+" FROM lab_combine_nasis_ncss cnn INNER JOIN lab_area s ON cnn.state_key=s.area_key WHERE s.area_code='TX'"
(p/'taxonomy_query.sql').write_text(q)
r=urllib.request.urlopen(urllib.request.Request('https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest',data=json.dumps({'query':q,'format':'JSON+COLUMNNAME'}).encode(),headers={'Content-Type':'application/json'}),timeout=120)
s=r.read().decode();(p/'taxonomy_raw.json').write_text(s);t=json.loads(s)['Table'];rows=[dict(zip(t[0],x)) for x in t[1:]]
assert len(rows)==len(set(r['pedon_key'] for r in rows)), 'Duplicate pedon keys'
base=list(csv.DictReader(open(p/'texas_all.csv')));ids=set(r['pedon_key'] for r in base);rows=[r for r in rows if r['pedon_key'] in ids]
with open(p/'texas_pedon_taxonomy.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=t[0]);w.writeheader();w.writerows(rows)
byid={r['pedon_key']:r for r in rows};joined=[byid.get(r['pedon_key'],{}) for r in base]
summary={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'base_samples':len(base),'base_pedons':len(ids),'supplement_pedons':len(rows),'unmatched_pedons':sorted(ids-set(byid)),'nonempty_fields_pedons':{k:sum(bool(r[k]) for r in rows) for k in t[0][4:]},'nonempty_fields_samples':{k:sum(bool(r.get(k)) for r in joined) for k in t[0][4:]},'class_type_counts':{k:dict(collections.Counter(r[k] or '(missing)' for r in rows)) for k in ['samp_class_type','corr_class_type','SSL_class_type']}}
(p/'taxonomy_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print(json.dumps(rows[:2],indent=2))
