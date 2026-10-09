# Dashboard specification and build guide

Canvas **1280 × 720** (16:9) on every page. Theme: `theme/phc_health_analytics_theme.json` (View › Themes › Browse for themes). Positions are given as **x, y, w, h** in pixels (Format › General › Properties). Every measure named below exists in `dax/measures.dax`.

## Shared page frame (all five analysis pages)

| Element | Position | Content |
|---|---|---|
| Header band (rectangle, fill `#13315C`) | 0, 0, 1280, 56 | Text box: page title in white, Segoe UI Semibold 18. Subtitle in `#D6E2EE`, 10 pt: "Primary Healthcare Performance & Service Delivery Analytics · anonymized programme data, Jan–Sep 2026". |
| Navigation buttons (6 × blank buttons, action = Page navigation) | 760, 14, 80 each, 28 | Overview · MNCH · Immunization & FP · Malaria · Data quality · Reset. The current page's button is filled `#0E7C86`, the others `#1D4E89`. |
| Slicer panel | 0, 56, 1280, 52 | Four dropdown slicers, 240 × 44 each, at x = 16, 266, 516, 766: **Month** (`DimDate[Month Short]`, filtered to `Is Programme Month = 1`, multi-select), **Quarter** (`DimDate[Quarter Label]`), **Adopter** (`DimAdopter[Adopter]`), **Zone** (`DimGeography[Zone]`). Page 1 also has **Service category** (`DimIndicator[ServiceCategory]`) at x = 1016. Sync the four common slicers across all pages (View › Sync slicers). |
| Footer note (text box) | 16, 696, 1248, 20 | 8 pt `#52606D`: "Counts are service contacts, not unique individuals. Missing reports are not counted as zero. No targets are defined. Facility and adopter names are pseudonymised." |

**Reset workflow:** create a bookmark "Reset filters" with *Data* checked, captured with all slicers cleared, and assign it to the Reset button. Alternatively, users can press **Ctrl+Shift+click** on a slicer's eraser icon.

---

## Page 1 – Executive Performance Overview

| # | Visual | Position | Fields / measures | Format |
|---|---|---|---|---|
| 1 | Card row (8 × *Card (new)* or separate cards) | y 116, h 92; x = 16 + 156·i, w 148 | General Attendance · OPD Visits · ANC Visits · Skilled Birth Deliveries · Immunization Doses <1 Year · FP Acceptors · Reports Received · Reporting Completeness % | Callout 24 pt `#13315C`; category label 9 pt. Reference label (new card): `[General Attendance QoQ %]` etc. where available. The doses card's subtitle must say "doses, not children". |
| 2 | Line + clustered column chart "Monthly service delivery trend" | 16, 216, 760, 236 | X: `DimDate[Month Short]`. Columns: General Attendance, OPD Visits. Line (secondary axis): Reporting Completeness %. | Axis titles "Service contacts" / "Reporting completeness". Data labels off; tooltips on. Subtitle: "June peak coincides with an immunization outreach campaign; September partially reported." |
| 3 | 100% stacked bar "Service delivery composition" | 784, 216, 480, 236 | Y: `DimIndicator[ServiceCategory]` (exclude Service utilisation and Mortality via visual filter). Values: Service Value. | Shows the composition of recorded contacts by category; values are counts of different units, so the title says "share of recorded service events". |
| 4 | Clustered bar "Zone comparison" | 16, 460, 400, 228 | Y: `DimGeography[Zone]`. X: General Attendance per Report. Tooltip: General Attendance, Reports Received, Reporting Completeness %. | Uses the per-report value so zones with weaker reporting aren't penalised. The note says the "Not disclosed" bar groups 2 small-cell facilities. |
| 5 | Matrix "Reporting performance summary" | 424, 460, 352, 228 | Rows: `DimAdopter[Adopter]`. Values: Expected Reports, Reports Received, Reporting Completeness %. | Conditional formatting: data bar on Reporting Completeness %, single hue `#0E7C86`. No red/green thresholds. |
| 6 | Text (Card (new) with measure, or Smart narrative replaced by measure) "Executive summary" | 784, 460, 480, 228 | `[Executive Narrative]` | 11 pt, wrap. Updates with every slicer. Add a static "Validated observations (Jan–Sep 2026)" text box below it if space allows (see the list at the end). |

## Page 2 – Maternal, Newborn and Child Health

| # | Visual | Position | Fields / measures | Notes |
|---|---|---|---|---|
| 1 | Cards (5) | y 116, h 84; x = 16 + 252·i, w 244 | ANC Visits · ANC First Visits · ANC Fourth Visits · Skilled Birth Deliveries · IPTp Dose 1 | – |
| 2 | Bar chart "ANC and IPTp contacts in the period" | 16, 208, 400, 260 | Create a field parameter (Modeling › New parameter › Fields) named *ANC & IPTp contacts* containing ANC First Visits, ANC Fourth Visits, ANC Eighth Visits, IPTp Dose 1, IPTp Dose 2, IPTp Dose 3. Use it as the Y axis; X = the parameter values. | Subtitle: "Same-period contacts – not a cohort; continuation ratios are cross-sectional." |
| 3 | Line chart "Monthly maternal health trend" | 424, 208, 840, 260 | X: Month Short. Lines: ANC First Visits, ANC Fourth Visits, Skilled Birth Deliveries, IPTp Dose 1 | Markers on; legend at the top. |
| 4 | Clustered column "Continuation ratios by quarter" | 16, 476, 620, 212 | X: Quarter Label. Values: ANC4 to ANC1 Ratio %, ANC8 to ANC1 Ratio %, IPTp3 to IPTp1 Ratio % | Title includes "(cross-sectional)". Data labels 0.0%. |
| 5 | Table "Recorded deaths – national" | 644, 476, 620, 212 | Rows: Month Short. Values: Neonatal Deaths, Infant Deaths, Under-5 Deaths, Maternal Deaths, Deaths per 100 Reports | Blank under adopter/zone filters (by design; caption explains). Totals row on. Small counts: no facility drill. |

## Page 3 – Immunization and Family Planning

| # | Visual | Position | Fields / measures | Notes |
|---|---|---|---|---|
| 1 | Cards (5) | y 116, h 84 | Immunization Doses <1 Year · Children 0-9m Fully Immunized · FP Clients Counselled · FP Acceptors · FP Acceptors per Client Counselled % | Doses card subtitle: "antigen doses, not children". |
| 2 | Column chart "Monthly immunization doses" | 16, 208, 620, 240 | X: Month Short. Y: Immunization Doses <1 Year. Tooltip: Immunization Doses <1 Year MoM % | Annotate June: "outreach campaign". |
| 3 | Line + column "FP counselling and uptake" | 644, 208, 620, 240 | Columns: FP Clients Counselled, FP Acceptors. Line: FP Acceptors per Client Counselled % | Subtitle: "service uptake among counselled clients – not contraceptive prevalence". |
| 4 | Stacked column "FP method acceptances (Jun–Sep)" | 16, 456, 620, 232 | X: Month Short (visual filter: Month Number ≥ 6). Legend: method measures (six FP … Acceptances) | Note: "fields added to the form in June; a client may accept more than one method". |
| 5 | Clustered bar "Period comparison by adopter" | 644, 456, 620, 232 | Y: Adopter. X: FP Acceptors, Immunization Doses <1 Year (small multiples by Quarter Label) | Pair with tooltip page T1. |

## Page 4 – Malaria and Other Priority Services

| # | Visual | Position | Fields / measures | Notes |
|---|---|---|---|---|
| 1 | Cards (6) | y 116, h 84 | Malaria Tests (All Ages) · U5 Malaria Tests · Adult Malaria Tests · Malaria Test Positivity % (All Ages) · U5 Treated per Positive % · Community Outreaches | – |
| 2 | Clustered column "Tests vs positive results" | 16, 208, 620, 240 | X: Month Short. Columns: U5 Malaria Tests, U5 Malaria Positive, Adult Malaria Tests, Adult Malaria Positive | Counts only, on one axis. |
| 3 | Line "Test positivity rate" | 644, 208, 620, 240 | X: Month Short. Lines: U5 Malaria Test Positivity %, Adult Malaria Test Positivity % | Y axis starts at 0%. Subtitle: "share of tests positive – not prevalence". |
| 4 | Clustered column "Treated per confirmed positive" | 16, 456, 620, 232 | X: Quarter Label. Values: U5 Treated per Positive %, Adult Treated per Positive % | Constant line at 100% labelled "treated = positive" (a reference, not a target). Subtitle: "values >100% indicate treatments recorded without a matching positive test – see Data quality". |
| 5 | Table "Malaria data-quality exceptions" | 644, 456, 620, 232 | Rows: `FactDataQuality[Check]` (visual filter: CheckCode in DQ01–DQ04). Values: Data Quality Exceptions | Drill-through enabled. |

## Page 5 – Programme Performance and Data Quality

| # | Visual | Position | Fields / measures | Notes |
|---|---|---|---|---|
| 1 | Cards (5) | y 116, h 84 | Expected Reports · Reports Received · Reporting Completeness % · Indicator Value Completeness % · Facility-Months with Logical Inconsistencies | – |
| 2 | Line + column "Expected vs submitted reports" | 16, 208, 620, 240 | Columns: Expected Reports, Reports Received. Line: Reporting Completeness % | Subtitle: "reporting completeness ≠ service coverage". |
| 3 | Matrix heat map "Facility-month reporting coverage" | 644, 208, 620, 240 | Rows: Adopter › Facility (drill). Columns: Month Short. Values: Reports Received | Background colour scale `#F4F7FA` → `#0E7C86` (0 → 1). Facility rows show pseudonyms only. |
| 4 | Bar "Data-quality exception summary" | 16, 456, 400, 232 | Y: `FactDataQuality[Check]`. X: Data Quality Exceptions | Sorted descending. |
| 5 | Table "Key indicator register" | 424, 456, 840, 232 | Rows: `DimIndicator[Indicator]`, `[Unit]`. Values: Service Value, Values Recorded, Indicator Value Completeness %, Selected Period Label | Conditional icon (shape, not colour alone) where completeness < 100%. |

## Drill-through page D1 – Facility detail (hidden from navigation)

- Drill-through field: `DimFacility[Facility]`. Keep all filters on. Add a back button.
- Visuals: cards (Reports Received, Reporting Completeness %, General Attendance, ANC Visits, Malaria Tests (All Ages)); a line of General Attendance by month; a table of `FactDataQuality` Check × Month; a matrix of `FactFacilityReporting[ReportingStatus]` by month.
- **Privacy:** no mortality visuals on this page (the measures return blank anyway). Only pseudonyms are shown.

## Tooltip page T1 – Period detail (Page information › Allow use as tooltip, 320 × 200)

- Cards: Selected Period Label, General Attendance, Reports Received, Reporting Completeness %, General Attendance per Report.
- Assign it to the trend and comparison visuals (Format › Tooltip › Report page = T1).

## Interactions

- Cross-filtering is left at the default (filter) between visuals on each page. Set the **Edit interactions** of slicers so the composition chart (P1-3) is not filtered by the Service category slicer: it shows all categories.
- Every page works with no selections (defaults to Jan–Sep 2026, all adopters, all zones).

## Validated observations (Jan–Sep 2026 – use as static text, update if the data change)

1. **Reporting declined steadily**, from 100% in January to 90% in August and 71.7% in September (September was incomplete at extraction). Quarterly completeness: 97.2% → 92.8% → 84.4%.
2. **Adopter B (5 facilities)** reported for 28.9% of expected facility-months; none of its facilities reported from June. Its low totals reflect missing reports, not confirmed absence of services.
3. **General attendance** was 377,483 contacts (Q1 116,771; Q2 136,126; Q3 124,586; Q3 vs Q2 −8.5%). Per report received, attendance *rose* (667 → 815 → 820), so the Q3 fall is largely a reporting effect.
4. **June peak**: immunization doses (31,477) were about double the other months' level (13,400–16,700), coinciding with an outreach campaign; Q2 is an inflated comparator.
5. **Malaria test positivity** was high and rose in Q3: under-5 64.4% → 62.0% → 72.3%; adult 63.8% → 61.8% → 66.6%. Treated-per-positive ratios are around 99–101%, with 27 facility-months recording more treatments than positives.
6. **ANC4-to-ANC1 ratio** (cross-sectional) increased from 52.3% in Q1 to 69.9% in Q3. IPTp3-to-IPTp1 stayed near 56–59%. These ratios point to continuation patterns worth investigating, not to completion rates.
7. **FP conversion** (acceptors per client counselled) fell from 58.0% in Q1 to about 51% in Q2–Q3.
8. **Data quality:** 315 exceptions were logged. 43 are logical inconsistencies across 36 facility-months, and 132 are FP method totals above acceptors (expected with multi-method counting).

## Build checklist (Power BI Desktop)

1. Create the `DataFolder` parameter, then paste each query from `powerquery/` (see `powerquery/ALL_QUERIES.md`). Close & Apply.
2. Model view: create the relationships in `docs/DATA_MODEL.md`. Mark `DimDate` as date table. Set sort-by columns. Hide keys.
3. Create the `Measures` table, then load `dax/measures.dax`, either with Tabular Editor 3 (*File › Open › DAX script*, then *Apply*) or by pasting each measure.
4. Import the theme. Build the pages above.
5. Run `validation/dax_validation_queries.dax` in DAX Studio and compare with `validation/reference_values.csv` (tolerance: rounding only).
6. Test the slicers with the scenarios in `validation/VALIDATION_REPORT.md` §3, then capture screenshots (File › Export › PDF, or Windows Snipping Tool at 100% zoom) into `screenshots/`.
7. Before sharing: File › Options › Current file › Privacy, and check that no "Show data" export or *See records* exposes anything other than pseudonyms (the data contain none).
