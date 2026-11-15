"""Author the portable teaching notebooks from reviewed lesson definitions.

Project: JupyterLite-C3S-Atlas. Author: project contributors (AI assisted).
Created/updated: 2026-11-15. Inputs: definitions below; outputs: content/*.ipynb.
Dependencies: nbformat. Change log: initial 20-chapter course.
The notebooks contain original explanations, executable examples, and linked sources.
"""
from pathlib import Path
import json
import shutil
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'
ATLAS = 'https://atlas.climate.copernicus.eu/'
GUIDE = 'https://confluence.ecmwf.int/spaces/CKB/pages/394237545/Copernicus+Interactive+Climate+Atlas+User+Guide'
DATASET = 'https://doi.org/10.24381/cds.h35hb680'
UPSTREAM = 'https://ecmwf-projects.github.io/c3s-atlas/'

BOOTSTRAP = '''# Install only in the browser kernel; desktop dependencies come from requirements.txt.
import sys
if sys.platform == "emscripten":
    import piplite
    await piplite.install(["numpy", "pandas", "matplotlib", "plotly==6.5.0"])

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from IPython.display import display
from atlas_helpers import (
    DATA, SYNTHETIC, COLORS, show, monthly_demo, anomalies, regular_grid,
    area_mean, coastlines, map_figure, globe_figure, warming_levels, load_monthly_csv,
)
print("Ready. Browser edits live in this browser; download work you want to keep.")
'''

LESSONS = []


def lesson(slug, title, question, concepts, blocks, exercise, answer, atlas_task, data='Synthetic teaching examples', sources=None):
    """Register one self-contained chapter with its evidence and learning checks."""
    LESSONS.append(dict(slug=slug, title=title, question=question, concepts=concepts,
                        blocks=blocks, exercise=exercise, answer=answer,
                        atlas_task=atlas_task, data=data, sources=sources or []))


lesson('01-atlas-orientation', 'A question-led tour of the Atlas',
       'What must you know before interpreting a climate map?',
       '''A climate result has an identity: **variable + dataset + place + period + statistic**.
       An observation estimates a measured quantity; a reanalysis blends observations with a
       physical model; a projection explores a conditional future. These are complementary
       forms of evidence, not interchangeable versions of the same experiment.

       The bundled catalogue snapshot is authentic metadata. Its spatial/temporal envelope
       is not a guarantee that every variable covers every point or year. The current CDS
       catalogue describes 35 indices; the application guide describes a larger selector.
       Treat availability as versioned metadata, not a permanent count.''',
       [('Read the actual catalogue', '''catalogue = json.loads((DATA / "reference/atlas-catalogue.json").read_text(encoding='utf-8'))
display(pd.DataFrame([
    ("Title", catalogue["title"]),
    ("DOI", catalogue["sci:doi"]),
    ("Licence", catalogue["license"]),
    ("Published", catalogue["published"]),
    ("Updated", catalogue["updated"]),
], columns=["Field", "Value"]))
assert catalogue["sci:doi"] == "10.24381/cds.h35hb680"
'''),
        ('Build a question card', '''question_card = {
    "question": "How does summer mean temperature change in a selected region?",
    "variable": "t (near-surface temperature)",
    "dataset": "choose ERA5 for a past-climate comparison",
    "region": "record the exact selected region or polygon",
    "reference": "1991–2020", "baseline": "1961–1990",
    "season": "JJA", "statistic": "mean, then reference minus baseline",
}
display(pd.Series(question_card, name="Analysis specification").to_frame())
''')],
       'Rewrite the card for rainfall extremes. Which field must change besides the variable?',
       'Change the statistic and units as well: a seasonal maximum, count, or total answers a different question from a mean daily amount. Verify availability for the chosen dataset.',
       'Open the official Atlas, select one variable, and record the complete information-panel description before changing a selector.',
       data='Authentic CDS catalogue metadata; original question-card example')

lesson('02-data-and-provenance', 'Data families and a reproducible record',
       'Can another reader identify exactly which evidence your figure used?',
       '''Provenance travels with data. A filename alone seldom records the processing,
       calendar, units, model member, or reference period. A checksum identifies exact bytes;
       it does not prove scientific quality. A DOI identifies a published resource; version
       and access date identify the particular release you used.

       Keep source data separate from prepared subsets and teaching examples. ERA5 and
       ERA5-Land have different domains and processing conventions; neither is a station
       observation. CORDEX provides regional simulations, and CMIP ensembles contain
       related models rather than independent random draws from all possible futures.''',
       [('Audit bundled files', '''import hashlib
manifest = json.loads((DATA / "manifest.json").read_text(encoding='utf-8'))
audit = []
for item in manifest:
    actual = hashlib.sha256((DATA / item["file"]).read_bytes()).hexdigest()
    audit.append({"file": item["file"], "bytes": item["bytes"],
                  "licence": item["licence"], "verified": actual == item["sha256"]})
assert all(row["verified"] for row in audit), "A reference file changed. Review provenance."
display(pd.DataFrame(audit))
'''),
        ('Keep the three data families distinct', '''families = pd.DataFrame({
    "family": ["Observation-based", "Reanalysis", "Projection"],
    "examples": ["E-OBS, Berkeley Earth, CPC, SST-CCI", "ERA5, ERA5-Land, CERRA, ORAS5", "CMIP5, CMIP6, CORDEX"],
    "question": ["What did instruments observe?", "What physical state best fits available evidence?", "What could happen under stated forcings?"],
})
display(families)
''')],
       'Explain why two files with the same DOI can legitimately have different hashes.',
       'They can be different subsets, revisions, encodings, or derived products. Preserve both their provenance and transformations; do not silently replace a snapshot.',
       'Compare one observational dataset with one reanalysis. Record coverage, grid spacing, and a limitation before comparing values.',
       data='Authentic reference-file bytes and provenance manifest')

lesson('03-baselines-and-anomalies', 'Baselines, anomalies, and trends',
       'How much of a visual change comes from changing the reference period?',
       '''An absolute anomaly is a value minus a reference climatology. Monthly anomalies
       should remove the matching calendar month's normal. A warmer baseline shifts
       anomalies downward without changing differences between two dates.

       The example is a fictional region. We calculate an equal-month annual mean to make
       the aggregation explicit; a day-weighted mean is another statistic. The fitted line
       below is descriptive. Serial dependence, changing coverage, and model specification
       matter for trend uncertainty, so this lesson does not attach a naive p-value.''',
       [('Compare reference periods', '''df = monthly_demo()
df["a_old"] = anomalies(df, "t", (1961, 1990))
df["a_new"] = anomalies(df, "t", (1991, 2020))
annual = df.groupby("year")[["a_old", "a_new"]].mean()
fig = go.Figure()
for col, label in [("a_old", "1961–1990 baseline"), ("a_new", "1991–2020 baseline")]:
    fig.add_scatter(x=annual.index, y=annual[col], mode="lines", name=label)
fig.update_layout(title="One record, two baselines · SYNTHETIC", xaxis_title="Year", yaxis_title="Temperature anomaly (°C)")
show(fig)
assert np.isclose(df.loc[df.year.between(1991, 2020), "a_new"].mean(), 0)
'''),
        ('Check a descriptive slope', '''slope = np.polyfit(annual.index - annual.index.min(), annual.a_new, 1)[0]
print(f"Descriptive slope of the invented series: {10*slope:.3f} °C per decade")
display(annual.tail().round(3))
# Changing a constant annual baseline cannot change this slope.
assert np.isclose(slope, np.polyfit(annual.index - annual.index.min(), annual.a_old, 1)[0])
''')],
       'Use 1981–2010 as the baseline. Does the line slope change? Is 1991–2020 the same as pre-industrial?',
       'The anomaly offset changes; the descriptive slope is unchanged for the same complete series. A modern normal is not a pre-industrial baseline.',
       'Compare the Atlas values, absolute changes, and trends views. Record the different units and periods in their legends.')

lesson('04-seasons-and-stripes', 'Annual cycles and seasonal stripes',
       'Does an annual average conceal which months are changing?',
       '''A seasonal cycle keeps the calendar month visible. Seasonal stripes are a
       year-by-month anomaly matrix with one colour scale across all cells. Choose a
       diverging palette centred at zero for signed anomalies and retain a numerical legend.

       A season crossing New Year needs an explicit season-year rule. For DJF we assign
       December to the following year and exclude incomplete seasons. Seasonal counts
       should be summed; monthly extremes need max/min aggregation, not a mean.''',
       [('Compare monthly normals', '''df = monthly_demo()
fig = go.Figure()
for start, end in [(1961, 1990), (1991, 2020)]:
    cycle = df[df.year.between(start, end)].groupby("month").t.mean()
    fig.add_scatter(x=cycle.index, y=cycle.values, mode="lines+markers", name=f"{start}–{end}")
fig.update_layout(title="Seasonal cycle · SYNTHETIC", xaxis_title="Month", yaxis_title="Mean temperature (°C)")
show(fig)
'''),
        ('Expose month-by-month changes', '''df["anomaly"] = anomalies(df, "t", (1961, 1990))
matrix = df.pivot(index="year", columns="month", values="anomaly")
limit = np.abs(matrix.to_numpy()).max()
fig = go.Figure(go.Heatmap(x=matrix.columns, y=matrix.index, z=matrix.to_numpy(),
    colorscale="RdBu_r", zmin=-limit, zmax=limit, colorbar=dict(title="Δ °C")))
fig.update_layout(title="Seasonal stripes · SYNTHETIC", xaxis_title="Month", yaxis_title="Year")
show(fig)
# Require all three months; dropping absent months can bias a seasonal mean.
djf = df[df.month.isin([12, 1, 2])].copy()
djf["season_year"] = djf.year + (djf.month == 12).astype(int)
seasons = djf.groupby("season_year").agg(mean_t=("t", "mean"), n=("t", "count"))
display(seasons[seasons.n == 3].head())
''')],
       'Which DJF seasons are incomplete at the ends of the record, and why?',
       'DJF 1961 lacks December 1960; DJF 2021 lacks January and February 2021. Only 1962–2020 contain all three months.',
       'Compare the annual cycle and seasonal stripes for one region. Keep dataset, reference, baseline, and variable fixed.')

lesson('05-heat-and-cold', 'Heat, cold, and threshold indices',
       'Can a monthly mean tell you how many days exceeded 35 °C?',
       '''No: a mean loses the daily distribution. Count hot days from daily maxima and
       tropical nights from daily minima. A monthly maximum of daily maxima answers a
       different question from the monthly average of daily maxima.

       This invented daily year illustrates t, tn, tx, dtr, txx, tnn, tx35, tx40, tr,
       fd, cooling degree-days, and heating degree-days. Degree-days are temperature
       departures accumulated through time; they are not measured energy consumption.
       The base thresholds below follow the CDS catalogue's teaching definitions.''',
       [('Calculate from daily values', '''rng = np.random.default_rng(5)
dates = pd.date_range("2001-01-01", "2001-12-31", freq="D")
day = np.arange(len(dates))
mean_t = 15 + 13*np.cos(2*np.pi*(day-200)/365) + rng.normal(0, 2, len(day))
daily = pd.DataFrame({"date": dates, "t": mean_t, "tx": mean_t+7, "tn": mean_t-7})
summary = pd.Series({
    "tx35 days (>35 °C)": int((daily.tx > 35).sum()),
    "tx40 days (>40 °C)": int((daily.tx > 40).sum()),
    "tropical nights (>20 °C)": int((daily.tn > 20).sum()),
    "frost days (<0 °C)": int((daily.tn < 0).sum()),
    "cooling degree-days (base 22 °C)": np.maximum(daily.t-22, 0).sum(),
    "heating degree-days (base 15.5 °C)": np.maximum(15.5-daily.t, 0).sum(),
})
display(summary.round(1).to_frame("SYNTHETIC index value"))
assert summary.iloc[1] <= summary.iloc[0]
'''),
        ('See the information hidden by the mean', '''fig = go.Figure(go.Histogram(x=daily.tx, xbins=dict(size=2), name="Daily maxima"))
fig.add_vline(x=35, line_dash="dash", annotation_text="35 °C threshold")
fig.update_layout(title="Daily maximum distribution · SYNTHETIC", xaxis_title="Daily maximum temperature (°C)", yaxis_title="Days")
show(fig)
display(daily.assign(month=daily.date.dt.month).groupby("month").agg(
    tx_mean=("tx", "mean"), txx=("tx", "max"), tnn=("tn", "min")).round(2))
''')],
       'Add 1 °C to every daily maximum and recompute tx35. Why is the count response not necessarily linear?',
       'Only days near the threshold cross it. The response depends on the distribution, not just its mean. Bias adjustment therefore matters strongly for threshold counts.',
       'Compare t, txx, and tx35 for the same region. Check whether bias adjustment is available and whether the units change.')

lesson('06-rain-and-water', 'Rainfall, extremes, and the water cycle',
       'How can similar rainfall totals hide very different hazards?',
       '''Mean daily precipitation, wet-day intensity, a one-day maximum, a five-day
       maximum, and a dry-spell length answer different questions. Monthly mean daily
       amounts must be multiplied by days in the month to obtain totals when the product
       metadata define them that way. Never infer this merely from a variable name.

       Our count convention is explicitly ≥1 mm for wet days and ≥10/20 mm for heavy
       days; check the exact upstream comparator before reproducing an official index.
       Runoff, evaporation, humidity, and soil storage help interpret the water cycle,
       but precipitation minus evaporation alone does not close every regional budget.''',
       [('Compute daily precipitation diagnostics', '''rng = np.random.default_rng(6)
rain = pd.Series(np.where(rng.random(365) < 0.4, rng.gamma(1.4, 6, 365), 0.0))
wet = rain >= 1
stats = pd.Series({"annual total (mm)": rain.sum(), "wet days (≥1 mm)": wet.sum(),
    "heavy days (≥10 mm)": (rain >= 10).sum(), "very heavy days (≥20 mm)": (rain >= 20).sum(),
    "wet-day intensity (mm/day)": rain[wet].mean(), "Rx1day (mm)": rain.max(),
    "Rx5day (mm)": rain.rolling(5, min_periods=5).sum().max()})
display(stats.round(2).to_frame("SYNTHETIC"))
assert stats["Rx5day (mm)"] >= stats["Rx1day (mm)"]
'''),
        ('Trace the water input through the year', '''fig = go.Figure()
fig.add_bar(x=np.arange(1, 366), y=rain, name="Daily precipitation")
fig.add_scatter(x=np.arange(1, 366), y=rain.rolling(5).sum(), name="5-day total")
fig.update_layout(title="Rainfall timing · SYNTHETIC", xaxis_title="Day of year", yaxis_title="Precipitation (mm)")
show(fig)
df = monthly_demo()
df["monthly_total_mm"] = df.r * df.days
display(df[["date", "r", "days", "monthly_total_mm"]].head())
''')],
       'Reorder the daily rain values. Which diagnostics remain fixed, and which may change?',
       'The total, threshold counts, wet-day intensity, and one-day maximum remain fixed. Five-day extremes and consecutive dry-day spells depend on order.',
       'Compare precipitation with Rx1day and Rx5day. Read whether the selected seasonal statistic uses a mean, sum, or maximum.')

lesson('07-drought', 'Drought, water balance, and accumulation',
       'Why do drought indicators depend on both timescale and reference climate?',
       '''Meteorological, agricultural, and hydrological drought refer to different
       parts of the system. Six-month precipitation and precipitation minus potential
       evapotranspiration describe accumulated supply and atmospheric demand. Soil moisture
       and runoff offer different evidence.

       The calculation here is a six-month water-balance sum, **not SPI-6 or SPEI-6**.
       Those indices need distribution fitting and a specified calibration period.
       Standardising with a simple mean and standard deviation is not a faithful substitute.
       Consult the upstream implementation for the current PET method and calibration.''',
       [('Track accumulated deficit', '''df = monthly_demo()
df["balance_mm"] = (df.r - df.pet) * df.days
df["balance_6month_mm"] = df.balance_mm.rolling(6, min_periods=6).sum()
assert df.balance_6month_mm.iloc[:5].isna().all()
fig = go.Figure(go.Scatter(x=df.date, y=df.balance_6month_mm, fill="tozeroy", name="Six-month P − PET"))
fig.add_hline(y=0, line_dash="dot")
fig.update_layout(title="Accumulated water balance, not SPEI · SYNTHETIC", xaxis_title="Month", yaxis_title="Six-month water balance (mm)")
show(fig)
'''),
        ('Count a dry spell without erasing missing days', '''# A small hand-checkable sequence. Missing breaks a confirmed spell and must be reported.
daily_rain = np.array([0.0, 0.2, 1.0, 0.0, 0.0, 0.0, 4.0])
run = longest = 0
for amount in daily_rain:
    run = run + 1 if np.isfinite(amount) and amount < 1 else 0
    longest = max(longest, run)
print("Longest confirmed dry spell:", longest, "days")
assert longest == 3
print("On incomplete real daily data this is a lower bound, not a complete annual CDD.")
''')],
       'Change the accumulation from 6 to 12 months. Why does the response become smoother?',
       'Longer windows integrate more months, spreading short disturbances over time. Overlapping windows are strongly dependent; they are not independent samples.',
       'Compare SPI-6, SPEI-6, soil moisture, and runoff where available. Record both the index calibration period and the display baseline.',
       sources=[('Upstream drought methods', 'https://github.com/ecmwf-projects/c3s-atlas/blob/main/book/notebooks/spei6.ipynb')])

lesson('08-wind-and-radiation', 'Wind, radiation, and energy context',
       'Why is a climate variable not already an energy-production estimate?',
       '''Near-surface wind speed, cloud fraction, and downward shortwave/longwave
       radiation describe physical conditions. Turbine output also depends on hub height,
       the turbine power curve, air density, losses, and operations. Solar production also
       depends on module orientation, temperature, shading, and equipment.

       An ideal wind-power density is proportional to the cube of speed. Cubing the mean
       wind is generally not the same as averaging the cube. This is a demonstration of
       nonlinear averaging, not a renewable-energy forecast.''',
       [('Show nonlinear averaging', '''rng = np.random.default_rng(8)
wind = rng.weibull(2.2, 1000)*7
rho = 1.225  # Illustrative constant density in kg/m³; not a turbine model.
mean_power_density = np.mean(0.5*rho*wind**3)
power_at_mean_wind = 0.5*rho*wind.mean()**3
display(pd.Series({"mean ideal power density (W/m²)": mean_power_density,
    "ideal power density at mean speed (W/m²)": power_at_mean_wind}).round(1).to_frame())
assert mean_power_density > power_at_mean_wind
fig = go.Figure(go.Histogram(x=wind, nbinsx=30))
fig.update_layout(title="Wind variability matters · SYNTHETIC", xaxis_title="Wind speed (m/s)", yaxis_title="Samples")
show(fig)
'''),
        ('Convert a radiation flux to an energy per area', '''# A constant illustrative monthly mean flux, not a station observation.
flux_w_m2, days = 180.0, 30
energy_kwh_m2 = flux_w_m2 * 24 * days / 1000
print(f"{flux_w_m2:g} W/m² for {days} days = {energy_kwh_m2:g} kWh/m²")
print("This is incoming energy per area, not electricity generated.")
''')],
       'Would this wind sample identify the expected output of a particular turbine?',
       'No. The ideal cubic relation omits cut-in/rated/cut-out behaviour, hub-height conditions, and operational losses.',
       'Explore sfcwind, rsds, rlds, and cloud cover. Record which data families provide each variable.')

lesson('09-snow-and-ice', 'Snow, sea ice, and what area means',
       'What is the difference between sea-ice area and thresholded extent?',
       '''Sea-ice concentration is the fraction of a grid cell covered by ice. Ice area
       sums concentration times cell area. An extent calculation counts the whole cell
       when concentration passes a stated threshold. The two quantities should not be
       labelled interchangeably.

       Snowfall water equivalent is not snow depth: depth depends on density, settling,
       and melt. Monthly maps also conceal daily timing. The miniature example uses
       equal-area fictional cells to make the arithmetic inspectable.''',
       [('Calculate area and thresholded extent', '''cell_km2 = np.array([100., 100., 100., 100., 100.])
concentration = np.array([1.0, 0.8, 0.4, 0.15, 0.05])
threshold = 0.15  # Chosen teaching threshold; always state it with an extent result.
area = np.sum(cell_km2 * concentration)
extent = np.sum(cell_km2[concentration >= threshold])
print(f"Ice area: {area:g} km²; extent at ≥{threshold:.0%}: {extent:g} km²")
assert np.isclose(area, 240) and np.isclose(extent, 400)
fig = go.Figure(go.Bar(x=[f"cell {i}" for i in range(1, 6)], y=concentration*100))
fig.add_hline(y=threshold*100, line_dash="dash")
fig.update_layout(title="Partial ice cover · SYNTHETIC", xaxis_title="Equal-area cell", yaxis_title="Ice concentration (%)")
show(fig)
'''),
        ('Test an extent discontinuity', '''changed = concentration.copy()
changed[3] = 0.149
print("Area change (km²):", np.sum(cell_km2*(changed-concentration)))
print("Extent change (km²):", cell_km2[changed >= threshold].sum()-extent)
''')],
       'Why does changing 15% to 14.9% produce a large extent change?',
       'A threshold converts a continuous fraction into a whole-cell decision. Extent changes discontinuously; area changes continuously.',
       'Compare sea-ice concentration with snowfall. Read the units, domain mask, and dataset availability for each.')

lesson('10-ocean-and-circulation', 'Ocean temperature and atmospheric circulation',
       'What can a spatial pattern tell you that a global average cannot?',
       '''Sea-surface temperature describes the ocean surface, not the whole ocean's heat
       content. Sea-level pressure patterns help describe atmospheric circulation, but
       a pressure map alone does not establish the cause of a temperature anomaly.

       Mask land before interpreting a real SST field. Seasonal cycles and reference
       periods must match before comparing anomalies. These analytic fields are fictional
       and illustrate map reading; they are not reconstructed events.''',
       [('Compare two spatial fields', '''lon, lat, _ = regular_grid()
xx, yy = np.meshgrid(lon, lat)
sst_anomaly = 0.8*np.cos(np.deg2rad(yy))*np.sin(2*np.deg2rad(xx))
pressure_anomaly = 5*np.sin(np.deg2rad(yy))*np.cos(np.deg2rad(xx))
fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
for ax, field, title, unit in zip(axes, [sst_anomaly, pressure_anomaly],
        ["SST-like anomaly (unmasked teaching field)", "Sea-level-pressure-like anomaly"], ["°C", "hPa"]):
    lim = np.abs(field).max()
    m = ax.pcolormesh(lon, lat, field, cmap="RdBu_r", vmin=-lim, vmax=lim, shading="auto")
    ax.set(xlabel="Longitude (°)", ylabel="Latitude (°)", title=title)
    fig.colorbar(m, ax=ax, label=unit)
fig.suptitle("SYNTHETIC — no physical coupling fitted")
plt.show()
'''),
        ('Make the comparison limits explicit', '''display(pd.DataFrame({
    "quantity": ["SST anomaly", "Pressure anomaly"],
    "unit": ["°C", "hPa"],
    "required metadata": ["ocean mask, source product, baseline", "reference level, source product, baseline"],
    "cannot infer alone": ["total ocean heat content", "a causal effect on local rainfall"],
}))
''')],
       'Why is a colour match between these two maps not a numerical match?',
       'The variables use different units and scales. Spatial alignment also does not establish a physical causal relationship.',
       'Explore SST from an ocean or satellite product and sea-level pressure from an atmospheric product. Keep their provenance separate.')

lesson('11-scenarios-and-ensembles', 'Scenarios, models, and ensemble spread',
       'How do you compare conditional futures without treating them as probabilities?',
       '''A scenario specifies assumptions about future forcing; a model simulates a
       response. An ensemble samples model responses and sometimes initial conditions.
       The fraction of models with a result is not automatically the probability of that
       result. Model genealogies and shared assumptions affect independence.

       These trajectories are invented. Their labels say lower and higher forcing to
       avoid presenting them as numerical SSP projections. The shaded band is the
       10th–90th percentile across invented members, not a confidence interval.''',
       [('Inspect the ensemble rather than only its average', '''rng = np.random.default_rng(11)
years = np.arange(2020, 2101)
ensembles = {}
fig = go.Figure()
for label, rate, color in [("Lower forcing illustration", 0.014, COLORS[0]), ("Higher forcing illustration", 0.045, COLORS[1])]:
    members = 1.1 + (years-2020)[None, :]*rng.normal(rate, rate*0.18, (20, 1)) + rng.normal(0, 0.08, (20, len(years)))
    ensembles[label] = members
    lo, med, hi = np.quantile(members, [0.1, 0.5, 0.9], axis=0)
    fig.add_scatter(x=years, y=lo, line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=years, y=hi, fill="tonexty", line=dict(width=0), opacity=0.2, name=f"{label}: 10–90% members")
    fig.add_scatter(x=years, y=med, line=dict(color=color), name=f"{label}: median")
fig.update_layout(title="Conditional pathways · SYNTHETIC", xaxis_title="Year", yaxis_title="Illustrative anomaly (°C)")
show(fig)
'''),
        ('Compare the same period in both ensembles', '''rows = []
for name, members in ensembles.items():
    late = members[:, years >= 2081].mean(axis=1)
    rows.append({"illustration": name, "members": len(late), "median": np.median(late),
                 "p10": np.quantile(late, .1), "p90": np.quantile(late, .9)})
display(pd.DataFrame(rows).round(2))
''')],
       'Why should historical and future simulations be matched by model/member identifier before differencing?',
       'Otherwise the change may partly reflect a change in ensemble composition. Report the intersection, exclusions, weighting, and available sample size.',
       'Compare two CMIP6 scenarios for the same variable and future period. Inspect the members and uncertainty legend.')

lesson('12-global-warming-levels', 'Global warming levels with real Atlas data',
       'Does a 2 °C warming level refer to one calendar year for every model?',
       '''No. A warming-level view aligns model-specific windows at a common amount
       of global warming. The bundled upstream CMIP6 table contains actual 20-year
       windows for several scenarios. Its numeric coordinates below are window midpoints,
       **not forecasts of the first year the observed planet reaches a threshold**.

       We retain both `NA` and `9999` literally and exclude them from date arithmetic.
       An absent window is not year zero and is not evidence of zero warming. This
       chapter reports source tokens without guessing whether absence means non-attainment,
       unavailable data, or a workflow-specific exclusion. The official Atlas warming-level
       calculation uses a specified high-forcing pathway; cross-scenario plots here explore
       the auxiliary table, not a recreation of the official display.''',
       [('Parse and inspect the real table', '''gwl = warming_levels()
display(gwl.groupby(["scenario", "status"]).size().unstack(fill_value=0))
display(gwl[gwl.status == "window"].head())
assert (gwl.loc[gwl.status == "window", "end"] - gwl.loc[gwl.status == "window", "start"]).eq(19).all()
'''),
        ('Compare valid model-specific windows', '''selected = gwl[(gwl.scenario == "ssp585") & (gwl.status == "window")]
fig = go.Figure()
for level in sorted(selected.level.unique()):
    part = selected[selected.level == level]
    fig.add_trace(go.Box(y=part.midpoint, name=f"{level:g} °C", boxpoints="all", jitter=.3,
        text=part.member, hovertemplate="%{text}<br>window midpoint %{y}<extra></extra>"))
fig.update_layout(title="Real CMIP6 auxiliary windows · SSP5-8.5", xaxis_title="Global warming level above 1850–1900", yaxis_title="20-year window midpoint")
show(fig)
display(selected.groupby("level").agg(n=("member", "size"), first_midpoint=("midpoint", "min"), last_midpoint=("midpoint", "max")))
''')],
       'Change the scenario to ssp126. Explain why different sample sizes matter when comparing boxes.',
       'Different levels/scenarios can have different valid members. Compare a common member set when appropriate and retain missing-status counts; boxes are not equal-probability forecasts.',
       'In the Atlas, switch between future periods and warming levels. Inspect the model windows and the chosen baseline.',
       data='Real upstream CMIP6 warming-level table, unmodified, pinned in data/manifest.json',
       sources=[('Source table and authors', 'https://github.com/ecmwf-projects/c3s-atlas/blob/main/auxiliar/GWLs/CMIP6_WarmingLevels.csv'), ('GWL implementation', 'https://github.com/ecmwf-projects/c3s-atlas/blob/main/book/notebooks/GWLs.ipynb')])

lesson('13-uncertainty-and-bias', 'Uncertainty and bias adjustment',
       'Can a corrected mean still leave the wrong extreme behaviour?',
       '''Yes. A mean shift can align the average while leaving variability and tails
       wrong. Bias adjustment requires a calibration period, an observational reference,
       and a method appropriate to the variable. It cannot eliminate scenario uncertainty
       or create reliable local detail that was absent from the model.

       Sign agreement across models is useful descriptive information, but it is not
       the complete Atlas robustness classification. This lesson deliberately does not
       reproduce official hatching from a single arbitrary agreement threshold.''',
       [('Separate mean bias from tail error', '''rng = np.random.default_rng(13)
reference = rng.normal(30, 3, 5000)
model = rng.normal(32, 5, 5000)
adjusted = model - model.mean() + reference.mean()
summary = pd.DataFrame({"series": ["reference", "model", "mean-shifted model"],
    "mean": [x.mean() for x in [reference, model, adjusted]],
    "p95": [np.quantile(x, .95) for x in [reference, model, adjusted]],
    "fraction above 35 °C": [(x > 35).mean() for x in [reference, model, adjusted]]})
display(summary.round(3))
fig = go.Figure()
for label, values in [("Reference", reference), ("Model", model), ("Mean shifted", adjusted)]:
    fig.add_histogram(x=values, histnorm="probability density", opacity=.45, name=label)
fig.update_layout(barmode="overlay", title="Mean correction leaves tail differences · SYNTHETIC", xaxis_title="Daily maximum temperature (°C)", yaxis_title="Density (1/°C)")
show(fig)
'''),
        ('Count sign agreement honestly', '''changes = np.array([-0.3, 0.2, 0.5, 0.7, 0.8, 1.0, 1.2, 1.5])
print("Invented members with positive change:", (changes > 0).sum(), "of", len(changes))
print("This fraction is not a probability, a p-value, or the official robustness mask.")
''')],
       'Why is evaluating the adjustment on the same reference sample not independent validation?',
       'The adjustment was tuned using that sample. Validate on held-out periods and examine tails, seasonality, and physical consistency, while acknowledging climate non-stationarity.',
       'Read the exact Atlas uncertainty legend for a trend and for a projection change. Explain why they use different evidence.',
       sources=[('Bias adjustment user tools', 'https://github.com/ecmwf-projects/c3s-atlas/blob/main/book/notebooks/tx35bals.ipynb')])

lesson('14-regions-and-weights', 'Regions, masks, and area weighting',
       'Why should a grid cell near the pole receive less weight?',
       '''Equal angular latitude/longitude cells do not have equal physical area.
       On a complete regular grid, cosine-latitude weights give the relative cell areas.
       For irregular grids use provided cell areas; for clipped polygons account for
       fractional overlap. A rectangular mask is not a coastline, country boundary,
       or IPCC reference region.

       Missing cells change the area represented by the mean. A calculation that
       renormalises over valid cells must also report coverage. A regional average
       does not describe every community or imply population-weighted exposure.''',
       [('Compare weighted and unweighted means', '''lon, lat, field = regular_grid()
weighted = area_mean(field, lat)
unweighted = field.mean()
print(f"Synthetic field: area mean {weighted:.3f} °C; unweighted mean {unweighted:.3f} °C")
assert weighted < unweighted  # The invented pattern is warmer at high latitudes.
xx, yy = np.meshgrid(lon, lat)
mask = (xx >= -10) & (xx <= 40) & (yy >= 30) & (yy <= 70)
regional = np.where(mask, field, np.nan)
print(f"Rectangular teaching region: {area_mean(regional, lat):.3f} °C")
show(map_figure(lon, lat, regional, "A rectangular region · SYNTHETIC"))
'''),
        ('Report missing area', '''weights = np.broadcast_to(np.cos(np.deg2rad(lat))[:, None], field.shape)
available = mask.copy()
available[lat > 60] = False
coverage = weights[available].sum() / weights[mask].sum()
print(f"Represented fraction of requested region area: {coverage:.1%}")
print("Renormalised mean:", area_mean(np.where(available, field, np.nan), lat))
''')],
       'Move the missing area from the north to the south. Does the mean change even when coverage is similar?',
       'Yes. Missingness can be spatially structured. Report both coverage and the missing-region pattern, not just a renormalised average.',
       'Compare a predefined region with a custom selection. Record the mask and weighting assumptions.',
       sources=[('xarray area-weighting tutorial — Mathias Hauser', 'https://docs.xarray.dev/en/stable/examples/area_weighted_temperature.html'), ('IPCC reference regions — Iturbide et al.', 'https://doi.org/10.5194/essd-12-2959-2020')])

lesson('15-interactive-2d-maps', 'Interactive 2D maps and honest legends',
       'What choices make a map easier to compare and harder to misread?',
       '''Use a sequential palette for ordered nonnegative quantities and a diverging
       palette with a meaningful centre for signed changes. Fix colour limits across
       comparisons; autoscaling can make different magnitudes look identical.

       This is a plate carrée map with longitude and latitude in degrees, not an
       equal-area projection. Zoom and hover are interactive. The bundled coastlines
       are public-domain Natural Earth data; the climate field is invented. No map
       service key, external tiles, or upload is required.''',
       [('Explore an interactive field', '''lon, lat, field = regular_grid()
fig = map_figure(lon, lat, field, "Read the coordinates and colour scale · SYNTHETIC")
show(fig)
display(pd.DataFrame(field[::6, ::12], index=lat[::6], columns=lon[::12]).round(2))
'''),
        ('Compare fixed colour limits in a static fallback', '''fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
for ax, factor in zip(axes, [1, 1.5]):
    im = ax.pcolormesh(lon, lat, field*factor, cmap="cividis", vmin=0, vmax=5, shading="auto")
    for line in coastlines():
        for segment in np.split(line, np.where(np.abs(np.diff(line[:, 0])) > 180)[0]+1):
            ax.plot(segment[:, 0], segment[:, 1], color="#183044", lw=.4)
    ax.set(title=f"Invented field × {factor}", xlabel="Longitude (°)", ylabel="Latitude (°)", xlim=(-180, 180), ylim=(-90, 90))
fig.colorbar(im, ax=axes, label="Illustrative anomaly (°C)")
fig.suptitle("SYNTHETIC · common colour limits · Natural Earth coastlines")
plt.show()
''')],
       'Set independent colour limits in each panel. Which comparison becomes misleading?',
       'The same colour can represent different magnitudes. Retain common scales when the purpose is direct numerical comparison.',
       'Choose a fixed range in the official map legend and compare two periods. Describe the change numerically as well as visually.',
       sources=[('Natural Earth terms and contributors', 'https://www.naturalearthdata.com/about/terms-of-use/')])

lesson('16-globes-and-3d-maps', 'Globes and three-dimensional climate maps',
       'What changes when a climate field is draped over a globe?',
       '''The globe removes the stretched polar appearance of a rectangular world map,
       but hides the far side. Rotate it to inspect that occlusion. Here all locations
       lie on a unit sphere: colour shows an invented anomaly; radius is not elevation
       and is not temperature.

       WebGL is required for the rotating globe. If your browser cannot render it,
       use the 2D map and numerical table. Coastlines provide orientation; they do not
       add geographic precision to a coarse climate field.''',
       [('Rotate the globe', '''show(globe_figure())
'''),
        ('Relate spherical coordinates to geography', '''longitude, latitude = -75.0, 40.0
lam, phi = np.deg2rad([longitude, latitude])
xyz = np.array([np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)])
print("Unit-sphere coordinates:", xyz.round(4))
assert np.isclose(np.linalg.norm(xyz), 1)
lon, lat, field = regular_grid()
show(map_figure(lon, lat, field, "2D alternative to the globe · SYNTHETIC"))
''')],
       'Which parts of the planet are concealed in the initial view? Can a globe replace a table of values?',
       'Roughly the far hemisphere is occluded. Rotate the view and use the map/table for exact comparison; perspective is not a numerical scale.',
       'Inspect the official Atlas geographical view options, then compare them with this independent educational globe.',
       sources=[('Plotly surface documentation', 'https://plotly.com/python/3d-surface-plots/')])

lesson('17-3d-scenes', '3D scenes: time, season, and climate',
       'When does a third axis clarify a pattern, and when does it obscure one?',
       '''A 3D scene need not be terrain. This scene places year and calendar month on
       the horizontal axes and a temperature anomaly on the vertical axis. Height is
       in degrees Celsius, not metres. Perspective and occlusion make exact comparisons
       harder, so a flat heatmap accompanies the surface.

       This is a climate data scene, not a digital twin, city model, or flood-inundation
       model. Neither an artistic surface nor a climate hazard layer is a complete risk
       estimate: exposure and vulnerability would need their own data and methods.''',
       [('Explore a year–month surface', '''df = monthly_demo()
df["anomaly"] = anomalies(df, "t", (1961, 1990))
matrix = df.pivot(index="month", columns="year", values="anomaly")
fig = go.Figure(go.Surface(x=matrix.columns, y=matrix.index, z=matrix.to_numpy(),
    colorscale="RdBu_r", cmid=0, colorbar=dict(title="Δ °C")))
fig.update_layout(title="Climate through time and season · SYNTHETIC",
    scene=dict(xaxis_title="Year", yaxis_title="Month", zaxis_title="Anomaly (°C)", aspectratio=dict(x=2, y=1, z=.7)))
show(fig)
'''),
        ('Use the flat alternative for exact comparisons', '''fig = go.Figure(go.Heatmap(x=matrix.columns, y=matrix.index, z=matrix.to_numpy(),
    colorscale="RdBu_r", zmid=0, colorbar=dict(title="Δ °C")))
fig.update_layout(title="Same values without perspective · SYNTHETIC", xaxis_title="Year", yaxis_title="Month")
show(fig)
display(matrix.iloc[:, -3:].round(2))
''')],
       'Change the vertical aspect ratio. Did the data change? Which view supports reading a particular month?',
       'Only the apparent steepness changes. A heatmap with hover or its numeric table is better for locating and comparing specific values.',
       'Use the Atlas seasonal stripes for a real region. Explain how the same year-by-month matrix could be displayed as a scene without adding new information.')

lesson('18-monitoring-and-urban', 'Monitoring and urban context',
       'How do you separate a recent anomaly from a city–rural contrast?',
       '''Monitoring compares current conditions with a stated historical reference.
       A single unusual month is not a long-term trend. Preliminary data, incomplete
       months, and changing station coverage can affect the comparison.

       Urban heat can involve different surface and air-temperature definitions and
       different day/night contrasts. A global grid cell is not a street-level exposure
       estimate. The fictional paired records below illustrate a city–rural difference;
       they do not reproduce the Atlas urban product or establish causation.''',
       [('Display a paired contrast', '''hour = np.arange(24)
rural = 23 + 6*np.sin(2*np.pi*(hour-8)/24)
urban = rural + 1.5 + 1.2*np.cos(2*np.pi*(hour-2)/24)
fig = go.Figure()
for label, values in [("Fictional rural air", rural), ("Fictional city air", urban)]:
    fig.add_scatter(x=hour, y=values, mode="lines+markers", name=label)
fig.update_layout(title="A paired daily cycle · SYNTHETIC", xaxis_title="Local hour", yaxis_title="Air temperature (°C)")
show(fig)
display(pd.DataFrame({"hour": hour, "urban_minus_rural_C": urban-rural}).round(2))
'''),
        ('Build a monitoring evidence checklist', '''display(pd.DataFrame({
    "check": ["Coverage", "Status", "Reference", "Variable", "Location"],
    "record": ["complete month or partial month", "preliminary or consolidated", "exact reference years", "surface or air; daily mean/min/max", "grid, station, city mask and rural comparator"],
}))
''')],
       'Why is subtracting a rural afternoon observation from a city nighttime observation not a valid paired contrast?',
       'Time of day is confounded with location. Match times, variable definitions, instrumentation, and coverage before interpreting the difference.',
       'Explore monitoring and urban views where the official application offers them. Record availability and product-specific limitations.',
       sources=[('Official urban workflow', 'https://github.com/ecmwf-projects/c3s-atlas/blob/main/book/notebooks/UHI.ipynb')])

lesson('19-bring-real-data', 'Bring a real C3S export into the browser',
       'How do you replace a teaching example without silently changing its meaning?',
       '''Use the official Atlas export controls or CDS to obtain a small regional
       series. Keep the original file and metadata. Atlas CSV layouts vary by product;
       inspect the headers and explicitly map the relevant time/value columns to the
       simple schema below. Do not guess a date column or discard model identities.

       Upload a prepared `my_series.csv` and `my_series.json` through the JupyterLite
       file browser. Required CSV columns are `date,value` with one ISO month-start row
       per month. The JSON sidecar records provenance and units. **Never upload a CDS
       API key.** Use the desktop preparation tool for large NetCDF files; browser memory
       and compiled-library availability are limited.''',
       [('Validate the documented teaching fixture', '''# This file demonstrates the import contract. It is labelled synthetic in its sidecar.
source_path = DATA / "examples/monthly_series.csv"
series = load_monthly_csv(source_path)
metadata = json.loads(source_path.with_suffix(".json").read_text(encoding='utf-8'))
display(pd.Series(metadata).to_frame("Provenance"))
display(series.head())
assert metadata["data_kind"] == "synthetic"
'''),
        ('Use an uploaded pair when present', '''# Set these paths to your uploaded files. Absence is reported; no fake real data are substituted.
csv_path, meta_path = Path("my_series.csv"), Path("my_series.json")
if csv_path.exists() and meta_path.exists():
    actual = load_monthly_csv(csv_path)
    provenance = json.loads(meta_path.read_text(encoding='utf-8'))
    required = {"data_kind", "source", "variable", "units", "region", "statistic", "reference_period", "licence", "transformations"}
    missing = required - provenance.keys()
    if missing:
        raise ValueError(f"Missing provenance fields: {sorted(missing)}")
    if not all(str(provenance[k]).strip() for k in required):
        raise ValueError("Provenance fields must be populated.")
    display(pd.Series(provenance).to_frame("Imported source"))
    fig = go.Figure(go.Scatter(x=actual.date, y=actual.value, connectgaps=False))
    fig.update_layout(title=f"{provenance['data_kind']}: {provenance['variable']} · {provenance['region']}",
        xaxis_title="Month", yaxis_title=provenance["units"])
    show(fig)
else:
    print("No uploaded file pair found. The example above is synthetic; no real-data analysis was run.")
''')],
       'Insert a duplicate month into a copy of the example. Does the validator stop? Why should it?',
       'Yes. Two rows for a month might be duplicates or different models/regions; averaging them silently would invent a processing decision. Resolve the identity first.',
       'Download one regional time series and retain its information-panel provenance. Follow the data guide to prepare a single-series CSV and sidecar.',
       data='Synthetic import fixture by default; optional explicit user-provided real-data pair',
       sources=[('CDS API guide', 'https://cds.climate.copernicus.eu/how-to-api')])

lesson('20-capstone', 'A reproducible regional climate story',
       'Can you communicate one result without overstating the evidence?',
       '''Build a small evidence card before writing a narrative. State the question,
       dataset identity, variable, spatial support, periods, method, finding, uncertainty,
       and limitation. Include source authors, data DOI/licence, transformations, and
       access date. A valid computation can still answer the wrong scientific question.

       The worked capstone below uses **real auxiliary warming-level windows** and makes
       a deliberately narrow descriptive claim. Extend it with an actual regional C3S
       export from Chapter 19. Do not turn a global warming-level table into a local
       impact estimate or report an ensemble fraction as an event probability.''',
       [('Calculate an auditable result from real data', '''table = warming_levels()
subset = table[(table.scenario == "ssp585") & (table.level == 2)]
valid = subset[subset.status == "window"]
assert len(valid) > 0
result = {"members listed": len(subset), "valid windows": len(valid),
    "median window midpoint": float(valid.midpoint.median()),
    "earliest window start": int(valid.start.min()), "latest window end": int(valid.end.max())}
display(pd.Series(result).to_frame("Real upstream table summary"))
fig = go.Figure(go.Scatter(x=valid.midpoint, y=valid.member, mode="markers",
    error_x=dict(type="data", array=np.full(len(valid), 9.5), visible=True)))
fig.update_layout(title="Real CMIP6 SSP5-8.5 windows at 2 °C", xaxis_title="Inclusive 20-year window (calendar years)", yaxis_title="Model/member")
show(fig)
'''),
        ('Compose a bounded evidence card', '''card = {
    "question": "Which 20-year windows are listed for 2 °C under SSP5-8.5?",
    "data": "Pinned C3S Atlas User Tools CMIP6 auxiliary table",
    "method": "Parse valid windows; preserve NA/9999 separately; describe midpoint distribution",
    "finding": f"{len(valid)} of {len(subset)} listed members have a numeric window; median midpoint {valid.midpoint.median():.1f}.",
    "uncertainty": "Model spread and differing availability; no probabilistic forecast inferred",
    "limitation": "Global warming-level windows do not give regional hazard or observed threshold dates",
    "credit": "European Union; C3S Atlas User Tools contributors; CMIP6 modelling groups",
    "source": "https://github.com/ecmwf-projects/c3s-atlas/tree/main/auxiliar/GWLs",
    "licence": "Apache-2.0, upstream repository; see data/manifest.json and bundled licence",
}
display(pd.Series(card).to_frame("Evidence card"))
''')],
       'Build a second card from a real regional export. Include a fixed-scale map or chart, exact units, and an alternative explanation or limitation.',
       'A complete card must identify its source and transformations, show a reproducible calculation, separate uncertainty types, and limit its claim to the available spatial and temporal support.',
       'Recreate your selected result in the official Atlas. Explain any difference in members, aggregation, periods, masks, or version.',
       data='Real CMIP6 auxiliary warming-level table; independent regional extension uses user-supplied C3S data')


def main():
    """Write notebook sources; execution and site builds are separate explicit steps."""
    (CONTENT / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'assets/atlas-splash.png', CONTENT / 'assets/atlas-splash.png')
    for position, entry in enumerate(LESSONS):
        title, slug = entry['title'], entry['slug']
        cells = [nbf.v4.new_markdown_cell(f'''![Original climate-globe illustration introducing {title}; illustrative, not a data map](assets/atlas-splash.png)

# {position+1:02d} · {title}

**Guiding question:** {entry['question']}

**Data:** {entry['data']}  
**Time:** 20–35 minutes · **Prerequisites:** basic Python; run cells from top to bottom.  
**Author:** JupyterLite-C3S-Atlas contributors (AI assisted) · **Created/updated:** 2026-11-15  
**Inputs:** bundled reference files and/or seeded examples specified below. **Outputs:** in-memory tables and figures; source data are not modified.  
**Runtime:** Python/Pyodide; NumPy, pandas, Matplotlib, Plotly; versions and tests are recorded in the validation report.  
**Change log:** initial educational chapter. **Contact:** [repository issues](https://github.com/jltobias/JupyterLite-C3S-Atlas/issues).

[Open in JupyterLite Lab](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path={slug}.ipynb) · [Official Atlas]({ATLAS})
'''), nbf.v4.new_markdown_cell('## Read the evidence\n\n' + textwrap.dedent(entry['concepts']).strip()),
                 nbf.v4.new_markdown_cell('## Start the browser lab\n\nRun this setup cell once. First load needs internet for the Python runtime and packages. The remaining lesson uses bundled data. If a 3D view is unavailable, use the 2D/table alternative. Download your edited notebook before clearing browser storage.'),
                 nbf.v4.new_code_cell(BOOTSTRAP)]
        for heading, source in entry['blocks']:
            cells.extend([nbf.v4.new_markdown_cell('## '+heading), nbf.v4.new_code_cell(textwrap.dedent(source).strip())])
        cells.extend([
            nbf.v4.new_markdown_cell('## Try it and explain\n\n'+entry['exercise']),
            nbf.v4.new_markdown_cell('**Interpretation check:** '+entry['answer']),
            nbf.v4.new_markdown_cell('## Transfer to the official Atlas\n\n'+entry['atlas_task']+'\n\nRecord the selections, source version, units, periods, and uncertainty legend. These independent lessons do not duplicate every production workflow in the official tools.'),
            nbf.v4.new_markdown_cell('## Sources and credit\n\n'+ '\n'.join(f'- [{label}]({url})' for label, url in [
                ('C3S Atlas dataset and DOI', DATASET), ('CSIC / Predictia Atlas user guide', GUIDE),
                ('Official C3S Atlas User Tools and contributors', UPSTREAM)] + entry['sources']) +
                '\n\nOriginal teaching text and code; original AI-generated splash illustration. Real reference files retain their source licences. Synthetic examples are not Copernicus measurements. See [credits](credits.md) and [data guide](data-guide.md).')
        ])
        if position+1 < len(LESSONS):
            next_entry = LESSONS[position+1]
            cells.append(nbf.v4.new_markdown_cell(f"**Continue:** [{next_entry['title']}]({next_entry['slug']}.ipynb)"))
        notebook = nbf.v4.new_notebook(cells=cells, metadata={
            'kernelspec': {'display_name': 'Python (Pyodide)', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.13'},
            'atlas': {'data_kind': entry['data'], 'chapter': position+1},
        })
        # Stable cell IDs make regeneration reviewable rather than changing every cell.
        for i, cell in enumerate(notebook.cells):
            cell['id'] = f'chapter-{position+1:02d}-cell-{i:02d}'
        nbf.write(notebook, CONTENT / f'{slug}.ipynb')
    (ROOT / 'curriculum.json').write_text(json.dumps([
        {k: e[k] for k in ['slug', 'title', 'question', 'data']} for e in LESSONS], indent=2)+'\n', encoding='utf-8')
    print(f'Wrote {len(LESSONS)} notebook sources.')


if __name__ == '__main__':
    main()
