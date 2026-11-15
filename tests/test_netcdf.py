"""Test the desktop exporter with a known scientific fixture and a masked-cell failure."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

xr = pytest.importorskip('xarray')
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_netcdf', ROOT/'scripts/prepare_netcdf.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_known_regional_mean_and_metadata(tmp_path):
    values = np.array([[[0., 0.], [9., 9.]], [[3., 3.], [12., 12.]]])
    ds = xr.Dataset({'t': (('time', 'lat', 'lon'), values, {'units': 'degC'})},
                    coords={'time': pd.date_range('2000-01-01', periods=2, freq='MS'),
                            'lat': [0., 60.], 'lon': [0., 10.]}, attrs={'source': 'TEST FIXTURE'})
    source, output = tmp_path/'source.nc', tmp_path/'series.csv'
    ds.to_netcdf(source)
    kwargs = dict(variable='t', start='2000-01-01', end='2000-02-28', lat_name='lat', lon_name='lon',
                  north=61, south=-1, west=-1, east=11, member=None, member_dim=None,
                  source_url='https://example.test/fixture', licence='test fixture')
    metadata = module.prepare(source, output, **kwargs)
    np.testing.assert_allclose(pd.read_csv(output).value, [3, 6])
    assert metadata['units'] == 'degC' and metadata['source_attributes']['source'] == 'TEST FIXTURE'
    assert output.with_suffix('.json').exists()
    with pytest.raises(FileExistsError):
        module.prepare(source, output, **kwargs)
    ds.t.values[0, 0, 0] = np.nan
    ds.to_netcdf(tmp_path/'masked.nc')
    with pytest.raises(ValueError, match='coverage policy'):
        module.prepare(tmp_path/'masked.nc', tmp_path/'masked.csv', **kwargs)
