#!/usr/bin/env python3
"""Rebuild public NCSS sample to frozen Census-2025 Texas-place join. No credentials."""
import argparse,csv,json,hashlib,urllib.request,zipfile,math,collections
from pathlib import Path
import shapefile,shapely,pyproj
from shapely.geometry import shape,Point
from shapely.ops import transform
from shapely.strtree import STRtree
URL='https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_48_place.zip'
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path(__file__).resolve().parent.parent/'texas_all.csv');p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
z=a.output/'tl_2025_48_place.zip'
if not z.exists(): urllib.request.urlretrieve(URL,z)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected='5a0c4d49641f69028ee9f5c343bf09936ec00a378e5e6393115b106bab935e13'
assert sha(z)==expected,'Frozen Census file SHA256 mismatch; review a changed source before use'
reader=shapefile.Reader(str(z)); records=[r.as_dict() for r in reader.records()];geoms=[shape(s.__geo_interface__) for s in reader.shapes()]
assert all(g.is_valid for g in geoms),'Invalid source geometry: do not silently repair'
prj=zipfile.ZipFile(z).read('tl_2025_48_place.prj').decode();crs=pyproj.CRS.from_wkt(prj)
xy=pyproj.Transformer.from_crs('EPSG:4326',crs,always_xy=True)
metric=pyproj.Transformer.from_crs(crs,'EPSG:3083',always_xy=True)
tree=STRtree(geoms);boundaries=[transform(metric.transform,g.boundary) for g in geoms];btree=STRtree(boundaries)
rows=list(csv.DictReader(a.input.open()));assert len({r['labsampnum'] for r in rows})==len(rows),'sample IDs not unique'
chem=['ph_saturated_paste','electrical_conductivity_satx','ca_satx','mg_satx','na_satx','k_satx','cl_satx','so4_satx']
fields=['labsampnum','pedon_key','site_key','latitude_decimal_degrees','longitude_decimal_degrees','county_name','complete_eight_parameters','locality_status','place_geoid','place_name','place_label','place_type','place_classfp','boundary_year','geometry_source_url','boundary_distance_m','within_100m_boundary','assignment_basis','coordinate_accuracy_quantified']
cache={};out=[]
for r in rows:
 key=(r['longitude_decimal_degrees'],r['latitude_decimal_degrees'])
 if key not in cache:
  d=dict.fromkeys(fields[7:],'');d.update(locality_status='missing',boundary_year=2025,geometry_source_url=URL,assignment_basis='coordinate_based_screening_not_verified_sample_location',coordinate_accuracy_quantified=0)
  if all(key):
   lon,lat=map(float,key)
   if not(math.isfinite(lon) and math.isfinite(lat) and -180<=lon<=180 and -90<=lat<=90): d['locality_status']='invalid_coordinates'
   else:
    pt=Point(*xy.transform(lon,lat));hits=[int(i) for i in tree.query(pt,predicate='intersects')]
    d['locality_status']='outside' if not hits else ('inside' if len(hits)==1 and geoms[hits[0]].contains(pt) else 'ambiguous')
    if len(hits)==1:
     q=records[hits[0]];d.update(place_geoid=q['GEOID'],place_name=q['NAME'],place_label=q['NAMELSAD'],place_classfp=q['CLASSFP'],place_type={'G4110':'incorporated_place','G4210':'census_designated_place'}.get(q['MTFCC'],q['MTFCC']))
    elif len(hits)>1:
     d.update(place_geoid='|'.join(records[i]['GEOID'] for i in hits),place_name='|'.join(records[i]['NAME'] for i in hits),place_type='ambiguous_multiple')
    mpt=transform(metric.transform,pt);dist=mpt.distance(boundaries[int(btree.nearest(mpt))]);d.update(boundary_distance_m=round(dist,1),within_100m_boundary=int(dist<=100))
  cache[key]=d
 result={k:r[k] for k in fields[:6]};result['complete_eight_parameters']=int(all(r[c]!='' for c in chem));result.update(cache[key]);out.append(result)
def save(name,values,columns):
 with (a.output/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(values)
save('texas_sample_localities.csv',out,fields)
groups={}
for r in out:
 if r['locality_status']!='inside':continue
 k=r['place_geoid'];g=groups.setdefault(k,dict(place_geoid=k,place_name=r['place_name'],place_label=r['place_label'],place_type=r['place_type'],boundary_year=2025,sample_count=0,complete_eight_sample_count=0,pedons=set(),complete_pedons=set(),counties=set(),near_boundary_sample_count=0))
 g['sample_count']+=1;g['complete_eight_sample_count']+=r['complete_eight_parameters'];g['pedons'].add(r['pedon_key']);g['counties'].add(r['county_name']);g['near_boundary_sample_count']+=r['within_100m_boundary']
 if r['complete_eight_parameters']:g['complete_pedons'].add(r['pedon_key'])
coverage=[]
for g in groups.values():
 g['pedon_count']=len(g.pop('pedons'));g['complete_eight_pedon_count']=len(g.pop('complete_pedons'));g['source_counties']='|'.join(sorted(x for x in g.pop('counties') if x));coverage.append(g)
coverage.sort(key=lambda x:(x['place_name'],x['place_geoid']));save('texas_locality_coverage.csv',coverage,list(coverage[0]))
summary={'input_rows':len(rows),'unique_sample_ids':len(out),'unique_coordinate_pairs_including_missing':len(cache),'source_place_polygons':len(geoms),'status_all':dict(collections.Counter(r['locality_status'] for r in out)),'status_complete_eight':dict(collections.Counter(r['locality_status'] for r in out if r['complete_eight_parameters'])),'places_with_samples':len(coverage),'places_with_complete_eight':sum(g['complete_eight_sample_count']>0 for g in coverage),'within_100m_boundary_all':sum(r['within_100m_boundary']==1 for r in out),'within_100m_boundary_complete':sum(r['within_100m_boundary']==1 and r['complete_eight_parameters'] for r in out),'boundary_source_url':URL,'boundary_sha256':sha(z),'input_sha256':sha(a.input),'output_sha256':sha(a.output/'texas_sample_localities.csv'),'input_crs':'EPSG:4326 assumed for standardized decimal degrees; per-record datum unavailable; legacy-location uncertainty remains','polygon_crs':crs.to_string(),'distance_crs':'EPSG:3083; approximate metres','versions':{'shapely':shapely.__version__,'pyproj':pyproj.__version__,'pyshp':shapefile.__version__}}
(a.output/'locality_validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
