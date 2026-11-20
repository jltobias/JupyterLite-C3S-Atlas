"""Small, auditable Climate Pulse readers and geographic teaching views.

Project contributors (AI assisted), 2026-11-20. Inputs: unchanged C3S CSVs;
outputs: derived tables/Plotly figures/GeoJSON. No network or credentials.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from atlas_helpers import DATA, coastlines

REGIONS = {
    'nino12': dict(name='Niño 1+2', west=-90, east=-80, south=-10, north=0),
    'nino3': dict(name='Niño 3', west=-150, east=-90, south=-5, north=5),
    'nino34': dict(name='Niño 3.4', west=-170, east=-120, south=-5, north=5),
    'nino4': dict(name='Niño 4', west=160, east=-150, south=-5, north=5),
}
ANOM = 'anom_1991_2020'
REL = 'rnino_anom_1991_2020'
CREDIT = 'Copernicus Climate Change Service (C3S) / ECMWF / European Union; ERA5'
BASE = 'https://jltobias.github.io/JupyterLite-C3S-Atlas/'


def load_pulse(region='nino34', aggregation='monthly', variable='sst'):
    """Read a known snapshot, validate dates/schema, keep preliminary status."""
    name = f'timeseries_era5_{variable}_{aggregation}_{region}.csv'
    manifest = json.loads((DATA/'pulse/manifest.json').read_text(encoding='utf-8'))
    if 'pulse/'+name not in {x['file'] for x in manifest}:
        raise ValueError('Choose a series listed in the bundled Pulse manifest.')
    df = pd.read_csv(DATA/'pulse'/name, comment='#', parse_dates=['date'])
    needed = [variable, 'clim_1991_2020', ANOM] + ([REL] if region in REGIONS else [])
    if not set(needed).issubset(df) or not np.isfinite(df[needed].to_numpy()).all():
        raise ValueError('Required values are missing or nonfinite.')
    dates = pd.date_range(df.date.iloc[0], df.date.iloc[-1], freq='MS' if aggregation == 'monthly' else 'D')
    if not df.date.reset_index(drop=True).equals(pd.Series(dates)):
        raise ValueError('Source dates must be unique, ascending, and gap-free.')
    if not np.allclose(df[variable]-df.clim_1991_2020, df[ANOM], atol=0.00011, rtol=0):
        raise ValueError('Absolute, climatology, and anomaly columns disagree.')
    return df.assign(year=df.date.dt.year, month=df.date.dt.month)


def complete_months(daily, column=ANOM):
    """Equal-day monthly averages; exclude incomplete months, never zero-fill.

    This aggregates the supplied daily statistic, not necessarily the producer's
    monthly product. In this snapshot daily SST notes specify 12 UTC values.
    """
    df = daily[['date', column]].copy()
    df['date'] = pd.to_datetime(df.date)
    if df.date.duplicated().any() or not df.date.dt.normalize().equals(df.date):
        raise ValueError('One unique midnight date per daily value is required.')
    if not np.isfinite(df[column]).all():
        raise ValueError('Daily values must be finite.')
    result = df.set_index('date')[column].resample('MS').agg(['mean', 'count'])
    result['expected'] = result.index.days_in_month
    return result[result['count'] == result.expected].reset_index()


def rank_same_month(df, date, column=ANOM):
    """Competition rank (ties share rank), across matching calendar months only."""
    date = pd.Timestamp(date)
    selected = df.loc[df.date == date, column]
    if len(selected) != 1 or not np.isfinite(selected.iloc[0]):
        raise ValueError('Select one finite, existing monthly value.')
    peers = df.loc[(df.date.dt.month == date.month) & df[column].notna(), column]
    value = float(selected.iloc[0])
    return dict(value=value, rank=int((peers > value).sum()+1), n=len(peers),
                ties=int((peers == value).sum()), rule='1 + number strictly warmer; same calendar month')


def region_rings(region):
    """RFC 7946 longitude/latitude rings, cut at ±180° without a long seam."""
    r = REGIONS[region]
    intervals = [(r['west'], r['east'])] if r['west'] < r['east'] else [(r['west'], 180), (-180, r['east'])]
    return [[[w, r['south']], [e, r['south']], [e, r['north']], [w, r['north']], [w, r['south']]] for w, e in intervals]


def region_geojson(date='2026-10-01'):
    """Real regional statistics attached to definition boxes, NOT pixel SST."""
    features = []
    for key, definition in REGIONS.items():
        df = load_pulse(key)
        selected = df.loc[df.date == pd.Timestamp(date)]
        if len(selected) != 1:
            raise ValueError('Requested month is not in every regional snapshot.')
        row = selected.iloc[0]
        rings = region_rings(key)
        geom = dict(type='Polygon', coordinates=[rings[0]]) if len(rings) == 1 else dict(type='MultiPolygon', coordinates=[[ring] for ring in rings])
        properties = dict(region=key, name=definition['name'], date=str(row.date.date()),
                          sst_c=float(row.sst), anomaly_c=float(row[ANOM]), relative_c=float(row[REL]),
                          units='degC', baseline='1991-2020', statistic='ocean-only area-weighted regional mean',
                          support='Definition box; overlapping regions; not a gridded field',
                          source=CREDIT, licence='CC-BY-4.0', doi='10.24381/cds.f17050d7',
                          snapshot='2026-11-20', transformation='CSV row joined to original region geometry')
        features.append(dict(type='Feature', id=key, geometry=geom, properties=properties))
    return dict(type='FeatureCollection', features=features)


def region_map(region='nino34', date='2026-10-01'):
    """2D region footprints; fill is a regional mean, not a spatial interpolation."""
    feature = next(f for f in region_geojson(date)['features'] if f['id'] == region)
    p = feature['properties']
    fig = go.Figure()
    for line in coastlines():
        # Retain source coastline pieces without drawing artificial seam connectors.
        for segment in np.split(line, np.flatnonzero(np.abs(np.diff(line[:, 0])) > 180)+1):
            fig.add_trace(go.Scatter(x=segment[:, 0], y=segment[:, 1], mode='lines', line=dict(color='#687c8e', width=1), hoverinfo='skip', showlegend=False))
    for key in REGIONS:
        for ring in region_rings(key):
            xy = np.array(ring)
            fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode='lines',
                line=dict(color='#b95721' if key == region else '#637b91', width=3 if key == region else 1),
                fill='toself' if key == region else None, fillcolor='rgba(230,159,0,0.28)',
                name=REGIONS[key]['name'], showlegend=False,
                hovertemplate=REGIONS[key]['name']+' definition box<extra></extra>'))
    fig.update_layout(title=f"{p['name']} · {date[:7]} · regional anomaly {p['anomaly_c']:.2f} °C",
        xaxis=dict(title='Longitude (°)', range=[-180,180]), yaxis=dict(title='Latitude (°)', range=[-35,35]),
        annotations=[dict(text='Boxes overlap; fill locates the selected region only · Natural Earth coastlines', x=0, y=-0.22, xref='paper', yref='paper', showarrow=False)])
    return fig


def region_globe(region='nino34', date='2026-10-01'):
    """Unit sphere and one real regional scalar, with local coastlines."""
    p = next(f['properties'] for f in region_geojson(date)['features'] if f['id'] == region)
    lon, lat = np.meshgrid(np.linspace(-180,180,73), np.linspace(-90,90,37))
    def xyz(lo, la, radius=1):
        a,b = np.deg2rad(lo),np.deg2rad(la)
        return radius*np.cos(b)*np.cos(a), radius*np.cos(b)*np.sin(a), radius*np.sin(b)
    x,y,z = xyz(lon,lat)
    fig = go.Figure(go.Surface(x=x,y=y,z=z, surfacecolor=np.zeros_like(z),
        colorscale=[[0,'#e1edf2'],[1,'#e1edf2']],showscale=False,hoverinfo='skip'))
    for ring in region_rings(region):
        w,s = ring[0]; e,n = ring[2]
        lo,la=np.meshgrid(np.linspace(w,e,20),np.linspace(s,n,8)); x,y,z=xyz(lo,la,1.008)
        fig.add_trace(go.Surface(x=x,y=y,z=z,surfacecolor=np.full_like(z,p['anomaly_c']),
            colorscale='RdBu_r', cmin=-4,cmax=4, colorbar=dict(title='Δ °C'),
            showscale=len(fig.data)==1,hovertemplate=f"{p['name']} region mean: {p['anomaly_c']:.4f} °C<extra></extra>"))
    xx,yy,zz=[],[],[]
    for line in coastlines():
        x,y,z=xyz(line[:,0],line[:,1],1.012)
        xx.extend(x.tolist()+[None]); yy.extend(y.tolist()+[None]); zz.extend(z.tolist()+[None])
    fig.add_trace(go.Scatter3d(x=xx,y=yy,z=zz,mode='lines',line=dict(color='#485c70',width=2),hoverinfo='skip',showlegend=False))
    axis=dict(visible=False)
    fig.update_layout(title=f"{p['name']} · {date[:7]} · one regional mean, not pixels",
        scene=dict(xaxis=axis,yaxis=axis,zaxis=axis,aspectmode='data',camera=dict(eye=dict(x=-1.6,y=-1.1,z=.5))))
    return fig
