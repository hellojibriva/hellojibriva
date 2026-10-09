# Phase 1 – Workspace inventory

Assessment date: 9 October 2026.

## Files and tooling found

| Item | Found | Notes |
|---|---|---|
| Source Excel workbook | 1 (programme Q3 2026 dashboard workbook, 16 sheets, ~1.7 MB) | Confidential; kept outside the repository and not published. |
| Derived Excel workbook | 1 (redesigned interactive version from an earlier task) | Contains real names, so it is **not** a portfolio input or output. |
| CSV files | none | – |
| Power BI files (`.pbix` / `.pbip`) | none | – |
| Power Query scripts / DAX / data model | none (the source dashboard is formula-based: SUMIFS over named ranges) | Rebuilt here as M + DAX. |
| Data dictionary | partial: the source "Methodology" sheet (indicator mapping, rules, standardisation maps) | Used as the authoritative definition source. |
| **Power BI Desktop** | **not available.** Linux container; no Power BI Desktop, Analysis Services or Windows runtime. | No `.pbix` could be created or opened. This deliverable is the complete build kit; see the README. |
| Other tools used | Python 3 (pandas), LibreOffice (cross-check only) | – |

## Source structure (relevant sheets)

| Sheet | Rows | Content |
|---|---|---|
| Clean_Data | 540 (60 facilities × 9 months) | Facility-month analysis layer: zone, state, LGA, ward, facility, adopter, reporting status, expected/reported flags, 32 indicators. |
| Trace_Long | 17,280 | Facility × month × indicator with value status (reported / zero / field blank / non-reporting / corrected) and backend traceability. |
| Monthly_Indicator_Table | 61 | Validated monthly, quarterly and Jan–Sep totals (used for reconciliation). |
| Methodology | 155 | Indicator definitions, rules, standardisation maps. |
| Other sheets | – | Presentation sheets (summaries, charts); not used as data inputs. |

## Dimensions available

| Dimension | Values | Used? |
|---|---|---|
| Month | January–September 2026 (single year) | Yes. No prior year, so no YoY. |
| Facility | 60 | Yes, pseudonymised. |
| Adopter (implementing partner) | 4 | Yes, pseudonymised. |
| Geopolitical zone | 6 | Yes; one small-cell group is suppressed. |
| State / LGA / ward | many | **No** (re-identification risk). |
| Reporting status | 5 source values | Yes, relabelled. |

## Indicators available

27 service indicators (attendance, ANC 1/4/8, IPTp 1–3, deliveries, immunization ×2, FP counselling/acceptors, 6 FP methods, malaria tests/positive/treated for under-5s and adults, outreaches) and 5 mortality fields. **Targets: none.** **Population denominators: none.** **Reporting timestamps: none**, so timeliness can't be measured.

## Key data-quality issues identified

See `DATA_PREPARATION.md` §4 for counts and treatment:
- September is partially reported.
- One adopter stopped reporting, and the source filled its months with zeros.
- FP method fields don't exist for January–May.
- Treated exceeds positive in 27 facility-months.
- ANC4 exceeds ANC1 in 92 facility-months (cross-sectional).
- FP method totals exceed acceptors in 132 facility-months.
- There is a June outreach spike.
- One value was corrected upstream.

The earlier `Data_QC` sheet referenced by the source is absent.
