# WAHIS Nigeria zoonoses — One Health surveillance analysis

Reproducible descriptive analysis of reported rabies, high-pathogenicity avian
influenza (HPAI) and tsetse-transmitted trypanosomosis in Nigeria, 2006–2023,
using the WOAH WAHIS quantitative extract.

**Current status: data audit complete, awaiting approval. No manuscript written.**

Start with **[`reports/DATA_AUDIT_REPORT.md`](reports/DATA_AUDIT_REPORT.md)**.

## Headline findings from the audit

* **The file is not one row per outbreak.** It has a block structure —
  *Year × Semester × Administrative Division × Disease × Serotype* — where one
  header row (blank `Species`) carries `New outbreaks` and one or more detail
  rows carry the animal counts. Row type must be identified by the blank
  `Species` field; the `Animal Category` label changed in 2020 and would drop
  95 outbreak records if used instead.
* **`-` is not `0`.** `New outbreaks` contains no zeros anywhere in the file,
  while other count columns carry `0` and `-` side by side. `-` is parsed to
  missing and never imputed.
* **The main hazard is zero-fabrication, not double-counting.** Summing
  `New outbreaks` over every row gives the same answer as summing over header
  rows only, because detail rows are missing there.
* **Trypanosomosis cannot span 2006–2023.** The WAHIS label is
  `Trypanosomosis (tsetse-transmitted) (-2021)`; reporting stops after 2021 at
  the series maximum. This is a classification change, not a disease decline,
  and it requires a decision on study framing — see §15.1 of the report.

## Layout

```
data/raw/         WOAH WAHIS extract — read-only, never modified
data/processed/   derived datasets + transformation log
scripts/          numbered, reproducible pipeline
outputs/          tables, figures (PNG + PDF), full run logs
reports/          the data audit report
```

## Reproducing

```bash
pip install pandas numpy matplotlib
python3 scripts/01_audit.py        # Phases 1–4: audit
python3 scripts/02_build_clean.py  # Phase 5:   clean datasets
python3 scripts/03_descriptive.py  # Phases 6–9: descriptive analysis
python3 scripts/04_figures.py      # Phase 10:  draft figures
```

Console output for each stage is committed under `outputs/logs/`.

## Scope

Descriptive surveillance epidemiology only. The analysis reports **what was
reported to WAHIS**. It does not estimate incidence or prevalence, does not
compute rates, does not model risk, and cannot support any statement about human
disease burden. See §14–15 of the audit report for the full limitations.
