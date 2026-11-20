# Work with the official Copernicus apps

Use these notebooks alongside [Climate Pulse](https://pulse.climate.copernicus.eu/)
and the [Copernicus Data Stores Applications catalogue](https://apps.climate.copernicus.eu/).
The course now contains **32 Python notebooks**. Chapters 21, 23, 24, and 26 also
include executable links to matching selections in the official Pulse app.

| Workshop | What you will do |
| --- | --- |
| [30: Global Pulse workshop](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/30-global-pulse-workshop.html) | Compare real global air/ocean records, calculate complete annual summaries, and open matching official views. |
| [31: Download and import](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/31-pulse-download-roundtrip.html) | Download a Pulse CSV, upload it to Lab, validate metadata, and separate new months from historical revisions. |
| [32: Copernicus apps workshop](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/32-copernicus-apps-workshop.html) | Explore 11 apps through questions, a catalogue matrix, and a reusable evidence journal. |

[Run Workshop 30](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path=30-global-pulse-workshop.ipynb) ·
[Run Workshop 31](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path=31-pulse-download-roundtrip.ipynb) ·
[Run Workshop 32](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path=32-copernicus-apps-workshop.ipynb)

## A practical route from Pulse to Python

1. Open a notebook's generated official Pulse link. Check region, date, variable,
   time aggregation, quantity, and reference period in the displayed app.
2. In Pulse, select the CSV download for **monthly Niño 3.4 SST**. Retain the entire
   file, including its original header. A share link preserves selections; it does
   not freeze the data version.
3. In JupyterLite, create `uploads/` and upload that file as `pulse_export.csv`.
   In Chapter 31 set `USE_UPLOADED_EXPORT = True`, then rerun the cells.
4. Inspect the header and comparison table. Download your original CSV, edited
   notebook, and `exports/pulse-import-audit.json` together. Record the real download
   time and verify the source before marking the evidence as checked.

The default chapter executes a self-check using the archived official CSV. It says
so prominently and does not claim to have retrieved a new file. The importer is
deliberately scoped to the demonstrated Niño 3.4 monthly schema: wrong region,
units, baseline, dates, or missing columns cause an error. The comparison separates
added dates, removed dates, and revised common dates. Missing values are not zeros.

On **20 November 2026**, the public Pulse CSV server returned no
`Access-Control-Allow-Origin` header for this site's origin. Consequently the
browser exercise uses normal download/upload, not an automatic cross-origin fetch.
No proxy, credentials, or weakened browser settings are part of the workflow.
The new helper's share parameters follow the current published Pulse application;
if the application changes, select the same settings manually and copy its Share URL.
Browser rendering and external app interactions remain unverified in this release.

## Explore the applications through questions

The following list reflects **11 catalogue entries checked on 20 November 2026**.
These questions are original teaching suggestions. They do not imply a shared API,
download format, licence, or comparison method across all apps.

| App | Suggested investigation | Official information |
| --- | --- | --- |
| Climate Pulse | How do absolute temperature and anomalies differ? | [Overview](https://apps.climate.copernicus.eu/overview?app=climate-pulse) |
| Climate Atlas | Which changes are conditional on scenario, region, and period? | [Overview](https://apps.climate.copernicus.eu/overview?app=climate-atlas) |
| ERA Explorer | What seasonal context does a location's reanalysis provide? | [Overview](https://apps.climate.copernicus.eu/overview?app=era-explorer) |
| Weather Replay | How did the weather evolve hour by hour during an event? | [Overview](https://apps.climate.copernicus.eu/overview?app=weather-replay) |
| Thermal Trace | How does a thermal-stress indicator differ from air temperature? | [Overview](https://apps.climate.copernicus.eu/overview?app=thermal-trace) |
| Global temperature trend monitor | How does a long-term indicator differ from one annual anomaly? | [Overview](https://apps.climate.copernicus.eu/overview?app=global-temperature-trend-monitor) |
| European Climate Data Explorer | Are two European indicators using the same definitions? | [Overview](https://apps.climate.copernicus.eu/overview?app=european-climate-data-explorer) |
| NECD Explorer | How do country support, season, and percentile define an unusual year? | [Overview](https://apps.climate.copernicus.eu/overview?app=nec-explorer) |
| Fire Emissions Watch | How do emissions differ from atmospheric concentrations? | [Overview](https://apps.climate.copernicus.eu/overview?app=fire-emissions-watch) |
| Aerosol Alerts | What are the forecast's issue time and valid time? | [Overview](https://apps.climate.copernicus.eu/overview?app=aerosol-alerts) |
| Methane Hotspot Explorer | What evidence supports a plume interpretation and its attribution? | [Overview](https://apps.climate.copernicus.eu/overview?app=methane-explorer) |

Try a heat/weather investigation using Weather Replay, ERA Explorer, and Thermal
Trace; a smoke investigation using Fire Emissions Watch and Aerosol Alerts; or a
regional-climate investigation using Climate Atlas and European Climate Data Explorer.
Chapter 32 writes a journal with empty values, explicitly marked **not yet inspected**.
Fill those fields from actual app use. A catalogue matrix records listed evidence
types, not performance ratings, availability guarantees, or climate measurements.

## Sources, credits, and training

Credit **ECMWF's Copernicus Data Stores Applications team**, the **Copernicus Climate
Change Service (C3S)** and **Atmosphere Monitoring Service (CAMS)**, and the individual
app and dataset authors identified in their About/credits panels. The
[catalogue's scope](https://apps.climate.copernicus.eu/about) also includes the wider
CEMS/Data Stores ecosystem; our observed 11 entries carry C3S or CAMS labels.
The factual index and original exercises are bundled, not external app imagery,
descriptions, code, or data. A catalogue listing does not grant a blanket reuse
licence for every linked product. Follow each source dataset's terms.

The numerical Pulse exercises use the previously archived **CC BY 4.0 ERA5 data**;
credit C3S/ECMWF/European Union, **Hersbach et al. (2020)**
([ERA5 paper](https://doi.org/10.1002/qj.3803)), and the
[monthly dataset](https://doi.org/10.24381/cds.f17050d7).
Derived annual plots day-weight the supplied monthly means and exclude incomplete
years. The source files are unchanged. See the [Pulse provenance guide](pulse-guide.md).

Continue with [Pulse information panels and tutorials](https://pulse.climate.copernicus.eu/faqs),
the [Weather Replay introduction and publisher video](https://climate.copernicus.eu/weather-replay-your-time-machine-revisit-past-weather),
[ERA Explorer's official notebooks](https://apps.copernicus-climate.eu/c3s-apps/era-explorer/notebooks/intro.html),
and [NECD Explorer's method](https://apps.copernicus-climate.eu/nec-explorer/).
These are links to original publishers; media have not been copied.
