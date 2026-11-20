# Validation evidence

Validated locally on **2026-11-20**. These are bounded execution checks, not a
scientific validation of the full C3S archive or the official Atlas algorithms.

| Check | Result | Evidence |
| --- | --- | --- |
| Fresh-kernel native Python execution | All 32 notebooks passed | [execution.json](execution.json): versions, per-notebook source hashes, reference/helper hashes, counts, timings. |
| Exact packaged Pyodide WebAssembly runtime, hosted in Node | All 32 notebooks passed, including actual piplite setup cells | [pyodide.json](pyodide.json): runtime/package versions and limitations. |
| Numerical and import/export tests | Fifteen passed | `tests/`: independent weighting calculation, baseline shift, missing/duplicate dates, real GWL windows, NetCDF export and masked-cell failure; Pulse snapshot hashes, tied ranks, leap/partial months, and antimeridian GeoJSON. |
| Jupyter Book | Built successfully with warnings treated as errors | `python scripts/build_site.py`; 32 executed chapters plus reference pages. |
| JupyterLite | Built successfully | 32 packaged notebooks, shared helpers/data, Pyodide kernel, and Plotly MIME renderer. |
| Local HTML links/assets | All checked links resolve | `python scripts/check_site.py`; includes gallery, chapter, Lab, and asset targets. |
| Figure inspection | Inspected original splash and rendered Matplotlib map panels | [Map figure](figures/15-interactive-2d-maps.png), [ocean/circulation figure](figures/10-ocean-and-circulation.png). |

The WebAssembly check ran Python 3.14 with the Pyodide distribution's packages,
separately from the desktop Python 3.13 environment. See the JSON records for exact
versions. It used a local package cache and exercised the actual notebook code;
it did not replace the lesson calculations with a different implementation.
Validation hashes for UTF-8 helper/manifest text normalize line endings to LF so
Windows and Linux agree. Downloaded CSV checksums in the data manifests always
refer to their original, unmodified bytes. Notebook hashes cover joined cell sources.

## Climate Pulse extension

Nine new notebooks passed native execution and actual Pyodide WebAssembly execution.
Seven real C3S/ECMWF CSVs retain their original headers, CC BY 4.0 statements, and
file hashes. The independent Pulse tests check known values, ranks with ties,
incomplete leap-month rejection, and Ni?o 4 geometry.

The dashboard control/data check exercised **16 region/view combinations** plus
point selection, invalid dates, and share parameters:
[pulse-dashboard.json](pulse-dashboard.json). This uses lightweight DOM/Plotly
adapters in Node; it does **not** establish browser or WebGL rendering correctness.
The baseline panel and calendar heatmap were extracted from executed notebook
outputs and visually inspected: [baseline panel](figures/23-pulse-baselines.png),
[calendar heatmap](figures/29-enso-story-lab.png).

The GeoLibre `data=` URL and RustGIS file import follow their official documentation.
No native GIS package is installed into Pyodide, and no claim is made that the
external application interfaces or notebook widgets were tested in a browser.

## Official-app workshops

Chapters 30?32 and the added Pulse launch cells passed native Python and Pyodide
execution. Five additional tests cover share-link semantics, day-weighted complete
years, importer rejection of changed metadata, revision/addition/removal separation,
and the sourced 11-app catalogue. All 11 official launch URLs returned HTTP 200.
This checks reachability, not the controls or rendering of those applications.

The Pulse CSV host returned no cross-origin permission for this site's origin;
the demonstrated live-data path is browser download followed by explicit Lab upload.
Default execution performs a labelled self-check against the bundled real CSV.
No fresh learner upload or external app UI was exercised. Known fixture changes
exercise the revision audit in tests. Static outputs were visually inspected:
[annual temperature panels](figures/30-global-pulse-workshop.png) and
[catalogue matrix](figures/32-copernicus-apps-workshop.png).

## Remaining verification boundaries

- **Browser UI and WebGL rendering were not tested:** the connected browser host
  was unavailable. Node-hosted WebAssembly verifies Python compatibility, not the
  JupyterLite service worker, browser package requests, persistent storage, rendered
  controls, or accessibility with assistive technology.
- **No authenticated CDS download was performed.** The NetCDF exporter was tested
  with a known synthetic fixture; an authentic gridded file still needs its own
  metadata, calendar, mask, and units checks. Real bundled warming-level data and
  catalogue metadata were loaded and validated by the lessons.
- **Publication is separate from the local build.** Do not infer a successful
  remote deployment from these local results. The Pages workflow runs the native
  checks again before publication.
- Optional build notices about absent `libarchive-c` and translations do not affect
  this English-language build. Local Jupyter kernels emitted a TCP-transport notice;
  notebook execution was on the local machine, not a public notebook server.

## Repeat the primary checks

```shell
python scripts/prepare_content.py
python -m pytest -q
python scripts/execute_notebooks.py
python scripts/build_site.py
python scripts/check_site.py
node scripts/check_pulse_dashboard.mjs
```

Some operations needed execution outside the session's restrictive Windows sandbox
to create temporary files and launch local kernels. A permission-denied test setup
is an environment failure, not a failed scientific assertion; the normal-permission
run passed. The initial UTF-8 source-reading issue was fixed before the successful
full notebook runs.

The optional `scripts/check_pyodide.mjs` expects Node 22 and a local cache of the
Pyodide version declared by `jupyterlite-pyodide-kernel`, including its transitive
NumPy/pandas/Matplotlib/IPython/micropip wheels plus Plotly 6.5.0 and Narwhals wheels.
It also uses the piplite wheel from the built Lab. Run
`node scripts/check_pyodide.mjs PATH_TO_CACHE` after building the site. The large
local test cache is not committed or required to use the published Lab.
