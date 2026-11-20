"""Build the dated Pulse dashboard and story from attributed CSV snapshots.

Original project code (AI assisted), 2026-11-20; no network access at build time.
"""
from pathlib import Path
import html
import json
import shutil
import sys
from urllib.parse import urlencode
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))
from pulse_helpers import load_pulse, region_geojson, region_rings, region_map, region_globe, REGIONS, ANOM, REL, BASE
from atlas_helpers import coastlines


def build(out):
    directory = out/'pulse'
    data = directory/'data'
    data.mkdir(parents=True, exist_ok=True)
    collection = region_geojson()
    (data/'enso-regions.geojson').write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copytree(ROOT/'content/data/pulse', data/'source', dirs_exist_ok=True)
    payload = dict(snapshot='2026-11-20', regions={}, coastlines=[line.tolist() for line in coastlines()])
    for key, info in REGIONS.items():
        df = load_pulse(key)
        payload['regions'][key] = dict(**info, rings=region_rings(key),
            rows=[[str(r.date.date()), r.sst, r[ANOM], r[REL]] for _,r in df.iterrows()])
    (data/'monthly.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    globe = region_globe()
    base = go.Figure(data=[globe.data[0],globe.data[-1]], layout=globe.layout)
    (data/'globe-base.json').write_text(base.to_json(), encoding='utf-8')
    table = pd.DataFrame([f['properties'] for f in collection['features']])[
        ['name','date','sst_c','anomaly_c','relative_c']].to_html(index=False, border=0)
    template = (ROOT/'site/pulse/index.html').read_text(encoding='utf-8')
    geo_url = 'https://web.geolibre.app/?'+urlencode({'data':BASE+'pulse/data/enso-regions.geojson'})
    template = template.replace('<!-- SNAPSHOT_TABLE -->', table).replace('{{GEOLIBRE_URL}}', html.escape(geo_url))
    (directory/'index.html').write_text(template, encoding='utf-8')
    story = out/'stories/enso'
    story.mkdir(parents=True, exist_ok=True)
    df=load_pulse()
    event = go.Figure()
    for year in [1982,1997,2015,2023,2026]:
        part=df[df.year==year]
        event.add_trace(go.Scatter(x=part.month,y=part[ANOM],mode='lines+markers',name=str(year)))
    event.update_layout(title='Matching months · ERA5 Niño 3.4', xaxis=dict(title='Month',dtick=1,range=[1,12]), yaxis_title='Anomaly (°C; 1991–2020)')
    relative=go.Figure()
    part=df[df.year>=2022]
    for col,name in [(ANOM,'Traditional anomaly'),(REL,'Relative index')]:
        relative.add_trace(go.Scatter(x=part.date,y=part[col],mode='lines',name=name))
    relative.update_layout(title='Two lenses on the same region',yaxis_title='°C; 1991–2020 reference',xaxis_title='Month')
    matrix=df[df.year<=2025].pivot(index='month',columns='year',values=ANOM)
    heat=go.Figure(go.Heatmap(x=matrix.columns,y=matrix.index,z=matrix.to_numpy(),colorscale='RdBu_r',zmin=-4,zmax=4,colorbar=dict(title='Δ °C')))
    heat.update_layout(title='Every complete year · ERA5 Niño 3.4',xaxis_title='Year',yaxis_title='Month')
    for filename, fig in [('locate',region_map()),('compare',event),('relative',relative),('calendar',heat)]:
        fig.update_layout(template='plotly_white',margin=dict(l=60,r=35,t=65,b=85),autosize=True)
        fig.write_html(story/f'{filename}.html',include_plotlyjs='../../assets/plotly.min.js',config={'responsive':True,'displaylogo':False})
    template=(ROOT/'site/stories/enso/index.html').read_text(encoding='utf-8')
    (story/'index.html').write_text(template.replace('<!-- SNAPSHOT_TABLE -->',table),encoding='utf-8')
    print('Built Pulse dashboard, GeoJSON handoffs, and five-panel ENSO story.')
