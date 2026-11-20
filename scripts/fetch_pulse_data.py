"""Archive public Climate Pulse CSVs, unmodified, with file-level provenance.

Project contributors (AI assisted), 2026-11-20. Run explicitly to refresh; builds
never contact the upstream data service. Python standard library only.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://sites.ecmwf.int/data/climatepulse/timeseries/csv'
SPECS = [('sst', 'monthly', r) for r in ['nino12', 'nino3', 'nino34', 'nino4', '60S-60N_ocean']]
SPECS += [('t2m', 'monthly', 'global'), ('sst', 'daily', 'nino34')]


def fetch(spec):
    variable, aggregation, region = spec
    filename = f'timeseries_era5_{variable}_{aggregation}_{region}.csv'
    url = f'{BASE}/{aggregation}/{filename}'
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if b'# Licence: CC-BY-4.0' not in data or b'1991-2020' not in data:
        raise ValueError(f'Review changed licence or baseline before saving {url}')
    path = ROOT/'content/data/pulse'/filename
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(data)
    return dict(file='pulse/'+filename, url=url, bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                retrieved=datetime.now(timezone.utc).isoformat(),
                revision='Dated snapshot of a mutable public CSV; see original header',
                licence='CC-BY-4.0', licence_url='https://creativecommons.org/licenses/by/4.0/',
                attribution='Copernicus Climate Change Service (C3S), ECMWF, European Union; ERA5 teams',
                doi='10.24381/cds.adbb2d47' if aggregation == 'daily' else '10.24381/cds.f17050d7',
                transformations='None; original CSV bytes and metadata header retained')


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, SPECS))
    (ROOT/'content/data/pulse/manifest.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    print(f'Archived {len(records)} CSV files ({sum(r["bytes"] for r in records):,} bytes).')
