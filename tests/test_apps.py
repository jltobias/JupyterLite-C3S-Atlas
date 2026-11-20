"""Independent checks for app navigation, annual aggregation, and export audits."""
from pathlib import Path
import sys
from urllib.parse import urlsplit, parse_qs
import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from app_helpers import pulse_link, complete_years, read_pulse_monthly_csv, compare_pulse_exports, apps_catalogue
from pulse_helpers import ANOM, REL


def test_official_pulse_query_semantics():
    query=parse_qs(urlsplit(pulse_link(quantity='relative')).query)
    assert query['region']==['nino-3-4']
    assert query['series']==['relative']
    assert query['map']==['anomaly']  # regional index is not a map variable
    assert parse_qs(urlsplit(pulse_link(variable='t2m',region='global')).query)['variable']==['2t']
    for args in [dict(variable='t2m'),dict(region='global',quantity='relative'),
                 dict(map_quantity='relative'),dict(aggregation='annual',date='2024-02-01'),
                 dict(date='2024-02-30'),dict(date='1970-01-01')]:
        with pytest.raises(ValueError):
            pulse_link(**args)


def test_day_weighted_leap_year_and_missing_month():
    frame=pd.DataFrame({'date':pd.date_range('2024-01-01','2025-02-01',freq='MS'),'x':0.})
    frame.loc[frame.date.eq('2024-02-01'),'x']=366/29
    result=complete_years(frame,'x')
    assert result.year.tolist()==[2024]
    assert result.iloc[0].value==pytest.approx(1.)
    assert result.iloc[0].days==366
    assert complete_years(frame.drop(index=1),'x').empty
    with pytest.raises(ValueError):
        complete_years(pd.concat([frame,frame.iloc[:1]]),'x')
    frame.loc[0,'x']=np.nan
    with pytest.raises(ValueError):
        complete_years(frame,'x')


def test_pulse_import_rejects_changed_meaning_and_broken_dates():
    raw=(ROOT/'content/data/pulse/timeseries_era5_sst_monthly_nino34.csv').read_bytes()
    frame,header=read_pulse_monthly_csv(raw)
    assert len(frame)==574 and '# Licence: CC-BY-4.0' in header
    for bad in [raw.replace(b'# Units: degC',b'# Units: K'),
                raw.replace(b'# Region: Nino 3.4 region;',b'# Region: Nino 4 region;'),
                raw.replace(b'# Reference period: 1991-2020',b'# Reference period: 1981-2010'),
                raw.replace(b'1979-02-01,',b'1979-01-01,')]:
        with pytest.raises(ValueError):
            read_pulse_monthly_csv(bad)


def test_export_comparison_separates_revision_addition_and_removal():
    before=pd.DataFrame({'date':pd.to_datetime(['2000-01-01','2000-02-01','2000-03-01']),
        'sst':[26.,27.,28.],'clim_1991_2020':[26.,26.,26.],ANOM:[0.,1.,2.],REL:[0.,.8,1.8]})
    after=before.iloc[1:].copy()
    after.loc[1,'sst']+=.1;after.loc[1,ANOM]+=.1
    new=after.iloc[-1:].copy();new['date']=pd.Timestamp('2000-04-01')
    after=pd.concat([after,new],ignore_index=True)
    result=compare_pulse_exports(before,after)
    assert result.status.tolist()==['removed','revised','unchanged','new']
    assert result.loc[result.status=='revised','anomaly_delta'].iloc[0]==pytest.approx(.1)
    assert result.loc[result.status.isin(['removed','new']),'anomaly_delta'].isna().all()


def test_catalogue_has_sources_and_explicit_empty_measurements():
    catalogue=apps_catalogue();entries=catalogue['entries']
    assert len(entries)==len({e['id'] for e in entries})==11
    assert {'climate-pulse','thermal-trace','weather-replay','methane-explorer','aerosol-alerts'}.issubset(e['id'] for e in entries)
    for app in entries:
        assert urlsplit(app['url']).scheme=='https'
        assert app['overview'].startswith(catalogue['source']+'overview?app=')
        assert app['exercise'] and app['limitation']
