# ADHFP Q3 2026 Dashboard – Redesign & Validation Summary

**Deliverable:** `ADHFP_2026_Q3_Dashboard_Interactive_Redesigned.xlsx` (the original workbook is unchanged; this is a separate file)
**Pivot sheet:** `Pivot_Explorer`, with 3 PivotTables and 6 slicers on Clean_Data (see section 0)
**Method:** I edited the workbook package directly instead of round-tripping it through a spreadsheet library. That way all 110 charts, comments, named ranges, filters and add-in parts are kept. Values were recalculated and checked in LibreOffice. Excel recalculates everything when the file is opened (`fullCalcOnLoad`).

## 0. Update – Excel repair prompt fixed; PivotTables and slicers added

**Repair prompt (cause and fix).** In the previous version, Clean_Data, Trace_Long and Lists each had **two** `<tabColor>` elements: they already had one, and I added a second. That breaks the worksheet schema, so Excel repaired those sheets when opening the file. Clean_Data and Lists feed every dashboard filter formula, which is why the filters came back as n/a. Each sheet now has exactly one tab colour.

To catch this kind of problem, every worksheet, the workbook, styles, all 112 charts, drawings and the pivot parts are now checked in two ways:
- against the ISO/IEC 29500 schemas, where the only remaining differences from the original are extension elements those schemas don't define;
- with a structural check for duplicate elements, row and cell order, overlapping merges or columns, style indexes and defined names. It finds 0 problems.

**New sheet: `Pivot_Explorer`** (second tab, linked from every navigation bar):

| Item | Detail |
|---|---|
| PivotTables (3) | All use one pivot cache on `Clean_Data!A1:AY541`, with 540 records. **PT_Month** is by month in calendar order. **PT_Zone** is by geopolitical zone. **PT_Facility** is by adopter, then facility, with adopters in the order MTN F, PSHAN, AIG F, HOW F. Each shows 8 summed measures plus a Grand Total. They refresh automatically when the file opens. |
| Slicers (6) | Quarter, Month, Geopolitical zone, Adopter, Facility and Reporting status. **Each slicer is connected to all three PivotTables.** |
| KPI tiles (6) | General attendance, Total ANC visits, Deliveries by SBA, Fully immunized <1 year, Facility reports received, and Reporting %. They read from the PivotTables through `GETPIVOTDATA`, so they follow the slicers. |
| Monthly table + 2 charts | A Jan–Sep table built with `GETPIVOTDATA`, plus two charts: General vs OPD attendance, and Reporting %. A month removed by the slicers shows as a gap, not a zero. |

**How it was built.** LibreOffice generated the pivot cache and records from Clean_Data. I wrote the PivotTable definitions in Excel's own layout, including row/column items, Grand Total and number formats. The slicer parts follow the Excel 2010+ slicer format. The main dashboard still uses its tested drop-down filters; the slicers drive the Pivot_Explorer sheet.

**Checks on the new sheet.** All 6 tiles and all 72 monthly-table cells equal independent pandas totals from Clean_Data (for example 377,483 general attendance, 494 of 540 reports = 91.5%). The PivotTable definitions pass the ISO schema. The 14,079-cell integrity check and the 9 dashboard filter scenarios were run again on this build, and all passed.

## 1. What was improved

| Area | Change |
|---|---|
| Visual identity | One palette across all sheets: deep navy, teal, green and restrained amber. Section bars are now underlined headings, borders are lighter, and table headers, total rows and notes look the same everywhere. |
| Category colours | These are the same in every chart. Adopters: MTN F navy, PSHAN teal, AIG F green, HOW F amber. Zones: NC navy, NE teal, NW green, SE purple, SS amber, SW terracotta. Quarters run from light (Q1) to dark (Q3). Rates (%) are always amber, and "Total" bars are slate. |
| Navigation | Every presentation sheet has the same tab bar in row 1, with the current sheet highlighted and "◀ Dashboard" to go back. Clean_Data and Trace_Long have a "◀ Back to Dashboard" link. The broken "QC" link to a non-existent `Data_QC` sheet was removed. |
| Main dashboard | Rebuilt as a clean grid with a title, subtitle and live selection line. Filters are in amber drop-downs with a status message. There are 4 KPI cards, 5 reporting-coverage cards, sections A–F, and an interpretation note. Panes are frozen below the filters, and the sheet is set up to print on landscape A4 pages. |
| Charts (110) | Consistent fonts and colours, lighter gridlines, and legends at the bottom that no longer overlap the plot. Rounded corners, inverted negative fills and per-point colour variation were removed. Charts are laid out on a 2-column grid with no overlaps. On September_2026, 2 charts used to cover the like-for-like table and are now below it. On Q3_By_Adopter, 16 charts used to overlap each other and are now on the grid. |
| Views and print | All sheets open at the top-left at 85% zoom. Presentation sheets are set to landscape and fit to page width. Tab colours separate presentation sheets from data sheets. |

## 2. Targets removed

- The **"Target achievement / Not set" KPI card** on the dashboard was removed.
- Stale text about target, achievement and gap columns was rewritten: Q3_2026_Summary A3 (it pointed to a "yellow target column H" that does not exist), Executive_Summary A25, and Methodology C137 and C146.
- No benchmarks or thresholds were added in their place.
- **Search result:** after editing, every cell, formula and chart title was searched for "target" and "achievement". Only two hits remain, and both are explicit disclaimers that *no programme targets are defined*: dashboard B157 and Methodology B137/C137.

## 3. Technical issues found and fixed

| # | Issue in the original | Fix |
|---|---|---|
| 1 | On the dashboard, the Apr–Sep half of the facility-trace and coverage tables (F:P) had been shifted 3 rows away from the Jan–Mar half. Four charts therefore plotted the wrong cells: the coverage chart plotted "OK" text, and the zone chart showed up to 500%. | Each table was rebuilt as one aligned block, and the charts were re-pointed to it. |
| 2 | The Jan–Sep coverage total `=SUM(C91:K91)` added counts and percentages together. It showed 87.9%; the correct figure is 494/540 = **91.5%**. The HOW F Jan–Sep totals pointed at the wrong rows (they showed 2.6 / 0 / 0). | The formulas were corrected. HOW F now shows 45 expected, 13 reporting and 32 non-responsive (28.9%). |
| 3 | The drill-down table showed only 4 rows. MTN F lost 2 of its 6 zones and HOW F lost 1 of its 5 facilities. | It now has 6 rows, and the total is unchanged. |
| 4 | The total row on the zone table was labelled " Total". | Relabelled "Nigeria total". |
| 5 | September_2026 T7:T54 was `IFERROR(#REF!-K7,"")`, a reconciliation against the deleted `Data_QC` sheet. | Replaced with "n/a" and a header that says why. |
| 6 | Chart "Deliveries and outreaches – Q1 vs Q2 vs Q3" plotted 12 indicators (rows 22–33). | Now plots Deliveries and Outreaches only, matching its title. |
| 7 | Seven "Attendance" charts plotted OPD on a separate secondary axis, so the two counts looked about the same size. | Both series are now clustered columns on one axis. Charts that mix counts with Reporting % keep their labelled secondary axis. |
| 8 | Count formulas on the dashboard returned **0** when every matching record was *not reported*. Charts also plotted blank rates as 0. | Counts now return blank, and chart helper rows turn blanks into #N/A so the charts show **gaps**. HOW F "recorded as 0" values stay 0, as the reporting rule requires. |
| 9 | Text referred to a `Data_QC` sheet that isn't in the workbook. | Reworded to "data-cleaning QC log". |

## 4. Interactivity (formula-driven, no macros)

- **Filters:** reporting period (month, quarter or Jan–Sep), **indicator category (new)**, indicator (46), geopolitical zone, adopter, and facility (the list follows the chosen adopter). A Reset switch returns everything to All.
- **What responds:** all KPI and coverage cards, the trend and quarter table, zone comparison, drill-down, facility trace, coverage tables and the 8 dashboard charts. Two tables are deliberately independent, and each says so in its heading: the zone table ignores the zone filter (it highlights the selected zone instead), and the HOW F table is not filtered.
- **Drill-down:** All → adopters; MTN F → zones; PSHAN, AIG F and HOW F → facilities. Choosing a facility gives a month-by-month trace of status, value and backend row. The tab links open the detailed sheets. Data sheets keep their AutoFilter and frozen headers.
- **Status message** explains empty results: reset active, indicator outside the chosen category, facility not run by the chosen adopter, facility not in the chosen zone, or no records.

## 5. Validation performed

| Test | Result |
|---|---|
| All **14,079** formula cells outside the dashboard, recalculated and compared with the original's cached values | All match except the 48 intended `#REF!` replacements |
| Formula text outside the dashboard | Unchanged except the same 48 cells |
| Source data (Clean_Data, Trace_Long) | Unchanged. The only addition is one back-link cell on each sheet. |
| Default dashboard view vs original | Matches. Q3 general attendance 124,586; Jan–Sep 377,483; Q2→Q3 −8.5%; monthly values identical; zones sum to the Nigeria total |
| **9 filter scenarios**, each checked against independent pandas calculations from Clean_Data (162 numeric checks) | **All passed** |
| ↳ September + ANC4 retention + South South (ratio) | Correct, displayed as % |
| ↳ HOW F + Omuanwa PHC, Q1 | Trace shows "Recorded as 0" status from February |
| ↳ MTN F, Q3 | Drill-down shows all 6 zones; total 15,991 |
| ↳ North Central + HOW F | No records: cards show "–", charts show gaps, status message explains why |
| ↳ PSHAN + Agwara PHC (MTN F facility) | Status warns that no records match |
| ↳ Reset = Yes | Everything returns to All / General attendance |
| ↳ Category mismatch | Warning shown |
| ↳ Deaths per 100 reports, Q2 | 19.2; change −1.4 per 100 |
| ↳ MPHC Okogbe (Aug–Sep missing) | Aug–Sep shown blank, not 0 |
| Formula errors | None, apart from the intended #N/A in the chart helper cells |
| Chart overlap and clipping | Rendered every sheet; no overlapping charts and no charts covering tables |

## 6. Limitations

1. **Slicers were not clicked in Excel.** LibreOffice cannot display slicers; it shows a placeholder box. I could not open the file in Microsoft Excel, so the slicer clicks themselves are untested. The PivotTables, GETPIVOTDATA links and totals were all verified. The main Interactive_Dashboard is still driven by its drop-downs, not by the slicers: rebuilding it on PivotTables would change the tested calculation logic.
2. **Testing was done in LibreOffice, not Microsoft Excel.** Excel recalculates everything on open and may ask to save when you close it. Please open the file once in Excel to confirm. The dependent drop-downs (Indicator by category, Facility by adopter) use `INDIRECT`, which is standard in Excel.
3. Changing the indicator category does not clear an indicator that is already selected. The status cell flags the mismatch instead.
4. Dashboard charts show rates multiplied by 100 so their labels read as percent. The axis title changes with the indicator type, and the tables keep the true values.
5. The drill-down chart always has 6 slots. With fewer entities (e.g. 4 adopters), the extra slots are empty.
6. Executive_Summary narrative text was not rewritten; only the target sentence was changed.
