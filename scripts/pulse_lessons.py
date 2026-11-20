"""Original Climate Pulse extension: nine executable Python learning chapters.

Contributors (AI assisted), 2026-11-20. Register with the common notebook authoring
pipeline. All numerical examples here use attributed, bundled ERA5 snapshots.
"""
PULSE = 'https://pulse.climate.copernicus.eu/'
ARTICLE = 'https://climate.copernicus.eu/new-version-climate-pulse-provides-new-monitoring-el-nino-conditions'
METHOD = 'https://www.ecmwf.int/en/about/media-centre/science-blog/2026/measuring-strength-el-nino'
IMPACTS = 'https://confluence.ecmwf.int/spaces/CKB/pages/373753799/ENSO+impacts+based+on+ERA5+reanalysis'
IMPORTS = '''from pulse_helpers import (
    load_pulse, complete_months, rank_same_month, region_rings, region_geojson,
    region_map, region_globe, REGIONS, ANOM, REL, CREDIT, BASE,
)
'''
SOURCES = [('C3S Climate Pulse 2.0 announcement (10 November 2026)', ARTICLE),
           ('Climate Pulse FAQs and methodology', PULSE+'faqs'),
           ('Climate Pulse credits and citations', PULSE+'credits'),
           ('ERA5 monthly data: C3S/ECMWF and ERA5 contributors', 'https://doi.org/10.24381/cds.f17050d7'),
           ('Hersbach et al. (2020): The ERA5 global reanalysis', 'https://doi.org/10.1002/qj.3803')]


def register(lesson):
    def add(slug, title, question, concepts, blocks, exercise, answer, transfer, sources=None):
        blocks[0] = (blocks[0][0], IMPORTS + blocks[0][1])
        lesson(slug, title, question, concepts, blocks, exercise, answer, transfer,
               data='Real C3S/ECMWF ERA5 Climate Pulse CSV snapshots retrieved 2026-11-20; CC BY 4.0',
               sources=SOURCES+(sources or []))

    add('21-climate-pulse-observatory', 'Climate Pulse: a reproducible observatory',
        'What does a near-real-time climate dashboard actually measure?',
        '''A monitoring result needs a timestamp as well as a value. Climate Pulse
        provides a recent view of ERA5 reanalysis; this book preserves a **fixed snapshot**
        so a class can reproduce the same calculation next month. Reanalysis combines
        observations and a model. It is neither a single thermometer nor a forecast.

        Start a monitoring record with quantity, region, time support, baseline, source
        version, and retrieval date. The bundled monthly products end in October 2026;
        the daily Niño 3.4 file extends to 18 November. Check these boundaries in code.
        Some recent values can be revised. Read the `status` field instead of assuming
        the newest sample is final.

        **A metadata reading exercise:** the daily SST header has a generic “daily means”
        description but a specific note stating **12 UTC SST**. Preserve both statements,
        follow the specific note for this exercise, and seek producer clarification before
        treating daily and monthly exports as identical aggregations. This is why provenance
        must include the original header, not just a convenient column name.''',
        [('Audit the evidence', '''import hashlib
manifest = json.loads((DATA / "pulse/manifest.json").read_text(encoding="utf-8"))
records = []
for record in manifest:
    path = DATA / record["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    frame = pd.read_csv(path, comment="#")
    records.append({"file": path.name, "rows": len(frame), "first": frame.date.min(),
                    "last": frame.date.max(), "licence": record["licence"]})
display(pd.DataFrame(records))
'''), ('Locate the newest daily point in its recent context', '''daily = load_pulse(aggregation="daily")
display(daily.tail(4)[["date", "sst", ANOM, REL, "status"]])
recent = daily[daily.date >= "2025-01-01"]
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(recent.date, recent[ANOM], label="Traditional Niño 3.4 anomaly")
ax.axhline(0, color="gray", lw=1)
ax.set(title="ERA5 daily export · 12 UTC SST per source note", ylabel="°C relative to 1991–2020")
ax.legend(); fig.autofmt_xdate(); plt.show()
''')],
        'Read one raw header in data/pulse. Identify a claim the numerical columns alone could not support.',
        'A date/value pair does not reveal spatial averaging, baseline, preliminary status, or the time-of-day convention. Those are part of the evidence.',
        'Open Climate Pulse, note its newest timestamp, and compare it with this archived snapshot. Save the official share link and export metadata; a changing live link is not an immutable data version.')

    add('22-pacific-regions', 'Four windows on the tropical Pacific',
        'Why does Niño 4 need two polygons on a longitude map?',
        '''The Niño regions sample different parts of the equatorial Pacific. They
        overlap, so their statistics are not independent observations or pieces that can
        be summed into a global average. Their definitions are geographic boxes; the
        producer averages **ocean points** inside them.

        Longitude wraps. Niño 4 spans 160°E to 150°W: its width is 50°, not 310°.
        GeoJSON uses longitude then latitude in degrees. Cut the geometry at ±180°
        so a GIS does not shade the long way around the planet. A rectangle's spherical
        area is proportional to longitude width times the difference of sine latitude;
        that geometric area includes any land and is not the exact producer ocean mask.''',
        [('Check geometry independently', '''rows = []
for key, r in REGIONS.items():
    width = (r["east"] - r["west"]) % 360
    area = 6371.0**2 * np.deg2rad(width) * (np.sin(np.deg2rad(r["north"])) - np.sin(np.deg2rad(r["south"])))
    rings = region_rings(key)
    assert all(ring[0] == ring[-1] for ring in rings)
    rows.append({"region": r["name"], "longitude width (degrees)": width,
                 "GeoJSON parts": len(rings), "box area (million km²)": area/1e6})
display(pd.DataFrame(rows))
assert rows[-1]["longitude width (degrees)"] == 50
'''), ('Follow a box across the seam', '''show(region_map("nino4"))
print(json.dumps(region_geojson()["features"][-1]["geometry"], indent=2))
''')],
        'Change the selected region to nino12. Explain why a smaller geographic box can still be scientifically useful.',
        'The boxes sample different ocean regimes. Area alone does not determine relevance, and overlapping boxes cannot be treated as disjoint tiles.',
        'Use the official Pulse region selector to compare all four Niño regions. Note the time support and SST units before comparing their temperatures.',
        [('ECMWF: ENSO region definitions and impacts', IMPACTS), ('IETF: GeoJSON geometry and antimeridian guidance', 'https://www.rfc-editor.org/rfc/rfc7946')])

    add('23-pulse-baselines', 'Warm water, unusual water',
        'Is the hottest month also the most anomalous month?',
        '''Absolute temperature describes the water; anomaly describes its departure
        from a reference climate for the same calendar month. Seasonal structure can
        make the largest absolute temperature occur at a different time from the largest
        anomaly. The source supplies both quantities and its 1991–2020 climatology.

        Verify that subtraction reproduces the published anomaly within rounding.
        Then compare equal calendar months across event years. A different baseline
        changes the zero point; it does not change the underlying absolute SST. Neither
        a regional anomaly nor a single warm month measures a sustained global warming level.''',
        [('Check the arithmetic and seasonal cycle', '''df = load_pulse()
residual = df.sst - df.clim_1991_2020 - df[ANOM]
print("Maximum rounding residual (°C):", abs(residual).max())
recent = df[df.year == 2026]
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
axes[0].plot(recent.month, recent.sst, "o-", label="2026 SST")
axes[0].plot(recent.month, recent.clim_1991_2020, "--", label="1991–2020 monthly climatology")
axes[0].set(ylabel="Absolute SST (°C)", title="ERA5 Niño 3.4: absolute temperature and departure")
axes[0].legend()
axes[1].bar(recent.month, recent[ANOM], color="#b95721")
axes[1].set(xlabel="Calendar month", ylabel="Anomaly (°C)", xticks=range(1,13))
plt.tight_layout(); plt.show()
'''), ('Compare matching months, with no invented future values', '''years = [1982, 1997, 2015, 2023, 2026]
fig = go.Figure()
for year in years:
    part = df[df.year == year]
    fig.add_trace(go.Scatter(x=part.month, y=part[ANOM], mode="lines+markers", name=str(year)))
fig.update_layout(title="ERA5 Niño 3.4 · published monthly anomalies", xaxis=dict(title="Month", dtick=1, range=[1,12]), yaxis_title="°C relative to 1991–2020")
show(fig)
display(df.loc[df.groupby("year")[ANOM].idxmax(), ["year", "month", ANOM]].tail())
''')],
        'Try a different set of comparison years. Which months exist for every selected year? Restrict a comparison to that common window.',
        'A truncated current year is not a full annual cycle. Missing November and December values must remain absent, not be set to zero or extrapolated.',
        'Recreate the Niño 3.4 comparison in Pulse using monthly anomalies. Compare the legend, reference period, and selected years with this notebook.')

    add('24-relative-enso', 'ENSO against a warming ocean',
        'What changes when the tropical background is removed?',
        '''The relative Niño index compares a Niño-region anomaly with a tropical-ocean
        anomaly and applies a region- and month-dependent scaling factor. Removing
        the tropical background changes what the index measures. Scaling preserves a
        useful amplitude range; simply subtracting two anomalies is not the full method.

        This lesson uses **the producer's published relative column**. It does not estimate
        missing tropical means or substitute global SST (whose domain is different).
        Use the linked ECMWF methodology for the equation, scaling conventions, and
        interpretation. A single daily or monthly index value is not, by itself, an operational
        ENSO declaration; consult the responsible monitoring agency and its full criteria.''',
        [('Compare two explicitly different quantities', '''df = load_pulse()
part = df[df.year >= 1979]
fig = go.Figure()
for col, label in [(ANOM, "Traditional anomaly"), (REL, "Published relative index")]:
    fig.add_trace(go.Scatter(x=part.date, y=part[col], name=label, mode="lines"))
fig.update_layout(title="ERA5 Niño 3.4 · traditional and relative monthly indices", yaxis_title="°C; 1991–2020 reference", xaxis_title="Month")
show(fig)
'''), ('Inspect the change of viewpoint', '''df["difference"] = df[ANOM] - df[REL]
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].scatter(df[ANOM], df[REL], c=df.year, cmap="viridis", s=9)
axes[0].plot([-3,4], [-3,4], color="gray", lw=1)
axes[0].set(xlabel="Traditional (°C)", ylabel="Relative (°C)", title="Equality line is a reference, not a fit")
axes[1].plot(df.date, df.difference, color="#7b456a")
axes[1].set(ylabel="Traditional minus relative (°C)", title="Difference includes the scaling convention")
plt.tight_layout(); plt.show()
display(df.loc[df.date.isin(pd.to_datetime(["1997-12-01", "2023-12-01", "2026-10-01"])), ["date", ANOM, REL, "difference"]])
''')],
        'Repeat with nino4. Explain why traditional minus relative is not a direct estimate of tropical-mean warming.',
        'The relative column includes scaling. A difference between scaled and unscaled indices cannot be interpreted as the removed background alone.',
        'In Pulse select anomalies and enable relative. Keep the region and time aggregation fixed, then compare the official methodology before using thresholds.',
        [('Tim Stockdale (2026): relative Niño indices and scaling', METHOD), ('Method DOI', 'https://doi.org/10.21957/d05ccfe150')])

    add('25-time-ranks-and-records', 'Days, seasons, and record claims',
        'When is a record comparison fair?',
        '''A rank depends on the comparison set. Compare October with other Octobers,
        keep the variable and region fixed, name the archive period, and state how ties
        are handled. A rank is descriptive, not a return period or a probability estimate.

        Three-month means suppress short fluctuations but adjacent windows share two
        months; they are not independent samples. A centred mean has no value at either
        end without a complete window. A recent daily export also contains a partial month:
        averaging that fragment and labelling it a full November mean would be misleading.
        Here we aggregate daily **12 UTC SST** values and keep that statistic distinct
        from the source's monthly product.''',
        [('Require a complete month', '''daily = load_pulse(aggregation="daily")
monthly_from_daily = complete_months(daily)
official = load_pulse()
audit = monthly_from_daily.merge(official[["date", ANOM]], on="date", how="inner")
audit["difference"] = audit["mean"] - audit[ANOM]
display(audit.tail(5))
print("Daily file ends:", daily.date.max().date())
print("Last complete derived month:", monthly_from_daily.date.max().date())
print("These products have different stated time support; agreement is not assumed.")
'''), ('A rank with its denominator and a rolling window', '''df = load_pulse()
date = df.date.max()
display(pd.Series(rank_same_month(df, date)).to_frame(f"{date:%Y-%m} · traditional Niño 3.4"))
df["centred_three_month"] = df[ANOM].rolling(3, center=True, min_periods=3).mean()
part = df[df.year >= 2022]
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(part.date, part[ANOM], label="Published monthly anomaly", alpha=.6)
ax.plot(part.date, part.centred_three_month, lw=2.5, label="Centred 3-month arithmetic mean")
ax.set(ylabel="°C relative to 1991–2020", title="ERA5 Niño 3.4 · endpoints are not extrapolated")
ax.legend(); fig.autofmt_xdate(); plt.show()
''')],
        'Rank another month. Replace the centred mean with a trailing mean and explain the changed date label.',
        'For a centred January value the window is December–February. A trailing January value uses November–January. Neither is automatically an agency-specific ONI or RONI product.',
        'Select monthly and annual views in Pulse. Inspect the information panel for each aggregation and compare its record definition with the denominator used here.',
        [('ERA5 hourly data underpinning daily exports', 'https://doi.org/10.24381/cds.adbb2d47')])

    add('26-pulse-maps-and-globes', 'One statistic, two geographic views',
        'What does a coloured region reveal—and what does it conceal?',
        '''A regional average has spatial support: the set of ocean points that
        contributed to it. This lesson locates that support using a geographic box.
        A constant-colour patch on the globe represents **one regional scalar**; it says
        nothing about within-region gradients, coastal extremes, or individual pixels.

        Select one region at a time because Niño boxes overlap. The globe is a unit
        sphere, and patch height is a tiny display offset to avoid flicker, not an elevation
        or temperature dimension. The fixed −4 to +4 °C scale allows comparisons; values
        outside it saturate, so always inspect the exact number. Use the table and 2D view
        when rotation hides a location or your device cannot render WebGL.''',
        [('Map the statistic and its support', '''region, date = "nino34", "2026-10-01"
features = region_geojson(date)["features"]
display(pd.DataFrame([f["properties"] for f in features])[["name", "date", "sst_c", "anomaly_c", "relative_c"]])
show(region_map(region, date))
'''), ('Rotate the same evidence', '''show(region_globe(region, date))
print("Colour: traditional SST anomaly; reference 1991–2020; unit °C.")
print("Source:", CREDIT, "· CC BY 4.0 · retrieval 2026-11-20")
''')],
        'Change the region to nino4 and the date to 1997-12-01. Inspect both sides of the antimeridian in the 2D view.',
        'The two pieces encode one connected geographic region and one shared value. Do not treat them as two measurements or sum overlapping Niño regions.',
        'Use Pulse’s map probe to inspect actual SST spatial variability within a Niño region. Explain why the regional-mean patch cannot reproduce those pixel values.')

    add('27-enso-and-global-context', 'Association is a question, not a mechanism',
        'How does a shared trend change an apparent ENSO relationship?',
        '''Join series by date before comparing them. Global air temperature and a
        Pacific SST index have different spatial and physical meanings. They can co-vary
        because of ENSO, background warming, other processes, and sampling choices.
        A scatterplot alone cannot isolate a cause or forecast an individual place.

        Compare a raw association with a simple linear-detrended sensitivity check over
        a fixed window. Detrending is an assumption, not a causal adjustment. A lag scan
        creates many opportunities to find a peak, and serial dependence makes nominal
        independent-sample significance misleading. Here we report descriptive correlations
        only. The official teleconnection resources show why regional and seasonal outcomes
        must be examined separately.''',
        [('Align quantities with different spatial support', '''nino = load_pulse()[["date", REL]].rename(columns={REL: "relative_nino34"})
air = load_pulse("global", variable="t2m")[["date", ANOM]].rename(columns={ANOM: "global_air"})
paired = nino.merge(air, on="date", validate="one_to_one")
paired = paired[(paired.date >= "1979-01-01") & (paired.date <= "2025-12-01")].copy()
assert len(paired) == 47*12
t = np.arange(len(paired))
for col in ["relative_nino34", "global_air"]:
    paired[col+"_detrended"] = paired[col] - np.polyval(np.polyfit(t, paired[col], 1), t)
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, suffix, title in zip(axes, ["", "_detrended"], ["Raw association", "After separate linear detrending"]):
    x, y = paired["relative_nino34"+suffix], paired["global_air"+suffix]
    ax.scatter(x, y, s=10, alpha=.5)
    ax.set(title=f"{title}; r={x.corr(y):.2f}", xlabel="Niño 3.4 relative (°C)", ylabel="Global air anomaly (°C)")
plt.tight_layout(); plt.show()
'''), ('Inspect lag sensitivity without selecting a forecast', '''rows = []
for lag in range(-12, 13):
    # Positive lag pairs earlier Niño values with later global-air values.
    x = paired.relative_nino34_detrended.shift(lag)
    valid = x.notna() & paired.global_air_detrended.notna()
    rows.append({"lag_months": lag, "r": x[valid].corr(paired.global_air_detrended[valid]), "pairs": int(valid.sum())})
lags = pd.DataFrame(rows)
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(lags.lag_months, lags.r, "o-"); ax.axhline(0, color="gray", lw=1)
ax.set(xlabel="Lag (months); positive = Niño leads air", ylabel="Descriptive Pearson r", title="1979–2025 · sensitivity scan, not a prediction model")
plt.show(); display(lags.iloc[::4])
''')],
        'Change the analysis window to 1991–2020. Record how the association changes before examining the official regional composites.',
        'A correlation depends on the sample, transformation, and lag. It does not identify the portion of a regional hazard caused by ENSO.',
        'Explore the official ENSO impacts page: compare early- and late-winter composites and individual years. Connect a composite to an Atlas variable without treating it as a local forecast.',
        [('ECMWF ENSO impacts and diversity of regional outcomes', IMPACTS)])

    add('28-rustgis-geolibre', 'From Python to RustGIS and GeoLibre',
        'Can another GIS preserve your numbers and their meaning?',
        '''GeoJSON is the bridge: small, readable geometries plus explicit properties.
        Export a dated feature collection, keep the numerical precision, and preserve
        units, baseline, source, licence, and transformation. Niño 4 uses a MultiPolygon
        split at the antimeridian. These boxes overlap and are not climate raster cells.

        **Browser workflow:** run this notebook, download `exports/enso-regions.geojson`
        from the Lab file browser, then add the file in RustGIS Web or GeoLibre Web.
        Style `anomaly_c` with a fixed diverging scale and inspect `relative_c` separately.
        Select one region before comparing views; save your local GIS project.

        RustGIS's Python engine uses native wheels; it is not installed in this Pyodide
        kernel. GeoLibre has Python notebook support, but this portable lesson uses its
        documented public `data=` URL and file import, avoiding unverified widget support.
        The launch links below are optional external apps. Browser restrictions and
        cross-origin requests may affect loading; the downloaded GeoJSON remains usable.
        No account, API token, remote project upload, or AI provider is required.''',
        [('Export and verify a portable dataset', '''collection = region_geojson("2026-10-01")
out = Path("exports"); out.mkdir(exist_ok=True)
path = out / "enso-regions.geojson"
path.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
roundtrip = json.loads(path.read_text(encoding="utf-8"))
assert roundtrip == collection
assert roundtrip["features"][-1]["geometry"]["type"] == "MultiPolygon"
display(pd.DataFrame([f["properties"] for f in roundtrip["features"]]))
print("Created", path, "— download from the JupyterLite file browser.")
'''), ('Launch the GIS comparison', '''from urllib.parse import urlencode
from IPython.display import Markdown
data_url = BASE + "pulse/data/enso-regions.geojson"
geo_url = "https://web.geolibre.app/?" + urlencode({"data": data_url})
rust_url = "https://web.rustgis.app/?blank&projection=globe"
display(Markdown(f"[Open shipped October 2026 dataset in GeoLibre]({geo_url}) · [Open RustGIS, then add the downloaded file]({rust_url})"))
show(region_map("nino4"))
print("Audit in each GIS: 4 features; Niño 4 has 2 polygon parts; longitude is first; property values match the table.")
''')],
        'In GeoLibre switch between the 2D view and globe, then save a project. In RustGIS inspect the same properties and save an .rgis project. Record app versions and any difference in rendering.',
        'Successful interoperability preserves coordinates, feature identity, numerical values, and provenance. Similar-looking maps alone do not establish a correct transfer.',
        'Return to the official Pulse map and distinguish its gridded SST display from the regional statistics exported here. Use CDS for an actual licensed gridded subset.',
        [('RustGIS installation and web limitations', 'https://rustgis.app/installation/'),
         ('RustGIS Python API and native runtime', 'https://rustgis.app/python/'),
         ('RustGIS authors and citation', 'https://rustgis.app/citation/'),
         ('GeoLibre embedding and documented data URL', 'https://geolibre.app/user-guide/embedding/'),
         ('GeoLibre Python integration', 'https://geolibre.app/python/'),
         ('GeoLibre authors and citation', 'https://doi.org/10.5281/zenodo.20785400')])

    add('29-enso-story-lab', 'A Pacific story in five evidence panels',
        'Can you tell a compelling story without outrunning the evidence?',
        '''Build the narrative in five steps: **locate → compare → contextualise →
        inspect time → state limits**. Each panel should answer one question and show
        the evidence needed to assess its claim. A globe supplies geographic context;
        a line chart is better for small temporal differences. A year–month heatmap
        keeps every complete month visible without occlusion.

        The companion storymap uses the same snapshots and downloadable GeoJSON.
        In the 3D scene below, x is year, y is calendar month, and z is an anomaly in °C.
        It is a data surface, not ocean topography. The partial 2026 row is omitted from
        the scene so interpolation never implies unpublished months. The dashboard retains
        available 2026 months individually. Read every conclusion with its as-of date.''',
        [('Make a scene and its flat alternative', '''df = load_pulse()
complete = df[df.year <= 2025]
matrix = complete.pivot(index="month", columns="year", values=ANOM)
assert matrix.notna().all().all()
fig = go.Figure(go.Surface(x=matrix.columns, y=matrix.index, z=matrix.to_numpy(),
    colorscale="RdBu_r", cmin=-4, cmax=4, colorbar=dict(title="Δ °C")))
fig.update_layout(title="ERA5 Niño 3.4 · 1979–2025 monthly anomaly surface", scene=dict(xaxis_title="Year", yaxis_title="Month", zaxis_title="Anomaly (°C)"))
show(fig)
fig, ax = plt.subplots(figsize=(12, 3.8))
image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="RdBu_r", vmin=-4, vmax=4,
                  extent=[1978.5,2025.5,.5,12.5])
ax.set(xlabel="Year", ylabel="Calendar month", title="The same evidence without 3D occlusion")
fig.colorbar(image, ax=ax, label="°C relative to 1991–2020"); plt.show()
'''), ('Write an evidence card that can travel with the story', '''latest = df.iloc[-1]
rank = rank_same_month(df, latest.date)
card = {
    "question": "How unusual is the latest archived October Niño 3.4 SST?",
    "as_of": "2026-11-20", "month": str(latest.date.date()),
    "finding": f"Traditional anomaly {latest[ANOM]:.4f} °C; rank {rank['rank']} of {rank['n']} matching calendar months.",
    "relative_index_c": float(latest[REL]),
    "method": "Published regional monthly values; 1991–2020 reference; competition rank.",
    "source": CREDIT, "doi": "10.24381/cds.f17050d7", "licence": "CC-BY-4.0",
    "transformation": "Original charts and region geometry; no reconstruction of SST pixels.",
    "limitation": "Snapshot, not live; regional mean, not local hazard; rank is not a return period.",
}
display(pd.Series(card).to_frame("Evidence card"))
out = Path("exports"); out.mkdir(exist_ok=True)
(out/"enso-story-card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
from IPython.display import Markdown
display(Markdown(f"[Explore the interactive Pulse lab]({BASE}pulse/) · [Read the five-panel storymap]({BASE}stories/enso/)"))
''')],
        'Write a second story about another region or archived month. Change the question and comparison set together, and include a counterexample or limitation.',
        'A defensible story preserves its source, date, spatial support, baseline, transformations, and denominator. Visual drama cannot supply missing evidence.',
        'Use the official Pulse share/export controls to save a complementary view, then compare it with your own card. Link official tutorial videos at their source instead of copying publisher media.',
        [('GeoLibre projects and story-map authoring', 'https://geolibre.app/user-guide/projects/')])
