"""Restore and verify byte-identical frozen public inputs; no network required."""
from pathlib import Path
import gzip,json,hashlib
root=Path(__file__).resolve().parent/'inputs'
for name,expected in json.loads((root/'checksums.json').read_text()).items():
    data=gzip.decompress((root/(name+'.gz')).read_bytes())
    if hashlib.sha256(data).hexdigest()!=expected: raise ValueError('Checksum mismatch: '+name)
    (root/name).write_bytes(data)
print('All frozen inputs restored and verified.')
