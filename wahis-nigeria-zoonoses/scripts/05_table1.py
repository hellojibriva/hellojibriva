"""
TABLE 1 — Reporting profile of the three zoonotic animal diseases,
Nigeria, WOAH WAHIS, 2006-2023.

Reads ONLY the cleaned analysis datasets produced by 02_build_clean.py:
    data/processed/analysis_outbreaks.csv     (one row per reporting-block header)
    data/processed/analysis_animal_counts.csv (one row per animal-category x species)

Writes outputs/tables/table1_disease_profile.{csv,md}. Nothing else is modified;
the raw extract and the audit outputs are not touched.

Conventions carried over from the audit (see reports/DATA_AUDIT_REPORT.md):
  * '-' was parsed to NaN upstream and is NEVER treated as zero here. Counts are
    summed with min_count=1 so an all-missing group stays missing, and every
    animal-count row reports how many records were actually populated.
  * A disease-year with no reporting block is NOT a reported zero. Such years are
    listed explicitly and excluded from the median/IQR of annual counts.
  * Outbreak totals are national in scope (ADM1 + the national 'Nigeria' records)
    so that they reconcile with the annual series in t02. The count of reporting
    states is computed from ADM1 records only, since national records cannot be
    assigned to a state.
  * Animal-level totals are reported PER DISEASE and must never be compared
    across the three columns (different hosts, sectors and detection pathways).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wahis_common as W  # noqa: E402

STUDY_YEARS = list(range(W.STUDY_START, W.STUDY_END + 1))
N_ADM1 = len(W.NIGERIA_ADM1)

ANIMAL_ROWS = [
    ("susceptible", "Susceptible animals"),
    ("cases", "Cases"),
    ("deaths", "Deaths"),
    ("killed_disposed", "Killed and disposed of"),
    ("slaughtered", "Slaughtered"),
    ("vaccinated", "Vaccinated"),
]


def fmt_int(v: float) -> str:
    """Integer with thousands separators; missing stays visibly missing."""
    return "not reported" if pd.isna(v) else f"{int(round(v)):,}"


def fmt_years(years: list[int]) -> str:
    """Collapse a sorted year list into compact ranges: 2009-2013, 2016."""
    if not years:
        return "none"
    runs, start, prev = [], years[0], years[0]
    for y in years[1:] + [None]:
        if y == prev + 1:
            prev = y
            continue
        runs.append(str(start) if start == prev else f"{start}–{prev}")
        start = prev = y
    return ", ".join(runs)


def build_table1(ob: pd.DataFrame, an: pd.DataFrame) -> pd.DataFrame:
    """Assemble Table 1 as characteristic-rows x disease-columns."""
    table: dict[str, dict[str, str]] = {}

    for disease in W.DISEASE_ORDER:
        o = ob[ob["disease"] == disease]
        a = an[an["disease"] == disease]
        o_state = o[o["geo_level"] == "state"]

        # Annual series over reporting years only. reindex(STUDY_YEARS) makes a
        # year with no reporting block NaN, not 0 -- the distinction the whole
        # audit turns on.
        annual = o.groupby("year")["new_outbreaks"].sum().reindex(STUDY_YEARS)
        reported = annual.dropna()
        silent = [int(y) for y in STUDY_YEARS if pd.isna(annual[y])]
        q1, q3 = reported.quantile([0.25, 0.75])
        peak_year = int(reported.idxmax())

        col: dict[str, str] = {
            "WAHIS disease label":
                next(k for k, v in W.DISEASE_LABELS.items() if v == disease),
            "Observation window":
                f"{int(o['year'].min())}–{int(o['year'].max())}",
            "Years with a report, n/18":
                f"{reported.size}/{len(STUDY_YEARS)}",
            "Years with no report":
                fmt_years(silent),
            "Reporting semesters, n":
                f"{o['semester'].nunique()}",
            "Reporting blocks, n":
                f"{len(o):,}",
            "States/FCT reporting, n/37":
                f"{o_state['location_std'].nunique()}/{N_ADM1}",
            "Total reported new outbreaks":
                f"{int(o['new_outbreaks'].sum()):,}",
            "Annual reported outbreaks, median (IQR)":
                f"{reported.median():.0f} ({q1:.0f}–{q3:.0f})",
            "Peak reporting year (outbreaks)":
                f"{peak_year} ({int(annual[peak_year]):,})",
            "Animal-count records, n":
                f"{len(a):,}",
            "Predominant host species":
                (lambda top: f"{top} "
                 f"({100 * a['species'].eq(top).mean():.1f}% of records)")(
                    a["species"].mode().iat[0]),
        }

        # Animal-level counts. min_count=1 keeps an all-missing group missing
        # rather than collapsing it to 0.
        for field, label in ANIMAL_ROWS:
            total = a[field].sum(min_count=1)
            n_rep, n_mis = int(a[field].count()), int(a[field].isna().sum())
            col[f"{label} — total"] = fmt_int(total)
            col[f"{label} — records reporting / missing"] = f"{n_rep} / {n_mis}"

        table[disease] = col

    return pd.DataFrame(table).reindex(columns=W.DISEASE_ORDER)


def to_markdown(frame: pd.DataFrame) -> list[str]:
    """Render a GitHub-flavoured markdown table. Avoids a tabulate dependency,
    keeping this script on the same pandas/numpy footing as the rest of the
    pipeline."""
    header = [frame.index.name or ""] + list(frame.columns)
    rows = [[str(idx)] + [str(v) for v in row]
            for idx, row in zip(frame.index, frame.to_numpy())]
    widths = [max(len(header[i]), *(len(r[i]) for r in rows))
              for i in range(len(header))]


    def line(cells: list[str]) -> str:
        return "| " + " | ".join(
            c.ljust(w) for c, w in zip(cells, widths)) + " |"

    return [line(header),
            "|" + "|".join("-" * (w + 2) for w in widths) + "|"] + \
           [line(r) for r in rows]


def main() -> None:
    ob = pd.read_csv(W.PROCESSED / "analysis_outbreaks.csv")
    an = pd.read_csv(W.PROCESSED / "analysis_animal_counts.csv")

    t1 = build_table1(ob, an)
    t1.index.name = "Characteristic"

    W.write_table(t1, "table1_disease_profile.csv")

    title = (
        "**Table 1.** Reporting profile of rabies, high-pathogenicity avian "
        "influenza and tsetse-transmitted trypanosomosis, Nigeria, WOAH WAHIS, "
        f"{W.STUDY_START}–{W.STUDY_END}."
    )
    footnotes = [
        "Values are counts of events **reported to WAHIS**, not estimates of "
        "disease occurrence. No population denominators exist in this dataset, "
        "so no rates are presented.",
        "A year with no reporting block is shown as a year with no report and "
        "is excluded from the median (IQR); it is **not** a reported zero. "
        "Missing counts ('-' in the source) are never imputed as zero.",
        "Outbreak totals are national in scope (state + national records). "
        "Exactly one study-period record is national rather than state-level "
        "(HPAI, 2014, 1 outbreak); states reporting is therefore counted from "
        "state-level records only.",
        "**Animal-level totals must not be compared across columns.** HPAI "
        "counts commercial poultry flocks, rabies counts individually presented "
        "animals, and trypanosomosis counts herd-screened cattle; hosts, "
        "sectors and detection pathways differ entirely.",
        "'Killed and disposed of' is a control-measure indicator, not a measure "
        "of disease impact: it exceeds 'Cases' on 12.3% of comparable records "
        "because healthy in-contact birds are culled.",
        "Trypanosomosis is reportable under this WAHIS name only to 2021 "
        "('(-2021)' suffix) and is first reported in 2008, so its observation "
        "window is 2008–2021. The absence of 2022–2023 records is a "
        "classification artefact, not an observed decline.",
    ]

    md = "\n".join(
        [title, ""]
        + to_markdown(t1)
        + [""]
        + [f"{i}. {f}" for i, f in enumerate(footnotes, start=1)]
    )
    (W.TABLES / "table1_disease_profile.md").write_text(md, encoding="utf-8")

    print(t1.to_string())
    print(f"\nWritten:\n  {W.TABLES / 'table1_disease_profile.csv'}"
          f"\n  {W.TABLES / 'table1_disease_profile.md'}")


if __name__ == "__main__":
    main()
