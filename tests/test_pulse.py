"""Independent edge cases for calendar statistics and Pacific geometry."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))
from pulse_helpers import load_pulse, complete_months, rank_same_month, region_geojson, REGIONS, ANOM


def test_pulse_source_integrity_and_known_snapshot():
    manifest = json.loads((ROOT/'content/data/pulse/manifest.json').read_text(encoding='utf-8'))
    assert len(manifest) == 7
    for record in manifest:
        raw = (ROOT/'content/data'/record['file']).read_bytes()
        assert len(raw) == record['bytes']
        assert hashlib.sha256(raw).hexdigest() == record['sha256']
        assert b'# Licence: CC-BY-4.0' in raw
    for region in REGIONS:
        assert len(load_pulse(region)) == 574
    assert len(load_pulse('60S-60N_ocean')) == 574
    assert len(load_pulse('global', variable='t2m')) == 1042
    df = load_pulse()
    assert df.iloc[-1][ANOM] == 3.2345
    assert rank_same_month(df, '2026-10-01')['n'] == 48
    assert load_pulse(aggregation='daily').date.max() == pd.Timestamp('2026-11-18')


def test_same_month_tied_rank_not_all_months():
    frame = pd.DataFrame({'date': pd.to_datetime(['2000-01-01','2000-02-01','2001-01-01','2002-01-01']), ANOM: [2., 99., 2., 4.]})
    result = rank_same_month(frame, '2000-01-01')
    assert (result['rank'], result['n'], result['ties']) == (2, 3, 2)
    with pytest.raises(ValueError):
        rank_same_month(frame, '1999-01-01')


def test_complete_leap_month_and_partial_month_rejection():
    frame = pd.DataFrame({'date': pd.date_range('2024-02-01','2024-03-05'), ANOM: 2.})
    result = complete_months(frame)
    assert len(result) == 1
    assert result.iloc[0]['count'] == 29
    assert result.iloc[0]['mean'] == 2
    assert complete_months(frame.drop(index=4)).empty
    with pytest.raises(ValueError, match='unique'):
        complete_months(pd.concat([frame,frame.iloc[:1]]))
    frame.loc[0,ANOM] = np.nan
    with pytest.raises(ValueError, match='finite'):
        complete_months(frame)


def test_antimeridian_geojson_and_regional_values():
    collection = region_geojson()
    assert len(collection['features']) == 4
    nino4 = collection['features'][-1]
    assert nino4['geometry']['type'] == 'MultiPolygon'
    rings = [polygon[0] for polygon in nino4['geometry']['coordinates']]
    assert rings[0][0] == [160, -5]
    assert rings[0][2] == [180, 5]
    assert rings[1][0] == [-180, -5]
    assert rings[1][2] == [-150, 5]
    assert sum(max(p[0] for p in r)-min(p[0] for p in r) for r in rings) == 50
    for ring in rings:
        assert ring[0] == ring[-1]
        signed = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))
        assert signed > 0  # exterior rings counterclockwise
    nino34 = collection['features'][2]['properties']
    assert nino34['anomaly_c'] == 3.2345
    assert nino34['relative_c'] == 2.6089
    assert nino34['baseline'] == '1991-2020'
    with pytest.raises(ValueError):
        region_geojson('2026-11-01')
