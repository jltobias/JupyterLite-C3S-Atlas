"""Official-app links, monthly Pulse import, and auditable calendar summaries.

Project contributors (AI assisted), 2026-11-20. Pure Python/Pyodide; no network.
Live app links are navigation aids, not a guaranteed application API.
"""
from io import StringIO
import json
import re
from urllib.parse import urlencode
import numpy as np
import pandas as pd
from atlas_helpers import DATA
from pulse_helpers import ANOM, REL

PULSE_REGIONS = {'global':'global', 'nino12':'nino-1-2', 'nino3':'nino-3',
                 'nino34':'nino-3-4', 'nino4':'nino-4'}


def pulse_link(variable='sst', region='nino34', quantity='anomaly',
               aggregation='monthly', date='2026-10-01', map_quantity='anomaly'):
    """Build the official app's observed share parameters (checked 2026-11-20)."""
    if variable not in {'sst','t2m'} or region not in PULSE_REGIONS:
        raise ValueError('Use sst/t2m and a supported Pulse region.')
    if variable == 't2m' and region != 'global':
        raise ValueError('This helper supports global air temperature only.')
    if quantity not in {'absolute','anomaly','relative'} or map_quantity not in {'absolute','anomaly'}:
        raise ValueError('Unsupported quantity; relative is a time-series index, not a map field.')
    if quantity == 'relative' and (variable != 'sst' or region == 'global'):
        raise ValueError('Relative indices require a Niño SST region.')
    if aggregation not in {'daily','monthly','annual'}:
        raise ValueError('Choose daily, monthly, or annual.')
    if not isinstance(date,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):
        raise ValueError('Use an ISO date, YYYY-MM-DD.')
    stamp = pd.Timestamp(date)
    if stamp < pd.Timestamp('1979-01-01' if variable == 'sst' else '1940-01-01'):
        raise ValueError('Date precedes the displayed Pulse record.')
    if aggregation != 'daily' and stamp.day != 1:
        raise ValueError('Monthly and annual links use period-start dates.')
    if aggregation == 'annual' and stamp.month != 1:
        raise ValueError('Annual links use January 1.')
    return 'https://pulse.climate.copernicus.eu/?'+urlencode(dict(
        variable='2t' if variable == 't2m' else variable, region=PULSE_REGIONS[region],
        series=quantity, map=map_quantity, aggregation=aggregation, date=date))


def apps_catalogue():
    """Original teaching annotations plus sourced factual catalogue fields."""
    return json.loads((DATA/'apps/catalogue.json').read_text(encoding='utf-8'))


def complete_years(frame, column):
    """Day-weight monthly means; emit only complete 12-month, finite years."""
    df = frame[['date',column]].copy()
    if df.empty:
        raise ValueError('No monthly values provided.')
    df['date'] = pd.to_datetime(df.date, errors='raise')
    if df.date.isna().any() or df.date.duplicated().any() or not df.date.dt.is_month_start.all():
        raise ValueError('Use one dated value per month, on the first day.')
    if not np.isfinite(df[column]).all():
        raise ValueError('Monthly values must be finite.')
    rows=[]
    for year, part in df.groupby(df.date.dt.year):
        if set(part.date.dt.month) != set(range(1,13)):
            continue
        weights=part.date.dt.days_in_month
        rows.append(dict(year=int(year), value=float(np.average(part[column],weights=weights)),
                         months=12, days=int(weights.sum())))
    return pd.DataFrame(rows,columns=['year','value','months','days'])


def read_pulse_monthly_csv(raw):
    """Strict importer for Niño 3.4 monthly CSV exports, preserving raw bytes.

    Scope deliberately matches the worked import exercise. Reject unrelated regions,
    units, baselines, daily series and changed schemas instead of guessing conversions.
    """
    text=raw.decode('utf-8-sig')
    header='\n'.join(line for line in text.splitlines() if line.startswith('#'))
    expected = ['# Units: degC', '# Reference period: 1991-2020', '# Licence: CC-BY-4.0',
                '# Region: Nino 3.4 region;', '# Dates: first day of the month']
    if not all(item in header for item in expected):
        raise ValueError('Expected the official Niño 3.4 monthly degC/1991–2020/CC-BY-4.0 export header; review metadata.')
    df=pd.read_csv(StringIO(text),comment='#',parse_dates=['date'])
    columns=['sst','clim_1991_2020',ANOM,REL]
    if df.empty or not set(columns+['date']).issubset(df):
        raise ValueError('Monthly CSV schema is missing expected columns.')
    if df.date.isna().any() or not df.date.dt.is_month_start.all():
        raise ValueError('Expected month-start dates.')
    expected_dates=pd.date_range(df.date.iloc[0],df.date.iloc[-1],freq='MS')
    if not df.date.reset_index(drop=True).equals(pd.Series(expected_dates)):
        raise ValueError('Dates must be unique, ascending, and consecutive.')
    if not np.isfinite(df[columns]).all().all():
        raise ValueError('Monthly values must be finite.')
    if not np.allclose(df.sst-df.clim_1991_2020,df[ANOM],atol=.00011,rtol=0):
        raise ValueError('Absolute, climatology, and anomaly values disagree beyond rounding.')
    return df, header


def compare_pulse_exports(before, after):
    """Outer date join; separate new/removed rows from revisions to common rows."""
    columns=['sst','clim_1991_2020',ANOM,REL]
    joined=before[['date']+columns].merge(after[['date']+columns],on='date',how='outer',
        suffixes=('_before','_after'),indicator=True,validate='one_to_one').sort_values('date')
    joined['status']=joined['_merge'].map({'left_only':'removed','right_only':'new','both':'unchanged'}).astype(str)
    common=joined['_merge'].eq('both')
    changed=np.zeros(len(joined),dtype=bool)
    for col in columns:
        changed |= common.to_numpy() & ~np.isclose(joined[col+'_before'],joined[col+'_after'],atol=1e-8,rtol=0,equal_nan=True)
    joined.loc[changed,'status']='revised'
    joined['anomaly_delta']=joined[ANOM+'_after']-joined[ANOM+'_before']
    return joined
