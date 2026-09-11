# WAHIS Nigeria animal disease surveillance analysis, 2006–2025

Rebuild of the analytical dataset, tables, figures and QC outputs from the raw WAHIS
quantitative export. **The manuscript has not been rewritten** — this is the analytical
layer only, for review.

## Layout

```
analysis/
  data/     WAHIS_Quantitative_data_20260910_RAW.csv   (read-only source of truth, md5 d6ebeda4...)
  scripts/  01-05 audits · 10 main analysis · 11-15 discrepancy forensics · 20 figures
  outputs/  all tables, figure datasets, QC outputs, QGIS join files, workbook
  figures/  Figure_1..4 PNG (300 dpi)
  qc/       QC_Checks.csv, QC_Reconciliation.csv
```

Workbook: `outputs/animal_disease_RESULTS_2006_2025.xlsx` (also written to
`/mnt/data/animal_disease_RESULTS_2006_2025.xlsx`), 35 sheets.
`animal_disease_RESULTS_FINAL.xlsx` is not present in this repository and was not modified.

## Reproduce

```bash
pip install pandas numpy scipy matplotlib openpyxl
python3 analysis/scripts/10_main_analysis.py    # tables, QC, workbook
python3 analysis/scripts/20_figures.py          # figures
```

## Core rules

- **Missing ≠ zero.** A disease-year with no WAHIS row stays NA. `-` parses to NaN, never 0.
  Group sums use `min_count=1`. A reported 0 is a legitimate observed value and is kept as 0.
  No interpolation, no zero-filling, no imputation anywhere.
- **Aggregation.** Per disease-year, each metric is the straight SUM over all raw rows.
  No deduplication. Verified safe: outbreak-carrying rows and count-carrying rows are
  structurally disjoint, and the two outbreak-row labellings never co-occur for the same
  Year/Semester/Disease/Division (0 of 520 keys).
- **Reported, not true.** All figures are *reported* counts. Geography describes the
  geographic concentration of reported outbreaks, not incidence, prevalence or
  population-adjusted burden.

## Status

32 of 33 QC checks PASS. The single FAIL is deliberate and unresolved-by-design: the
previously published Spearman coefficients do not reproduce as labelled. Root cause
identified and documented in `QC_Spearman_Resolution` — see the audit report.
