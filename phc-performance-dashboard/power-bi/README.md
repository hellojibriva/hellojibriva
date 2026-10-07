# PHC Performance Dashboard: Power BI

A five-page Power BI report with its data model, saved as a Power BI Project (`.pbip`). The de-identified data is built into the model, so there are no file paths or data connections to set up.

## Open it

1. Download this `power-bi` folder (or `PHC_Performance_Dashboard_PowerBI.zip` from the project folder) and unzip it.
2. In **Power BI Desktop**, choose **File > Open report > Browse reports**, then open `PHC_Performance_Dashboard.pbip`.
3. Select **Refresh** on the Home ribbon to load the data (a few seconds).
4. To get a single `.pbix` file, choose **File > Save as** and pick the *Power BI file (.pbix)* type.

Requires Power BI Desktop from September 2025 or later. If an older version refuses to open the project, update Desktop, or turn on **File > Options and settings > Options > Preview features > "Power BI Project (.pbip) save option"**, **"Store semantic model using TMDL format"** and **"Store reports using enhanced metadata format (PBIR)"**, then restart Desktop.

## Pages

| Page | Contents |
|---|---|
| Overview | 8 KPI cards, monthly attendance, immunisation doses (June immunisation outreach), facilities reporting, community outreaches, and a headline that rewrites itself for the current filters |
| Maternal & malaria | ANC1→4→8 and IPT1→2→3 cascades, malaria tested → positive → treated for children and adults, positivity and retention trends |
| Zones & facilities | Zone performance table, facility table sorted by lowest ANC4 retention, ANC4 retention by zone |
| FP, mortality & barriers | Family planning method mix, deaths by category, challenge themes facilities report |
| Data quality | Facility × month report status matrix (✓ received, ⚠ flagged, ✗ missing), reports failing each check, completeness by month |

Month, Zone and Partner slicers sit on every page and stay in sync.

## Data model

A star schema with one fact table and conformed dimensions:

- **Reports**: 449 facility-month reports with 31 indicators and 8 data-quality flags. It also holds all 55 measures, grouped into display folders: Coverage, Service volume, Antenatal care, Malaria, Family planning, Mortality, Barriers and Data quality.
- **Facility** (60 rows) and **Month** (8 rows): dimensions. June carries the *Immunisation outreach* programme event.
- **Challenge Themes**: one row per theme mentioned in a report, related to Facility and Month.
- **Helper tables**: ANC Step, IPTp Step, Malaria Step, FP Method, Death Category and DQ Check. These small tables give cascade and breakdown charts a sorted axis, while SWITCH measures return the matching value.

Every rate is a ratio of sums, for example `ANC4 Retention = DIVIDE([ANC4], [ANC1])`. Reporting completeness compares reports received with *facilities in the selection × months in the selection*. June volumes are excluded from the spike checks because they reflect the immunisation outreach.

## Rebuild

The project is generated from the de-identified CSV:

```bash
python ../scripts/build_dataset.py path/to/source.xlsx   # only if the source data changes
python ../scripts/build_powerbi.py
```

The generated files were checked before publishing:

- The semantic model loads in Microsoft's Tabular Object Model (`TmdlSerializer`), and every DAX column and measure reference resolves.
- Every report file validates against Microsoft's published PBIR JSON schemas, and the theme validates against the Power BI report theme schema.
- Every field a visual uses exists in the model.
