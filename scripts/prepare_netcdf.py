"""Prepare a small, explicit C3S NetCDF subset for browser teaching.

Project: JupyterLite-C3S-Atlas. Author: project contributors (AI assisted).
Created/updated: 2026-11-15. Input: local licensed NetCDF; output: CSV + JSON.
Runtime: Python 3.11+; requirements-data.txt. No downloads or credentials.
Change log: initial explicit-selector export. Source files remain unmodified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import xarray as xr


def prepare(source: Path, output: Path, variable: str, start: str, end: str,
            lat_name: str, lon_name: str, north: float, west: float, south: float,
            east: float, member: str | None, member_dim: str | None,
            source_url: str, licence: str) -> dict:
    """Export monthly regional means on a regular grid with explicit metadata.

    The tool rejects extra dimensions, duplicate/nonmonthly times, irregular
    coordinates, wrapped boxes and incomplete spatial coverage. It performs no
    unit conversion, interpolation, anomaly calculation, or ensemble averaging.
    """
    if not (-90 < south < north < 90 and -180 <= west < east <= 180):
        raise ValueError('Use an increasing non-wrapping box within the poles.')
    if output.exists() or output.with_suffix('.json').exists():
        raise FileExistsError('Choose a new output name; existing exports are preserved.')
    with xr.open_dataset(source) as ds:
        data = ds[variable]
        if member_dim:
            if member is None:
                raise ValueError('An explicit member label is required.')
            data = data.sel({member_dim: member})
        if set(data.dims) != {'time', lat_name, lon_name}:
            raise ValueError(f'Select one member/level first. Unexpected dimensions: {data.dims}')
        units = data.attrs.get('units')
        if not units:
            raise ValueError('Missing units attribute: inspect and document the source first.')
        # Normalise geographic longitude without changing values; disallow duplicate seams.
        data = data.assign_coords({lon_name: ((data[lon_name]+180) % 360)-180}).sortby(lon_name).sortby(lat_name)
        for coord in [lat_name, lon_name]:
            arr = data[coord].values
            if len(arr) < 2 or not np.isfinite(arr).all() or not np.all(np.diff(arr) > 0) or not np.allclose(np.diff(arr), np.diff(arr)[0]):
                raise ValueError(f'{coord} must be a unique, regular, one-dimensional geographic grid.')
        data = data.sel(time=slice(start, end), **{lat_name: slice(south, north), lon_name: slice(west, east)})
        if any(data.sizes[k] == 0 for k in data.dims):
            raise ValueError('Selection contains no cells or dates.')
        if data.size > 5_000_000:
            raise ValueError('Subset too large for this teaching exporter; choose a smaller box/period.')
        values = data.load()
        if not np.isfinite(values.values).all():
            raise ValueError('Missing/masked cells need an explicit coverage policy. Choose a fully valid region or adapt deliberately.')
        weights = np.cos(np.deg2rad(data[lat_name]))
        series = data.weighted(weights).mean([lat_name, lon_name]).to_series()
        # Non-Gregorian calendars need an explicit conversion policy, never an implicit cast.
        import pandas as pd
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError('Non-standard calendar: document a calendar conversion before export.')
        months = series.index.to_period('M')
        if months.has_duplicates or not months.is_monotonic_increasing:
            raise ValueError('Expected one ascending observation per calendar month.')
        expected = pd.period_range(months[0], months[-1], freq='M')
        if not months.equals(expected):
            raise ValueError('Monthly coverage is incomplete.')
        frame = pd.DataFrame({'date': months.to_timestamp(), 'value': series.to_numpy()})
        metadata = dict(data_kind='real C3S-derived subset', source=source_url, variable=variable,
                        units=str(units), region=f'cell centres in N/W/S/E {north}/{west}/{south}/{east}',
                        statistic='cos(latitude)-weighted spatial mean of source monthly values',
                        reference_period='none; absolute source values', licence=licence,
                        transformations='longitude normalisation; explicit time/box/member selection; area mean; month-start labels',
                        source_file=source.name, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        source_attributes={k: str(v) for k, v in ds.attrs.items()},
                        variable_attributes={k: str(v) for k, v in data.attrs.items()},
                        selected_member=member, selected_period=[start, end],
                        actual_period=[str(frame.date.iloc[0].date()), str(frame.date.iloc[-1].date())],
                        selected_cells=int(data.sizes[lat_name]*data.sizes[lon_name]),
                        attribution='Contains modified Copernicus Climate Change Service information; retain source-file references.')
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False, date_format='%Y-%m-%d')
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--variable', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--lat-name', default='lat')
    parser.add_argument('--lon-name', default='lon')
    parser.add_argument('--box', type=float, nargs=4, metavar=('N', 'W', 'S', 'E'), required=True)
    parser.add_argument('--member')
    parser.add_argument('--member-dim')
    parser.add_argument('--source-url', default='https://doi.org/10.24381/cds.h35hb680')
    parser.add_argument('--licence', default='CC-BY-4.0; retain underlying source citations')
    args = parser.parse_args()
    fields = vars(args).copy()
    north, west, south, east = fields.pop('box')
    result = prepare(**fields, north=north, west=west, south=south, east=east)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
