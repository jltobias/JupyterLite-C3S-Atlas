"""Fetch unmodified public reference files and record provenance.

Project: JupyterLite-C3S-Atlas; author: project contributors (AI assisted).
Created/updated: 2026-11-15. Inputs: public HTTPS sources below.
Outputs: content/data/reference/*, content/data/manifest.json, third-party licences.
Runtime: Python 3.11+ standard library. No credentials or analytical transformations.
Change log: 2026-11-15 - initial source-preserving downloader.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def get(url: str) -> bytes:
    """Read a public HTTPS resource; propagate errors without substituting data."""
    with urlopen(Request(url, headers={'User-Agent': 'JupyterLite-C3S-Atlas-education'}), timeout=90) as response:
        return response.read()


def main() -> None:
    """Preserve source bytes and snapshot identities for browser-ready reference data."""
    atlas_sha = json.loads(get('https://api.github.com/repos/ecmwf-projects/c3s-atlas/commits/main'))['sha']
    coast_sha = json.loads(get('https://api.github.com/repos/nvkelso/natural-earth-vector/commits/master'))['sha']
    sources = [
        ('CMIP6_WarmingLevels.csv', f'https://raw.githubusercontent.com/ecmwf-projects/c3s-atlas/{atlas_sha}/auxiliar/GWLs/CMIP6_WarmingLevels.csv', 'Apache-2.0 (upstream repository)', 'European Union; C3S Atlas User Tools contributors; underlying CMIP6 modelling groups', atlas_sha),
        ('ne_110m_coastline.geojson', f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{coast_sha}/geojson/ne_110m_coastline.geojson', 'Public domain', 'Natural Earth; Nathaniel Vaughn Kelso, Tom Patterson and contributors', coast_sha),
        ('atlas-catalogue.json', 'https://cds.climate.copernicus.eu/api/catalogue/v1/collections/multi-origin-c3s-atlas', 'CC-BY-4.0 (catalogue dataset licence)', 'Copernicus Climate Change Service / ECMWF', 'catalogue snapshot'),
    ]
    folder = ROOT / 'content/data/reference'
    folder.mkdir(parents=True, exist_ok=True)
    manifest = []
    for filename, url, licence, attribution, revision in sources:
        data = get(url)
        (folder / filename).write_bytes(data)
        manifest.append(dict(file=f'reference/{filename}', url=url, licence=licence,
                             attribution=attribution, revision=revision,
                             retrieved='2026-11-15', sha256=hashlib.sha256(data).hexdigest(),
                             bytes=len(data), transformations='None; original bytes'))
        print(f'{filename}: {len(data):,} bytes')
    (folder.parent / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    licences = ROOT / 'licenses'
    licences.mkdir(exist_ok=True)
    for filename, url in [
        ('C3S-Atlas-Apache-2.0.txt', f'https://raw.githubusercontent.com/ecmwf-projects/c3s-atlas/{atlas_sha}/LICENSE'),
        ('Natural-Earth.md', f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{coast_sha}/LICENSE.md'),
    ]:
        (licences / filename).write_bytes(get(url))


if __name__ == '__main__':
    main()
