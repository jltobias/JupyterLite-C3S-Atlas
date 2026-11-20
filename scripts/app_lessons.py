"""Original app-connected lessons and launch examples, 2026-11-20.

Uses existing licensed Pulse CSVs and an attributed factual applications index.
No external service is contacted when the notebooks execute by default.
"""
CATALOGUE='https://apps.climate.copernicus.eu/'
PULSE='https://pulse.climate.copernicus.eu/'
BOOT='''from app_helpers import pulse_link, complete_years, read_pulse_monthly_csv, compare_pulse_exports, apps_catalogue
from pulse_helpers import load_pulse, ANOM, REL
from IPython.display import Markdown
'''


def register(lesson, lessons):
    # Extend existing worked examples with the official application's actual query keys.
    for entry in lessons:
        slug=entry['slug']
        choices={
            '21-climate-pulse-observatory': ('daily','2026-11-18','anomaly'),
            '23-pulse-baselines': ('monthly','2026-10-01','absolute'),
            '24-relative-enso': ('monthly','2026-10-01','relative'),
            '26-pulse-maps-and-globes': ('monthly','2026-10-01','anomaly'),
        }
        if slug in choices:
            aggregation,date,quantity=choices[slug]
            entry['blocks'].append(('Open the same selection in official Climate Pulse',f'''from app_helpers import pulse_link
from IPython.display import Markdown
url = pulse_link(region="nino34", aggregation="{aggregation}", date="{date}", quantity="{quantity}")
display(Markdown(f"[Open this selection in the official Climate Pulse app]({{url}})"))
print("Check the displayed region, date, aggregation, quantity, and baseline after opening.")
print("The official app may update or revise its data. The notebook keeps its dated snapshot.")
print("For a gridded map, use Pulse’s map view and probe; a relative Niño index is a regional time series.")
'''))
            entry['sources'].append(('Official Climate Pulse application',PULSE))

    def add(slug,title,question,concepts,blocks,exercise,answer,transfer,data,sources):
        blocks[0]=(blocks[0][0],BOOT+blocks[0][1])
        lesson(slug,title,question,concepts,blocks,exercise,answer,transfer,data=data,
               sources=[('Official Climate Pulse',PULSE),('Copernicus Data Stores Applications',CATALOGUE)]+sources)

    add('30-global-pulse-workshop','Global temperature: from Pulse to Python',
        'How do global air and ocean records answer different questions?',
        '''Use the official app as a companion to the calculation: choose a quantity
        in Python, open its matching Pulse selection, and compare the displayed metadata.
        Our source files are archived on 20 November 2026; the official app keeps evolving.
        Share-link parameters were checked against the published Pulse application on
        that date. If a future version changes them, choose the same settings manually
        and copy the app's own Share link.

        “Global” air temperature covers land and ocean at all latitudes, whereas this
        global SST export covers ocean points from 60°S to 60°N. Different domains and
        variables mean the series should not be subtracted as though they were repeated
        measurements of the same quantity. Both anomalies below use 1991–2020.

        Build complete annual summaries by weighting monthly means by days per month.
        Omit incomplete years explicitly. This is our stated aggregation of the supplied
        monthly product, not a claim to reproduce every detail of the official annual view.
        A single annual anomaly is also different from a sustained long-term warming level.
        Consult the trend monitor's method before comparing its 1.5 °C context.''',
        [('Open two complementary official views', '''air = load_pulse("global", variable="t2m")
ocean = load_pulse("60S-60N_ocean")
display(pd.DataFrame([
    {"series":"Global 2 m air", "start":str(air.date.min().date()), "end":str(air.date.max().date()), "domain":"All latitudes, land + ocean"},
    {"series":"Global SST", "start":str(ocean.date.min().date()), "end":str(ocean.date.max().date()), "domain":"Ocean, 60°S–60°N"},
]))
air_url = pulse_link(variable="t2m", region="global", quantity="anomaly", date="2024-01-01", aggregation="annual")
sst_url = pulse_link(region="global", quantity="anomaly", date="2024-01-01", aggregation="annual")
display(Markdown(f"[Official Pulse: global air, 2024 annual anomaly]({air_url}) · [Official Pulse: global SST, 2024 annual anomaly]({sst_url})"))
'''), ('Compare complete years with visible spatial domains', '''annual_air = complete_years(air, ANOM)
annual_ocean = complete_years(ocean, ANOM)
fig, axes = plt.subplots(2,1,figsize=(11,6),sharex=True)
for ax, annual, label, colour in [(axes[0],annual_air,"Global air · all latitudes","#a64825"), (axes[1],annual_ocean,"SST · ocean 60°S–60°N","#087e8b")]:
    ax.plot(annual.year, annual.value, color=colour)
    ax.axhline(0,color="gray",lw=1)
    ax.set(title=label, ylabel="Anomaly (°C; 1991–2020)")
axes[1].set_xlabel("Complete calendar year · derived day-weighted monthly mean")
plt.tight_layout(); plt.show()
display(annual_air.tail().rename(columns={"value":"global_air_anomaly_c"}))
print("Incomplete 2026 is excluded from these annual curves.")
'''), ('Separate annual monitoring from a long-term indicator', '''ranked = annual_air.assign(rank=annual_air.value.rank(method="min",ascending=False).astype(int))
year = 2024
row = ranked.loc[ranked.year == year].iloc[0]
card = {"year":year,"derived_annual_anomaly_c":round(float(row.value),4),
        "rank_among_complete_years":int(row["rank"]),"number_of_years":len(ranked),
        "baseline":"1991–2020","method":"Day-weight supplied monthly anomalies; complete years only",
        "scope":"Global 2 m air; descriptive archive rank",
        "not_inferred":"Date of sustained 1.5 °C warming; attribution of any local event"}
display(pd.Series(card).to_frame("Monitoring card"))
catalogue = apps_catalogue()
monitor = next(app for app in catalogue["entries"] if app["id"] == "global-temperature-trend-monitor")
display(Markdown(f"[Compare with the official global temperature trend monitor]({monitor['url']})"))
''')],
        'Choose a different complete year, open its official annual view, and record any difference in rounding or aggregation. Then compare the reference period and method used by the trend monitor.',
        'A fair comparison needs the same variable, spatial support, reference period, averaging rule, and archive version. An annual anomaly alone does not establish a sustained global warming level.',
        'In Pulse, switch between daily, monthly, and annual views. In the trend monitor, read its method before comparing the numerical indicator. Keep both source links with your evidence card.',
        'Real archived C3S/ECMWF ERA5 global air and ocean monthly CSVs; derived annual summaries',
        [('ERA5 monthly dataset','https://doi.org/10.24381/cds.f17050d7'),('Pulse methodology',PULSE+'faqs'),('Global temperature trend monitor overview',CATALOGUE+'overview?app=global-temperature-trend-monitor')])

    add('31-pulse-download-roundtrip','Download, import, and audit a Pulse export',
        'Has a newer export added months, revised history, or changed its meaning?',
        '''A live view is useful for exploration; a retained CSV is useful for reproduction.
        Open the official Niño 3.4 monthly view, select the CSV download control, and keep
        the whole file including its metadata header. In JupyterLite, create `uploads/`
        and upload the CSV as `pulse_export.csv`. Set `USE_UPLOADED_EXPORT = True`
        below only after checking the source. A missing or incompatible file stops with an
        explicit error; it is never silently relabelled as real data.

        **Browser download path:** the public CSV endpoint returned no cross-origin
        permission header when checked on 20 November 2026. Therefore this lesson uses
        normal browser download followed by Lab upload, rather than promising an automatic
        Pyodide fetch. Opening the CSV URL directly in a new tab is another download route.
        No proxy, token, or security-setting change is needed.

        The default example reads the bundled original export and audits it against itself:
        zero revisions are expected. After you explicitly select a new export, an outer date
        join distinguishes newly added months, removed months, and revisions to existing
        numbers. A changed value is not necessarily a data error: examine source processing,
        metadata, revisions, and rounding before interpreting the difference.''',
        [('Choose the source explicitly and retain the header', '''import hashlib
snapshot_path = DATA / "pulse/timeseries_era5_sst_monthly_nino34.csv"
snapshot_bytes = snapshot_path.read_bytes()
USE_UPLOADED_EXPORT = False  # Change only after downloading and uploading an official export.
chosen_path = Path("uploads/pulse_export.csv") if USE_UPLOADED_EXPORT else snapshot_path
raw = chosen_path.read_bytes()  # Missing uploaded files fail here, without fallback.
current, header = read_pulse_monthly_csv(raw)
baseline, baseline_header = read_pulse_monthly_csv(snapshot_bytes)
mode = "USER-UPLOADED EXPORT — review metadata" if USE_UPLOADED_EXPORT else "BUNDLED SNAPSHOT SELF-CHECK"
print(mode, "\\nPath:", chosen_path, "\\nSHA-256:", hashlib.sha256(raw).hexdigest())
print(header)
manifest = json.loads((DATA/"pulse/manifest.json").read_text(encoding="utf-8"))
source_url = next(r["url"] for r in manifest if r["file"].endswith(snapshot_path.name))
display(Markdown(f"[Open official monthly Niño 3.4]({pulse_link()}) · [Open the public source CSV]({source_url})"))
'''), ('Distinguish additions from revisions', '''audit = compare_pulse_exports(baseline, current)
counts = audit.status.value_counts().reindex(["unchanged","revised","new","removed"],fill_value=0)
display(counts.to_frame("Months"))
fig, ax = plt.subplots(figsize=(8,3.5))
ax.bar(counts.index,counts.values,color=["#637b91","#b95721","#087e8b","#80577f"])
ax.set(ylabel="Months",title=mode+" · source comparison"); plt.show()
display(audit[audit.status != "unchanged"].head(20))
if not USE_UPLOADED_EXPORT:
    assert counts["unchanged"] == len(baseline) and counts.drop("unchanged").sum() == 0
'''), ('Save a provenance sidecar without changing the source', '''from datetime import datetime, timezone
out = Path("exports"); out.mkdir(exist_ok=True)
evidence = {"mode":mode,"input_file":str(chosen_path),"sha256":hashlib.sha256(raw).hexdigest(),
    "audited_utc":datetime.now(timezone.utc).isoformat(),
    "official_source_url":source_url,"source_verified_by_learner":False,
    "retrieval_time_for_uploaded_file":"Record the actual download time; this audit time is not a retrieval time",
    "rows":len(current),"first_month":str(current.date.min().date()),"last_month":str(current.date.max().date()),
    "baseline":"1991–2020","units":"degC","licence":"CC-BY-4.0 per validated source header",
    "credit":"C3S / ECMWF / European Union; ERA5 teams",
    "transformation":"Parse original CSV; outer join by month; classify changes; raw bytes retained"}
(out/"pulse-import-audit.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print("Download exports/pulse-import-audit.json together with your original CSV and notebook.")
''')],
        'Download a fresh export, upload it, enable the explicit import switch, and rerun. Report its actual retrieval time and whether any common months changed. If none changed, say so.',
        'A new date is not a revision to an old date. The default self-check demonstrates the workflow but is not evidence that a live export was fetched.',
        'Use Pulse’s own export controls and retain the selected variable, region, aggregation, baseline, and app share URL. Check its credits before publishing a derived chart.',
        'Real bundled Niño 3.4 CSV self-check by default; explicit optional learner-uploaded official monthly export',
        [('Pulse source/data credits',PULSE+'credits'),('ERA5 monthly source','https://doi.org/10.24381/cds.f17050d7')])

    add('32-copernicus-apps-workshop','A field guide to the Copernicus apps',
        'Which app supplies the evidence your question actually needs?',
        '''The Copernicus applications catalogue brings together tools from C3S, CAMS,
        and the wider Data Stores ecosystem. Our dated index contains the **11 entries
        observed on 20 November 2026**. It is an original teaching guide with factual
        names, launch links, programme labels, and source dataset identifiers; it does not
        bundle external app data or copy their screenshots and descriptions.

        Use the links to try three investigations. **Heat and weather:** follow one event
        in Weather Replay, inspect local historical context in ERA Explorer, and examine
        the thermal-stress quantity in Thermal Trace. **Smoke:** separate fire emissions
        in Fire Emissions Watch from aerosol forecast information in Aerosol Alerts.
        **Regional climate:** compare indicator definitions in Climate Atlas and the European
        Climate Data Explorer; inspect NECD Explorer's country/season threshold separately.
        Methane Hotspot Explorer provides another exercise in distinguishing a remotely
        observed signal from a claim about its source.

        These are questions to investigate, not claims that the apps share an API, units,
        spatial support, or download licence. Record the exact selections and read each
        app's credits and linked dataset terms. Missing source IDs in our catalogue mean
        the entry did not list them, not that the app has no source data. No legal, health,
        attribution, or operational warning decision is made by this teaching exercise.''',
        [('Find apps by the evidence question', '''catalogue = apps_catalogue()
apps = pd.DataFrame(catalogue["entries"])
display(apps[["name","programme","data_type","topic"]])
for app in catalogue["entries"]:
    display(Markdown(f"**[{app['name']}]({app['url']})** · [official overview]({app['overview']})\\n\\nTry: {app['exercise']}\\n\\nCheck: {app['limitation']}"))
'''), ('Visualise the catalogue without inventing climate measurements', '''types = ["Reanalysis","Observations","Projections","Forecast"]
matrix = np.array([[int(kind.lower() in row.data_type.lower()) for kind in types] for row in apps.itertuples()])
fig, ax = plt.subplots(figsize=(9,6))
ax.imshow(matrix,cmap="Blues",vmin=0,vmax=1,aspect="auto")
ax.set(xticks=range(len(types)),xticklabels=types,yticks=range(len(apps)),yticklabels=apps.name,
       title="Evidence types listed by the catalogue · not app ratings")
for i in range(len(apps)):
    for j in range(len(types)):
        ax.text(j,i,"Listed" if matrix[i,j] else "—",ha="center",va="center",color="white" if matrix[i,j] else "#12334b",fontsize=8)
plt.tight_layout(); plt.show()
print("Blank = not listed for that app in this dated catalogue; it does not prove absence of a capability.")
'''), ('Build a reusable cross-app evidence journal', '''case_ids = ["weather-replay","era-explorer","thermal-trace"]  # Choose another investigation.
records=[]
for app in catalogue["entries"]:
    if app["id"] in case_ids:
        records.append({"app":app["name"],"url":app["url"],"task":app["exercise"],
          "review_status":"not yet inspected by learner","location":None,"selected_time":None,
          "forecast_issue_time_if_applicable":None,"variable_and_units":None,"spatial_support":None,
          "reference_period":None,"displayed_value":None,"dataset_version_and_licence":None,
          "share_url":None,"interpretation_limit":app["limitation"]})
display(pd.DataFrame(records)[["app","review_status","location","selected_time","displayed_value"]])
out=Path("exports"); out.mkdir(exist_ok=True)
(out/"copernicus-app-evidence-journal.json").write_text(json.dumps(records,indent=2),encoding="utf-8")
print("Fill the null fields only with inspected evidence. A blank is not zero and not a completed observation.")
''')],
        'Complete one investigation with two or three apps. Fill the evidence journal, then explain which quantities can be compared directly and which need different spatial or temporal support.',
        'A matching location and date are necessary but not sufficient. Compare quantity, units, forecast issue/valid time, averaging support, baseline, dataset/version, and licence before joining numbers.',
        'Open the official catalogue to discover additions since this snapshot. Use the app overview and About panels to find datasets, tutorials, credits, and limitations; export only where the app supports it.',
        'Sourced factual app catalogue with original teaching annotations; empty learner evidence template; no fabricated app measurements',
        [('Catalogue team and scope',CATALOGUE+'about'),
         ('Weather Replay introduction and video','https://climate.copernicus.eu/weather-replay-your-time-machine-revisit-past-weather'),
         ('ERA Explorer official training notebooks','https://apps.copernicus-climate.eu/c3s-apps/era-explorer/notebooks/intro.html'),
         ('NECD Explorer methods','https://apps.copernicus-climate.eu/nec-explorer/')])
