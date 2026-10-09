# Primary Healthcare Performance & Service Delivery Analytics – Power BI

*Portfolio classification: anonymized health programme analytics demonstration using de-identified programme data.*

An executive Power BI dashboard design for a primary healthcare programme covering 60 facilities, 4 implementing partners and 6 geopolitical zones in Nigeria (January–September 2026). It turns routine monthly facility reports into insight on:
- service utilisation;
- maternal, newborn and child health;
- immunization and family planning;
- malaria testing and treatment;
- reporting completeness and data quality.

> **Status – read first.** Power BI Desktop was not available in the build environment (Linux). This folder is the **complete, validated build kit**: anonymized data, Power Query (M) scripts, a documented star-schema model, 84 DAX measures, a theme, and a page-by-page specification with exact layouts. The `.pbix` file and the screenshots are produced by following the build checklist in Power BI Desktop; they are **not** included yet, and nothing here claims they exist.

## What's in this folder

| Path | Contents |
|---|---|
| `data/` | Anonymized analysis-ready CSVs: 4 facts, 4 dimensions. No names, states, LGAs, wards or free text. |
| `powerquery/` | One M script per table, plus the `DataFolder` parameter and a calendar table (`ALL_QUERIES.md` has them all on one page). |
| `dax/measures.dax` | 84 explicit measures in display folders, with format strings and descriptions (Tabular Editor 3 DAX-script format, or copy/paste). |
| `dax/DAX_MEASURES.md` | Readable measure inventory. |
| `theme/` | Power BI report theme (navy/teal palette, accessible contrast). |
| `docs/DASHBOARD_SPEC.md` | 5 analysis pages + drill-through + tooltip page: every visual, field, position, interaction, and the build checklist. |
| `docs/DATA_MODEL.md` | Tables, grain, relationships (all 1:*, single direction), column settings. |
| `docs/DATA_DICTIONARY.md` | Every indicator: definition, numerator/denominator, unit, aggregation, limitations; plus what *cannot* be calculated. |
| `docs/DATA_PREPARATION.md` | Anonymization rules, missing-vs-zero treatment, 11 data-quality checks, limitations. |
| `docs/PROJECT_INVENTORY.md` | Phase-1 assessment of the files, structures and tooling available. |
| `validation/` | Validation report, automated check results, independent reference values for every measure, DAX Studio queries. |
| `scripts/` | Reproducible pipeline: prepare → build model assets → validate. Running the first and last needs the confidential source, which is not included. |
| `PROJECT_SUMMARY.md` | One-page summary for recruiters and clients. |

## Reproduce the dashboard in Power BI Desktop

1. Copy this folder locally. In Power BI Desktop create the parameter `DataFolder` = full path of `data\` (with the trailing backslash).
2. Add each query from `powerquery/` (Blank query › Advanced editor). Close & Apply.
3. Create the relationships listed in `docs/DATA_MODEL.md` and mark `DimDate` as the date table.
4. Create an empty `Measures` table and load `dax/measures.dax`, via Tabular Editor 3 or by pasting each measure.
5. Import `theme/phc_health_analytics_theme.json` and build the pages from `docs/DASHBOARD_SPEC.md`.
6. Validate: run `validation/dax_validation_queries.dax` in DAX Studio and compare with `validation/reference_values.csv`. Then work through the manual tests in `validation/VALIDATION_REPORT.md` §3.
7. Save as `PHC_Performance_Dashboard.pbix` and export screenshots to `screenshots/`.

## Methods in brief

- **Privacy by design.** Stable pseudonyms (`Facility 001`, `Adopter A`) from a seeded shuffle. Location detail and free text are dropped. A small cell is suppressed, mortality is published nationally only, and the identity mapping is kept outside the repository. An automated scan checks every file against all 208 source identifiers.
- **Missing ≠ zero.** Facility-months with no report, and form fields that didn't exist yet, are NULL. This replaces 2,592 source zeros, and no total changes.
- **Correct ratios.** Every rate is a ratio of sums using `DIVIDE()`, never an average of facility percentages.
- **Honest labelling.**
  - Contacts are not people.
  - The immunization field counts doses.
  - ANC4/ANC1 is a cross-sectional ratio, not completion.
  - Treated-per-positive can exceed 100% and is flagged.
- **Reconciliation.** 288 indicator × month totals and all Jan–Sep totals match the validated source exactly.

## Tools

Power BI (Power Query M, DAX, star-schema modelling, field parameters, drill-through, tooltip pages, bookmarks), Python/pandas (data preparation, anonymization, automated QA), Tabular Editor / DAX Studio (deployment and measure testing).
