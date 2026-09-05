"""
PHASE 5: build the derived analysis datasets.

The raw file is read-only and untouched. Three derived datasets are written to
data/processed/, plus a transformation log. Every exclusion is counted and
reported; nothing is dropped silently.

  1. wahis_ng_rows_annotated.csv   all 1,112 raw rows + derived columns
  2. analysis_outbreaks.csv        one row per reporting block header
                                   (unit of the PRIMARY outcome)
  3. analysis_animal_counts.csv    one row per animal-category x species record
                                   (unit of the SECONDARY outcomes)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wahis_common as W  # noqa: E402

W.PROCESSED.mkdir(parents=True, exist_ok=True)
log: list[dict] = []


def step(name: str, detail: str, n_in: int, n_out: int) -> None:
    log.append({"step": name, "detail": detail, "rows_in": n_in,
                "rows_out": n_out, "rows_removed": n_in - n_out})
    print(f"[{name}] {detail}: {n_in} -> {n_out} (removed {n_in - n_out})")


raw = W.load_raw()
df = W.annotate(raw)
print(f"Raw file: {W.RAW_FILE.name}  md5={W.file_checksum()}  rows={len(df)}")

# ---- 1. Annotated master (nothing removed) -------------------------------
keep = [
    "row_index_raw", "year", "Semester", "World region", "Country",
    "location_raw", "location_std", "location_recoded", "geo_level",
    "Disease", "disease", "Serotype/Subtype/Genotype", "Animal Category",
    "Species", "Measuring units", "Event_id", "Outbreak_id", "block_id",
    "row_type", "in_study_period",
] + list(W.COUNT_RENAME.values())
master = df[keep].rename(columns={
    "Semester": "semester", "World region": "world_region", "Country": "country",
    "Disease": "disease_wahis_label", "Serotype/Subtype/Genotype": "serotype",
    "Animal Category": "animal_category", "Species": "species",
    "Measuring units": "measuring_units", "Event_id": "event_id",
    "Outbreak_id": "outbreak_id",
})
master.to_csv(W.PROCESSED / "wahis_ng_rows_annotated.csv", index=False)
step("master", "annotated copy of every raw row, nothing dropped",
     len(df), len(master))

# ---- 2. Analysis frames ---------------------------------------------------
# Exclusion 1: study period. Retained in the master, excluded from analysis.
n0 = len(df)
sp = df[df["in_study_period"]].copy()
step("E1_period", f"restrict to {W.STUDY_START}-{W.STUDY_END} "
     f"(2005 n={(df['year'] == 2005).sum()}, 2024-2026 n={(df['year'] > W.STUDY_END).sum()})",
     n0, len(sp))

# Exclusion 2: sub-state (ADM2) rows. Zero inside the study period, but the
# filter is kept so the pipeline stays correct if the period is widened.
n1 = len(sp)
sp = sp[sp["geo_level"] != "sub_state"]
step("E2_adm2", "drop ADM2/LGA-grain rows (all fall in 2026)", n1, len(sp))

# Outbreak frame: header rows only. geo_level is retained so that national
# rows can be included in national summaries and excluded from state ones.
ob = sp[sp["row_type"] == "outbreak_row"][
    ["block_id", "year", "Semester", "disease", "Serotype/Subtype/Genotype",
     "geo_level", "location_raw", "location_std", "Animal Category",
     "new_outbreaks"]
].rename(columns={"Semester": "semester",
                  "Serotype/Subtype/Genotype": "serotype",
                  "Animal Category": "header_animal_category"})
assert ob["new_outbreaks"].notna().all(), "header row without an outbreak count"
assert not ob["block_id"].duplicated().any(), "two header rows in one block"
ob.to_csv(W.PROCESSED / "analysis_outbreaks.csv", index=False)
step("outbreaks", "one row per reporting-block header", len(sp), len(ob))

# Animal-count frame: detail rows only.
an = sp[sp["row_type"] == "animal_row"][
    ["block_id", "year", "Semester", "disease", "Serotype/Subtype/Genotype",
     "geo_level", "location_raw", "location_std", "Animal Category", "Species",
     "Measuring units"] + [W.COUNT_RENAME[c] for c in W.ANIMAL_COUNT_COLS]
].rename(columns={"Semester": "semester",
                  "Serotype/Subtype/Genotype": "serotype",
                  "Animal Category": "animal_category", "Species": "species",
                  "Measuring units": "measuring_units"})
an["all_counts_missing"] = an[
    [W.COUNT_RENAME[c] for c in W.ANIMAL_COUNT_COLS]
].isna().all(axis=1)
an.to_csv(W.PROCESSED / "analysis_animal_counts.csv", index=False)
step("animal_counts", "one row per animal-category x species record",
     len(sp), len(an))
print(f"       of which informationally empty (every count '-'): "
      f"{int(an['all_counts_missing'].sum())} — retained and flagged, not dropped")

# ---- 3. Location standardisation table -----------------------------------
loc = (
    df.groupby(["location_raw", "location_std", "geo_level"])
    .agg(n_rows=("row_index_raw", "size"), first_year=("year", "min"),
         last_year=("year", "max"))
    .reset_index()
)
loc["action"] = "kept as reported"
loc.loc[loc["location_raw"] != loc["location_std"], "action"] = (
    "recoded (spelling variant; disjoint years, never co-occurring)"
)
loc.loc[loc["geo_level"] == "national", "action"] = (
    "kept, flagged national — excluded from state-level analysis"
)
loc.loc[loc["geo_level"] == "sub_state", "action"] = (
    "kept, flagged ADM2/LGA — excluded from state-level analysis, not rolled up"
)
loc = loc.sort_values(["geo_level", "location_raw"])
loc.to_csv(W.PROCESSED / "location_standardisation.csv", index=False)
print(f"\nLocation standardisation table: {len(loc)} labels, "
      f"{int((loc['location_raw'] != loc['location_std']).sum())} recoded")

pd.DataFrame(log).to_csv(W.PROCESSED / "transformation_log.csv", index=False)
print(f"\nWritten to {W.PROCESSED}")
for p in sorted(W.PROCESSED.glob("*.csv")):
    print(f"  {p.name:36s} {p.stat().st_size:>9,} bytes")
