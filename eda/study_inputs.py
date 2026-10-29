"""Standalone public-input loader: exact identifiers, hashes and source values.
New study code; no application, solver, or third-party upstream code imported.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,functools
ROOT=Path(__file__).resolve().parent
SAT=['ph_saturated_paste','electrical_conductivity_satx','ca_satx','mg_satx','na_satx','k_satx','cl_satx','so4_satx']
WATER=['ph_water_extract','ec_water_extract','calcium_water_extractable','magnesium_water_extractable','sodium_water_extractable','potassium_water_extractable','chloride_water_extractable','sulfate_water_extractable']
NUMERIC=set(SAT+WATER+['hzn_top','hzn_bot','latitude_decimal_degrees','longitude_decimal_degrees'])
def verified_source(path, expected_bytes, expected_sha256, compressed_sha256):
    """Accept exact plain CSV only when its gzip archive is absent; never repair bytes."""
    path=Path(path)
    if path.is_file():
        packed=path.read_bytes()
        if hashlib.sha256(packed).hexdigest()!=compressed_sha256:
            raise ValueError('Compressed checksum mismatch: '+path.name)
        with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
            raw=stream.read(expected_bytes+1)
    else:
        plain=path.with_suffix('')
        if not plain.is_file():raise FileNotFoundError('Missing verified input: '+str(path)+' or '+str(plain))
        with plain.open('rb') as stream:raw=stream.read(expected_bytes+1)
    if len(raw)!=expected_bytes or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Source checksum/size mismatch: '+path.name)
    return raw

@functools.lru_cache(maxsize=1)
def load_records():
    meta=json.loads((ROOT/'texas_sources/checksum.json').read_text())
    raw=verified_source(ROOT/'texas_sources/texas_all.csv.gz',meta['bytes'],meta['sha256'],meta['compressedSha256'])
    rows=[]
    for source in csv.DictReader(io.StringIO(raw.decode())):
        row={k:(None if v.strip() in ('','NULL') else float(v) if k in NUMERIC else v) for k,v in source.items()}
        row.update(perchlorate=None,ammonium=None,source='USDA NCSS SCD',state='Texas',country='USA')
        rows.append(row)
    if len({r['labsampnum'] for r in rows})!=len(rows):raise ValueError('Duplicate sample identity')
    validation=json.loads((ROOT/'texas_sources/locality_validation.json').read_text())
    locality_raw=verified_source(ROOT/'texas_sources/texas_sample_localities.csv.gz',3099795,validation['output_sha256'],'be4259be136532b7a0253e417f40514ffb9ad5ab1b1b952e23cd7b33ae38caad')
    if hashlib.sha256(locality_raw).hexdigest()!=validation['output_sha256']:raise ValueError('Locality checksum mismatch')
    if meta['sha256']!=validation['input_sha256']:raise ValueError('Locality input mismatch')
    localities={r['labsampnum']:r for r in csv.DictReader(io.StringIO(locality_raw.decode()))}
    if len(localities)!=len(rows):raise ValueError('Locality identity count mismatch')
    for row in rows:
        loc=localities[row['labsampnum']]
        if any(loc[k]!=row[k] for k in ['pedon_key','site_key']):raise ValueError('Locality identity mismatch')
        for k in ['latitude_decimal_degrees','longitude_decimal_degrees']:
            if (float(loc[k]) if loc[k] else None)!=row[k]:raise ValueError('Locality coordinate mismatch')
        row['locality']={k:v or None for k,v in loc.items() if k not in ['labsampnum','pedon_key','site_key','latitude_decimal_degrees','longitude_decimal_degrees','county_name']}
    taxroot=ROOT/'texas_sources/taxonomy'
    taxmeta=json.loads((taxroot/'checksum.json').read_text())
    taxraw=verified_source(taxroot/'texas_pedon_taxonomy.csv.gz',taxmeta['bytes'],taxmeta['sha256'],taxmeta['compressedSha256'])
    taxrows=list(csv.DictReader(io.StringIO(taxraw.decode())))
    taxonomy={r['pedon_key']:r for r in taxrows}
    if len(taxonomy)!=len(taxrows):raise ValueError('Duplicate taxonomy pedon')
    for row in rows:
        tax=taxonomy[row['pedon_key']]
        if any(tax[k]!=row[k] for k in ['site_key','pedlabsampnum','upedonid']):raise ValueError('Taxonomy identity mismatch')
        tax={k:(v if v.strip() not in ('','NULL') else None) for k,v in tax.items()}
        basis=next((prefix for prefix in ['corr','samp','SSL'] if tax[prefix+'_name']),None)
        row['soil']={'name':tax[basis+'_name'] if basis else None,'classification':tax[basis+'_classification_name'] if basis else None,'classType':tax[basis+'_class_type'] if basis else None,'date':tax[basis+'_classdate'] if basis else None,'basis':{'corr':'correlated','samp':'sampled_as','SSL':'laboratory'}.get(basis),'source':'USDA NCSS pedon taxonomy','original':tax}
    return rows
