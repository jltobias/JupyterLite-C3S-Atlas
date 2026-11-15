"""Build the static landing page, Jupyter Book, galleries, and JupyterLite Lab.

Project: JupyterLite-C3S-Atlas; contributors (AI assisted); 2026-11-15.
Inputs: executed content notebooks, site templates, reference files. Output: _site/.
Runtime: requirements.txt. No deployment or external-state mutation.
"""
from __future__ import annotations
import argparse
import html
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import numpy as np
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))
from atlas_helpers import regular_grid, map_figure, globe_figure, monthly_demo, anomalies


def run(*args):
    """Fail a build on any failed subprocess instead of publishing a partial site."""
    subprocess.run(list(args), cwd=ROOT, check=True)


def cli(name: str) -> str:
    """Select console scripts from this interpreter's environment on each OS."""
    return str(Path(sysconfig.get_path('scripts')) / (name + ('.exe' if sys.platform == 'win32' else '')))


def galleries(out: Path):
    """Build self-contained plot galleries with local JS and numerical alternatives."""
    assets = out/'assets'
    assets.mkdir(exist_ok=True)
    (assets/'plotly.min.js').write_text(get_plotlyjs(), encoding='utf-8')
    lon, lat, field = regular_grid()
    df = monthly_demo()
    df['anomaly'] = anomalies(df, 't', (1961, 1990))
    matrix = df.pivot(index='month', columns='year', values='anomaly')
    scene = go.Figure(go.Surface(x=matrix.columns, y=matrix.index, z=matrix.to_numpy(),
                                colorscale='RdBu_r', cmid=0, colorbar=dict(title='Δ °C')))
    scene.update_layout(scene=dict(xaxis_title='Year', yaxis_title='Month', zaxis_title='Anomaly (°C)'))
    pages = [
        ('maps', 'Interactive 2D maps', map_figure(lon, lat, field, 'Synthetic climate pattern'),
         '15-interactive-2d-maps', 'Pan, zoom, and hover. This plate carrée map uses longitude and latitude in degrees. Polar areas appear stretched. The field is invented; coastlines are public-domain Natural Earth data.'),
        ('globe', 'A rotating climate globe', globe_figure(), '16-globes-and-3d-maps',
         'Drag to rotate; scroll to zoom. The surface is a unit sphere: colour represents a synthetic temperature anomaly, not terrain elevation. Coastlines: Natural Earth. If WebGL is unavailable, use the 2D map and table.'),
        ('scenes', 'Climate in three dimensions', scene, '17-3d-scenes',
         'Explore year, month, and anomaly on three axes. Height is temperature in °C, not metres. This is an invented climate data scene, not a city model. Rotate to expose hidden values; use the table for exact comparisons.'),
    ]
    import pandas as pd
    coarse_table = pd.DataFrame(field[::6, ::12], index=lat[::6], columns=lon[::12]).round(2)
    coarse_table.index.name = 'Latitude / longitude (°)'
    for slug, title, fig, chapter, text in pages:
        directory = out/slug
        directory.mkdir(exist_ok=True)
        fig.update_layout(template='plotly_white', margin=dict(l=60,r=45,t=50,b=60),
                          title=title+' · SYNTHETIC', autosize=True)
        fig.write_html(directory/'plot.html', include_plotlyjs='../assets/plotly.min.js',
                       config={'responsive': True, 'displaylogo': False}, full_html=True)
        table = matrix.iloc[:, -5:].round(2) if slug == 'scenes' else coarse_table
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · C3S Atlas learning</title><link rel="stylesheet" href="../style.css"></head><body>
<a class="skip" href="#main">Skip to content</a><header><nav class="wrap" aria-label="Main"><a class="brand" href="../">JupyterLite / C3S Atlas</a><a href="../book/index.html">Book</a><a href="../lite/lab/index.html">Lab</a><a href="../maps/">2D maps</a><a href="../globe/">3D globe</a><a href="../scenes/">3D scenes</a></nav></header>
<main class="wrap" id="main"><div class="page-title"><span class="tag">SYNTHETIC TEACHING EXAMPLE</span><h1>{title}</h1><p class="lede">{text}</p></div>
<p><a href="../book/{chapter}.html">Read the chapter</a> · <a href="../lite/lab/index.html?path={chapter}.ipynb">Edit the Python notebook</a> · <a href="../maps/">2D alternative</a></p>
<iframe class="plot" src="plot.html" title="{html.escape(title)}: interactive synthetic teaching plot" loading="eager"></iframe>
<section><h2>Read the values</h2><p>Selected values from the same synthetic field (°C). The map table lists latitude rows and longitude columns; the scene table lists months and years. No climate measurements are represented.</p><div class="table-scroll">{table.to_html(border=0)}</div></section></main>
<footer><div class="wrap">Independent educational visualisation. <a href="../book/credits.html">Sources and credits</a>. <a href="https://atlas.climate.copernicus.eu/">Open the official C3S Atlas</a> for authentic climate products.</div></footer></body></html>'''
        (directory/'index.html').write_text(page, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-lite', action='store_true', help='Build documentation/galleries only for a local diagnostic.')
    args = parser.parse_args()
    run(sys.executable, str(ROOT/'scripts/prepare_content.py'))
    # Book uses executed outputs committed/generated separately, so no network data access occurs here.
    run(cli('jupyter-book'), 'build', 'content', '--warningiserror', '--keep-going')
    out = ROOT/'_site'
    out.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'site', out, dirs_exist_ok=True)
    shutil.copytree(ROOT/'assets', out/'assets', dirs_exist_ok=True)
    shutil.copytree(ROOT/'content/_build/html', out/'book', dirs_exist_ok=True)
    # Published URLs in portable source notebooks become relative site links in
    # the built book, so the same artifact also navigates correctly on localhost.
    for page in (out/'book').glob('*.html'):
        page.write_text(page.read_text(encoding='utf-8').replace(
            'https://jltobias.github.io/JupyterLite-C3S-Atlas/', '../'), encoding='utf-8')
    galleries(out)
    if not args.skip_lite:
        # Contents are staged without book build products, avoiding recursive distribution.
        lite_contents = ROOT/'_build/lite-content'
        if lite_contents.exists():
            # This is exclusively this build's generated staging directory.
            if not lite_contents.resolve().is_relative_to((ROOT/'_build').resolve()):
                raise ValueError('Unexpected staging path')
            shutil.rmtree(lite_contents)
        shutil.copytree(ROOT/'content', lite_contents, ignore=shutil.ignore_patterns('_build', '_static', '_config.yml', '_toc.yml', '__pycache__'))
        run(cli('jupyter-lite'), 'build', '--contents', str(lite_contents),
            '--output-dir', str(out/'lite'))
    (out/'.nojekyll').touch()
    print(f'Built site: {out}')


if __name__ == '__main__':
    main()
