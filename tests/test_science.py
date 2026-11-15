"""Independent numeric checks and negative controls for the teaching utilities."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))
from atlas_helpers import anomalies, area_mean, load_monthly_csv, warming_levels


def test_area_weighted_mean_known_solution():
    # Equal-width rows centred at 0° and 60° have weights 1 and 1/2.
    assert area_mean(np.array([[0., 0.], [9., 9.]]), np.array([0., 60.])) == pytest.approx(3.)
    assert area_mean(np.array([[0., np.nan], [9., 9.]]), np.array([0., 60.])) == pytest.approx(4.5)


def test_no_missing_grid_becomes_zero():
    with pytest.raises(ValueError, match='No valid'):
        area_mean(np.full((2, 2), np.nan), np.array([0., 60.]))
    with pytest.raises(ValueError, match='equal latitude'):
        area_mean(np.ones((3, 2)), np.array([0., 10., 40.]))


def test_anomaly_baseline_and_incomplete_period():
    df = pd.DataFrame({'year': [2000]*12+[2001]*12, 'month': list(range(1, 13))*2,
                       't': list(range(12))+list(range(2, 14))})
    result = anomalies(df, 't', (2000, 2000))
    np.testing.assert_allclose(result.iloc[:12], 0)
    np.testing.assert_allclose(result.iloc[12:], 2)
    with pytest.raises(ValueError, match='every year/month'):
        anomalies(df.iloc[1:], 't', (2000, 2000))


def test_import_rejects_duplicates_gaps_and_infinity(tmp_path):
    path = tmp_path/'series.csv'
    for text in ['date,value\n2000-01-01,1\n2000-01-01,2\n',
                 'date,value\n2000-01-01,1\n2000-03-01,2\n',
                 'date,value\n2000-01-01,inf\n']:
        path.write_text(text)
        with pytest.raises(ValueError):
            load_monthly_csv(path)
    path.write_text('date,value\n2000-01-01,1\n2000-02-01,\n2000-03-01,3\n')
    assert load_monthly_csv(path).value.isna().sum() == 1


def test_real_gwl_tokens_are_not_dates():
    data = warming_levels()
    assert len(data) == 600  # Independent row/header count of the pinned 30×20 source.
    assert set(data.status) == {'window', 'NA', '9999'}
    assert data.loc[data.status != 'window', 'midpoint'].isna().all()
    known = data[(data.member == 'CCCma_CanESM5_r1i1p1f1') & (data.scenario == 'ssp585') & (data.level == 2)]
    assert known.iloc[0].start == 2013
    assert known.iloc[0].end == 2032
    assert known.iloc[0].midpoint == 2022.5
