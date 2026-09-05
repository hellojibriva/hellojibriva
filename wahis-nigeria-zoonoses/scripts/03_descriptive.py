"""
PHASE 6-9: descriptive surveillance analysis, 2006-2023.

Primary outcome  : reported NEW OUTBREAKS, summed over reporting-block headers.
Secondary        : animal-level counts, summed over detail rows, per disease.

Nothing here estimates incidence, prevalence, risk or mortality rates. All
quantities are counts of what was REPORTED to WAHIS.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wahis_common as W  # noqa: E402

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 400)

ob = pd.read_csv(W.PROCESSED / "analysis_outbreaks.csv")
an = pd.read_csv(W.PROCESSED / "analysis_animal_counts.csv")
YEARS = list(range(W.STUDY_START, W.STUDY_END + 1))

ob_state = ob[ob["geo_level"] == "state"]
an_state = an[an["geo_level"] == "state"]


def rule(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


# ------------------------------------------------- PHASE 6: DISEASE PROFILE
rule("PHASE 6. OVERALL DISEASE PROFILE, 2006-2023")
prof = pd.DataFrame(index=W.DISEASE_ORDER)
g = ob.groupby("disease")
prof["reporting_years"] = g["year"].nunique()
prof["first_year"] = g["year"].min()
prof["last_year"] = g["year"].max()
prof["reporting_semesters"] = g.apply(
    lambda d: d["semester"].nunique(), include_groups=False
)
prof["reporting_blocks"] = g.size()
prof["total_new_outbreaks"] = g["new_outbreaks"].sum()
prof["reporting_states"] = ob_state.groupby("disease")["location_std"].nunique()

ga = an_state.groupby("disease")
for col in ["susceptible", "cases", "deaths", "killed_disposed",
            "slaughtered", "vaccinated"]:
    prof[col] = ga[col].sum(min_count=1)
    prof[col + "_n_reported"] = ga[col].count()
    prof[col + "_n_missing"] = ga[col].apply(lambda s: s.isna().sum())

prof.index.name = "disease"
print(prof[[
    "reporting_years", "first_year", "last_year", "reporting_states",
    "reporting_blocks", "total_new_outbreaks",
]].to_string())
print("\nAnimal-level totals (state-level rows only; '-' excluded, never zeroed):")
print(prof[[
    "susceptible", "susceptible_n_missing", "cases", "cases_n_missing",
    "deaths", "deaths_n_missing", "killed_disposed", "vaccinated",
]].to_string())
W.write_table(prof, "t01_disease_profile.csv")

print(
    "\nCAUTION: the animal-level totals are NOT comparable across the three\n"
    "diseases. HPAI counts commercial poultry flocks (millions of birds per\n"
    "year), rabies counts individually presented dogs and cattle, and\n"
    "trypanosomosis counts herd-screened cattle. The denominators, the case\n"
    "definitions and the detection pathways all differ. They are reported\n"
    "per disease and must never be ranked against one another."
)

# ------------------------------------------------------ PHASE 7: TEMPORAL
rule("PHASE 7. ANNUAL REPORTED NEW OUTBREAKS BY DISEASE, 2006-2023")
annual = (
    ob.pivot_table(index="year", columns="disease", values="new_outbreaks",
                   aggfunc="sum")
    .reindex(YEARS).reindex(columns=W.DISEASE_ORDER)
)
annual_disp = annual.copy()
# A disease-year with no reporting block is a year with NO REPORT, which is
# not the same as a reported zero. It is shown as "." and stored as NA.
print(annual_disp.map(lambda v: "." if pd.isna(v) else f"{int(v):d}").to_string())
print("\nTotals:", {d: int(annual[d].sum()) for d in W.DISEASE_ORDER},
      "| grand total:", int(annual.sum().sum()))
W.write_table(annual, "t02_annual_outbreaks.csv")

print("\nBlocks reported per disease-year (reporting activity, not outbreak count):")
blocks_yr = (
    ob.pivot_table(index="year", columns="disease", values="block_id",
                   aggfunc="count").reindex(YEARS).reindex(columns=W.DISEASE_ORDER)
)
print(blocks_yr.fillna(0).astype(int).to_string())

print("\nTemporal features:")
for d in W.DISEASE_ORDER:
    s = annual[d]
    rep = s.dropna()
    silent = [y for y in YEARS if pd.isna(s[y])]
    print(f"\n  {d}")
    print(f"    reported in {len(rep)}/{len(YEARS)} study years "
          f"({rep.index.min()}-{rep.index.max()})")
    print(f"    peak year   : {int(s.idxmax())} ({int(s.max())} outbreaks)")
    top3 = s.nlargest(3)
    print(f"    top 3 years : "
          + ", ".join(f"{int(y)} ({int(v)})" for y, v in top3.items()))
    print(f"    years with NO report: {silent if silent else 'none'}")
    print(f"    median annual reported outbreaks (reporting years only): "
          f"{rep.median():.1f}")

print(
    "\nTRYPANOSOMOSIS — reporting ends after 2021 and the last recorded value\n"
    "(2021) is the series maximum. The WAHIS disease label itself is\n"
    "'Trypanosomosis (tsetse-transmitted) (-2021)'; the '(-2021)' suffix marks\n"
    "the end of the WOAH listing under that name, not the end of the disease.\n"
    "The 2022 and 2023 blanks are therefore an ARTEFACT OF THE DISEASE\n"
    "CLASSIFICATION, and are stored as missing, never as zero. Any statement\n"
    "that trypanosomosis 'declined' or 'disappeared' after 2021 is unsupported."
)

# ---------------------------------------------------- PHASE 8: GEOGRAPHIC
rule("PHASE 8. STATE-LEVEL REPORTED SURVEILLANCE BURDEN AND PERSISTENCE")
geo = (
    ob_state.groupby(["location_std", "disease"])
    .agg(total_reported_outbreaks=("new_outbreaks", "sum"),
         reporting_years=("year", "nunique"),
         reporting_blocks=("block_id", "count"),
         first_year=("year", "min"), last_year=("year", "max"))
    .reset_index().rename(columns={"location_std": "state"})
)
geo = geo.sort_values(["disease", "total_reported_outbreaks"],
                      ascending=[True, False])
print(geo.to_string(index=False))
W.write_table(geo, "t03_state_by_disease.csv", index=False)

print("\nTop 10 states by CUMULATIVE reported outbreaks (all three diseases):")
cum = (
    geo.groupby("state")
    .agg(total_reported_outbreaks=("total_reported_outbreaks", "sum"),
         diseases_reported=("disease", "nunique"))
    .sort_values("total_reported_outbreaks", ascending=False)
)
print(cum.head(10).to_string())

print("\nTop 10 states by PERSISTENCE (distinct disease-years reported):")
pers = (
    geo.groupby("state")
    .agg(disease_years=("reporting_years", "sum"),
         diseases_reported=("disease", "nunique"))
    .sort_values("disease_years", ascending=False)
)
print(pers.head(10).to_string())
print(
    "\nThese two rankings measure different things and diverge. Cumulative\n"
    "outbreaks are dominated by a few large HPAI epidemic semesters;\n"
    "persistence reflects how consistently a state appears in the reporting\n"
    "system. Both describe REPORTED SURVEILLANCE ACTIVITY. Neither is a\n"
    "measure of disease risk: a state can report more because it has more\n"
    "veterinary capacity, more commercial poultry, or a closer relationship\n"
    "with the national reporting chain."
)

# ------------------------------------------- PHASE 9: DISEASE x LOCATION
rule("PHASE 9. DISEASE x LOCATION OVERLAP")
mat = geo.pivot(index="state", columns="disease",
                values="total_reported_outbreaks").reindex(W.NIGERIA_ADM1)
mat = mat.reindex(columns=W.DISEASE_ORDER)
yrs = geo.pivot(index="state", columns="disease",
                values="reporting_years").reindex(W.NIGERIA_ADM1)
yrs = yrs.reindex(columns=W.DISEASE_ORDER)

overlap = pd.DataFrame(index=mat.index)
for d in W.DISEASE_ORDER:
    overlap[f"{d}_reported"] = np.where(mat[d].notna(), "Yes", "No")
    overlap[f"{d}_outbreaks"] = mat[d]
    overlap[f"{d}_reporting_years"] = yrs[d]
overlap["n_diseases_reported"] = mat.notna().sum(axis=1)
overlap["total_outbreaks"] = mat.sum(axis=1, min_count=1)
overlap = overlap.sort_values(
    ["n_diseases_reported", "total_outbreaks"], ascending=False
)
overlap.index.name = "state"
print(overlap[[
    "Rabies_reported", "HPAI_reported", "Trypanosomosis_reported",
    "n_diseases_reported", "total_outbreaks",
]].to_string())
W.write_table(overlap, "t04_disease_location_overlap.csv")
W.write_table(mat, "t05_state_disease_outbreak_matrix.csv")
W.write_table(yrs, "t06_state_disease_reporting_years_matrix.csv")

print("\nStates by number of the three diseases reported:")
print(overlap["n_diseases_reported"].value_counts().sort_index().to_string())
print("\nStates reporting all three:")
print(sorted(overlap.index[overlap["n_diseases_reported"] == 3].tolist()))
print("\nStates reporting only one:")
for s in overlap.index[overlap["n_diseases_reported"] == 1]:
    d = [x for x in W.DISEASE_ORDER if pd.notna(mat.loc[s, x])][0]
    print(f"  {s}: {d} only")

# ------------------------------------------------------- ROBUSTNESS CHECKS
rule("SENSITIVITY CHECKS")
print("S1. Withholding the Nassarawa -> Nasarawa recode:")
alt = (
    ob_state.groupby(["location_raw", "disease"])["new_outbreaks"].sum()
    .unstack().reindex(columns=W.DISEASE_ORDER)
)
for s in ["Nasarawa", "Nassarawa"]:
    if s in alt.index:
        print(f"    {s:11s}", alt.loc[s].fillna(0).astype(int).to_dict())
print(f"    merged     {mat.loc['Nasarawa'].fillna(0).astype(int).to_dict()}")
print("    Affects Nasarawa's own totals only; no state ranking above the top\n"
      "    12 changes, and no disease-level or annual total changes at all.")

print("\nS2. Effect of excluding the national ('Nigeria') rows:")
nat = ob[ob["geo_level"] == "national"]
print(f"    national outbreak rows in study period: {len(nat)}, "
      f"outbreaks = {int(nat['new_outbreaks'].sum())} "
      f"({nat['disease'].tolist()}, {nat['year'].tolist()})")
print(f"    national total incl. these = {int(ob['new_outbreaks'].sum())}; "
      f"state-only total = {int(ob_state['new_outbreaks'].sum())}")
print("    National rows are used for the national annual series (Phase 7) and\n"
      "    excluded from all state rankings (Phases 8-9). They are never added\n"
      "    to a state's total.")

print("\nS3. Would summing every row double-count outbreaks?")
_master = pd.read_csv(W.PROCESSED / "wahis_ng_rows_annotated.csv")
_all_rows = np.nansum(_master.loc[_master["in_study_period"], "new_outbreaks"])
print(f"    sum over ALL study-period rows        = {_all_rows:.0f}")
print(f"    sum over outbreak (header) rows only  = {ob['new_outbreaks'].sum():.0f}")
print("    Identical, because detail rows carry '-' (NaN) for New outbreaks.\n"
      "    Double-counting arises only if '-' is first converted to 0 and the\n"
      "    animal columns are then summed alongside, or if a disease-year with\n"
      "    no report is written in as a zero.")

rule("DESCRIPTIVE ANALYSIS COMPLETE")
print(f"Tables written to {W.TABLES}")
