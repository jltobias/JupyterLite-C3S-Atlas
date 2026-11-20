# Climate Pulse, ENSO, and open GIS

**Nine additional Python chapters (21–29), an interactive dashboard, and an ENSO
storymap use authentic ERA5 regional time series.** The original 20-chapter Atlas
course remains available. This extension follows the
[C3S Climate Pulse 2.0 announcement, 10 November 2026](https://climate.copernicus.eu/new-version-climate-pulse-provides-new-monitoring-el-nino-conditions).
It is an independent educational project.

[Interactive Pulse lab](https://jltobias.github.io/JupyterLite-C3S-Atlas/pulse/) ·
[ENSO storymap](https://jltobias.github.io/JupyterLite-C3S-Atlas/stories/enso/) ·
[Start Chapter 21](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/21-climate-pulse-observatory.html) ·
[Run Python](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path=21-climate-pulse-observatory.ipynb)

## Follow the new learning route

| Chapter | Question and output |
| --- | --- |
| [21: Observatory](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/21-climate-pulse-observatory.html) | Audit source hashes, temporal coverage, and daily status. |
| [22: Pacific regions](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/22-pacific-regions.html) | Draw four Niño boxes; split Niño 4 correctly at the antimeridian. |
| [23: Baselines](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/23-pulse-baselines.html) | Compare absolute SST, anomalies, and corresponding months. |
| [24: Relative ENSO](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/24-relative-enso.html) | Compare the producer's traditional and relative index columns. |
| [25: Time and ranks](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/25-time-ranks-and-records.html) | Reject incomplete months; calculate transparent ranks and rolling means. |
| [26: Maps and globes](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/26-pulse-maps-and-globes.html) | Locate a regional average in 2D and on a rotating globe. |
| [27: Global context](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/27-enso-and-global-context.html) | Explore detrending and lag sensitivity without causal or forecast claims. |
| [28: Open GIS](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/28-rustgis-geolibre.html) | Export GeoJSON; compare RustGIS and GeoLibre file/URL handoffs. |
| [29: Story lab](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/29-enso-story-lab.html) | Build a heatmap, 3D calendar surface, and cited evidence card. |

Allow 20–35 minutes per notebook. For a 90-minute workshop, use Chapters 21, 24,
and 28, then discuss the five-panel story. The first cell of every chapter includes
the project's original splash illustration. All numerical lessons use small local
files after the Python packages load. No CDS credentials are needed.

## What the snapshot contains

The [Pulse manifest](https://jltobias.github.io/JupyterLite-C3S-Atlas/pulse/data/source/manifest.json) lists seven original CSVs, retrieved
**20 November 2026**: monthly SST for Niño 1+2, 3, 3.4, 4 and the 60°S–60°N ocean,
monthly global 2 m air temperature, and daily Niño 3.4 SST. All headers, source DOIs,
licence statements, dates, status flags, and bytes are retained. Monthly SST spans
January 1979–October 2026; global monthly air temperature begins in January 1940;
daily Niño 3.4 ends on 18 November 2026. These are snapshots of mutable public
exports, not a live feed or immutable upstream release.

Each CSV explicitly states **CC BY 4.0**. The archive records the original public
URL, SHA-256, byte count, retrieval timestamp, and unchanged-data transformation.
Derived charts select columns, join dates, or calculate explicitly named statistics.
Original GeoJSON geometry encodes published region definitions and joins one monthly
row per region; it does **not** reconstruct SST pixels. The boxes overlap. The
archive contains no gridded temperature fields, screenshots, or copied publisher videos.

**Daily metadata caveat:** the generic SST description says daily means, but its
specific Notes section says values are SST at 12 UTC. Our daily aggregation exercise
follows that specific note and does not claim equivalence to the producer's monthly
product. The unchanged header makes the conflict inspectable. Consult the producer
before a scientific analysis requiring an exact hourly sampling convention.

The relative index is read directly from `rnino_anom_1991_2020`. We do not invent
tropical means or scaling factors. It differs from both an unscaled subtraction
and NOAA's separately defined operational products. A monthly value alone is not
an ENSO declaration. Ranks use matching calendar months and competition ranking
(1 + number strictly warmer); no return periods or event probabilities are inferred.

## Reproduce and refresh deliberately

The standard site build uses archived bytes and makes no Pulse requests. To refresh,
run `python scripts/fetch_pulse_data.py` explicitly. This contacts the seven public
export URLs and replaces the local snapshot and manifest. Then review source headers,
coverage, licence, and changed hashes; update the dated teaching narrative, default
map month, UI date bounds, and expected snapshot tests before rebuilding. The current
dashboard/story intentionally target the November 2026 snapshot; refresh is not an
unattended live-data pipeline.

Run `python scripts/generate_notebooks.py`, `python scripts/prepare_content.py`,
`python -m pytest -q`, `python scripts/execute_notebooks.py`,
`python scripts/build_site.py`, and `python scripts/check_site.py`.
Source lesson definitions live in `scripts/pulse_lessons.py`; generated notebooks
must be re-executed after regeneration. Download edits and `exports/` results from
the Lab file browser. Lab saves do not change GitHub.

## RustGIS and GeoLibre: the supported handoff

1. Run Chapter 28, then download `exports/enso-regions.geojson` from Lab.
2. In [RustGIS Web](https://web.rustgis.app/?blank&projection=globe), add the file.
   Inspect four features and the two parts of Niño 4. Filter to one region, style
   `anomaly_c`, try the globe, and save an `.rgis` project locally.
3. In [GeoLibre Web](https://web.geolibre.app/), add the same file. Alternatively,
   use the dashboard's documented `data=` launch link for the shipped October 2026
   file. Compare 2D and globe views, save a local project, and explore the story-map
   tools linked in the [project guide](https://geolibre.app/user-guide/projects/).
4. Check values, units, baseline, dates, and geometry against the notebook table.
   Record the app version and renderer with your exported figure.

RustGIS's Python engine requires native wheels ([Python documentation](https://rustgis.app/python/));
it is not a dependency of this Pyodide course. GeoLibre has its own
[Python integration](https://geolibre.app/python/), but no claim is made that its
widget runs in this Lab. Our integration is standard GeoJSON plus a documented
[browser URL handoff](https://geolibre.app/user-guide/embedding/). Public Pages data
must permit cross-origin reads; downloading and adding the file is the fallback.
Neither external application UI nor WebGL has been tested through an available
browser host for this release. No remote project upload or external AI service is
part of the exercise. Basemap providers have their own terms if you enable them.

## Authors, citations, and media

- **Copernicus Climate Change Service (C3S), implemented by ECMWF on behalf of the
  European Union**, and the ERA5 production teams: source regional data. Credit the
  data even when you redraw a chart. Use “Contains modified Copernicus Climate
  Change Service information (2026)” for the derived educational views and describe
  the transformations. This project has no official endorsement.
- **Hersbach, H., et al. (2020)**. *The ERA5 global reanalysis*. QJRMS 146,
  1999–2049. [doi:10.1002/qj.3803](https://doi.org/10.1002/qj.3803).
- **ERA5 monthly dataset**, [doi:10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7),
  and **ERA5 hourly dataset** underlying the daily export,
  [doi:10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47).
  The global-air header also identifies the climatology at
  [doi:10.24381/7470b643](https://doi.org/10.24381/7470b643). Data licence:
  [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Tim Stockdale (2026)**. *Measuring the strength of El Niño – introducing
  Relative Niño indices*, ECMWF, 10 June.
  [doi:10.21957/d05ccfe150](https://doi.org/10.21957/d05ccfe150).
- **Christopher Goddard; updated by Michela Giusti**, ECMWF Knowledge Base:
  [ENSO impacts based on ERA5](https://confluence.ecmwf.int/spaces/CKB/pages/373753799/ENSO+impacts+based+on+ERA5+reanalysis).
  Linked for methodology, geographic definitions, and interpretation, not copied media.
- **RustGIS**: Qiusheng Wu, José Gregorio Rincón Albarracín, Elpidio Filho, Daniel
  Hofbauer, Mavrick Fitzgerald, Dominik Strebel, and contributors (2026),
  [doi:10.5281/zenodo.23633281](https://doi.org/10.5281/zenodo.23633281);
  [Apache-2.0 repository licence](https://github.com/opengeos/RustGIS/blob/main/LICENSE).
- **GeoLibre**: Qiusheng Wu, Daniel Hofbauer, and contributors (2026),
  [doi:10.5281/zenodo.20785400](https://doi.org/10.5281/zenodo.20785400);
  [MIT repository licence](https://github.com/opengeos/GeoLibre/blob/main/LICENSE).
  These external apps are linked, not redistributed. Their dependencies retain
  their respective terms.
- **Natural Earth**, Nathaniel Vaughn Kelso, Tom Patterson, and contributors:
  coastlines, public domain. **Made with Natural Earth.**

Use the [official Pulse](https://pulse.climate.copernicus.eu/) information panels
for its short video tutorials and the [RustGIS guide](https://rustgis.app/) and
[GeoLibre guide](https://geolibre.app/) for current training. Links retain publisher
authorship and usage context; no screenshots, logos, video files, or article text
are republished. Original explanations, teaching code, and project artwork remain
under the repository's licence; third-party data are not relicensed.
