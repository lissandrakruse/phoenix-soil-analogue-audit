import urllib.request,json,pathlib,csv
root=pathlib.Path(__file__).parent
ions=['ph_saturated_paste','electrical_conductivity_satx','ca_satx','mg_satx','na_satx','k_satx','cl_satx','so4_satx']
water=['ph_water_extract','ec_water_extract','calcium_water_extractable','magnesium_water_extractable','sodium_water_extractable','potassium_water_extractable','chloride_water_extractable','sulfate_water_extractable']
base=" FROM lab_combine_nasis_ncss cnn INNER JOIN lab_pedon p ON p.pedon_key=cnn.pedon_key INNER JOIN lab_layer l ON l.pedon_key=p.pedon_key INNER JOIN lab_chemical_properties c ON c.labsampnum=l.labsampnum INNER JOIN lab_area s ON cnn.state_key=s.area_key LEFT JOIN lab_area ct ON cnn.county_key=ct.area_key WHERE s.area_code='TX'"
sel=['l.labsampnum','c.result_source_key','c.prep_code','cnn.pedon_key','cnn.site_key','p.pedlabsampnum','l.hzn_top','l.hzn_bot','l.hzn_desgn','cnn.upedonid','cnn.site_obsdate','cnn.latitude_decimal_degrees','cnn.longitude_decimal_degrees','s.area_name AS state_name','ct.area_name AS county_name']
methods=['ph_saturated_paste_method','electrical_cond_satx_method','ca_satx_method','mg_satx_method','na_satx_method','k_satx_method','cl_satx_method','so4_satx_method','ph_water_extract_method','water_extract_method']
q='SELECT '+','.join(sel+ions+methods+water)+base
(root/'query.sql').write_text(q)
data=json.dumps({'query':q,'format':'JSON+COLUMNNAME'}).encode()
r=urllib.request.urlopen(urllib.request.Request('https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest',data=data,headers={'Content-Type':'application/json'}),timeout=180)
s=r.read().decode();(root/'texas_raw.json').write_text(s)
t=json.loads(s)['Table'];rows=[dict(zip(t[0],x)) for x in t[1:]]
with (root/'texas_all.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=t[0]);w.writeheader();w.writerows(rows)
complete=[r for r in rows if all(r.get(k) is not None for k in ions)]
with (root/'texas_complete_saturation.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=t[0]);w.writeheader();w.writerows(complete)
summary={'rows':len(rows),'samples':len(set(r['labsampnum'] for r in rows)),'availability':{k:sum(r[k] is not None for r in rows) for k in ions+water},'saturation_complete_rows':len(complete),'saturation_complete_samples':len(set(r['labsampnum'] for r in complete)),'water_complete_rows':sum(all(r[k] is not None for k in water) for r in rows),'complete_counties':sorted(set(r['county_name'] or 'NULL' for r in complete))}
(root/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print(json.dumps(complete[:3],indent=2))
