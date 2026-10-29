"""Download optional original Census archive for locality regeneration, verifying its hash."""
from pathlib import Path
import urllib.request,hashlib
URL='https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_48_place.zip'
EXPECTED='5a0c4d49641f69028ee9f5c343bf09936ec00a378e5e6393115b106bab935e13'
b=urllib.request.urlopen(URL,timeout=120).read()
if hashlib.sha256(b).hexdigest()!=EXPECTED: raise ValueError('Census archive checksum changed; refusing substitution')
(Path(__file__).resolve().parent/'tl_2025_48_place.zip').write_bytes(b)
print('Verified original Census archive downloaded.')
