"""
PHASE 1-4: data audit of the raw WAHIS Nigeria extract.

Runs every structural check that the audit report cites, writes machine-readable
audit tables to outputs/tables/, and prints a human-readable log. Reads the raw
file only; writes nothing to data/raw/.
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
pd.set_option("display.max_columns", 60)


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


raw = W.load_raw()
df = W.annotate(raw)

# ---------------------------------------------------------------- A. STRUCTURE
rule("A. FILE STRUCTURE")
print(f"File          : {W.RAW_FILE.name}")
print(f"MD5           : {W.file_checksum()}")
print(f"Rows          : {len(df):,}")
print(f"Columns       : {raw.shape[1]}")
print(f"Encoding      : UTF-8 with BOM (utf-8-sig)")
print(f"Year range    : {df['year'].min()}-{df['year'].max()}")
print(f"Country       : {sorted(raw['Country'].unique())}")
print(f"World region  : {sorted(raw['World region'].unique())}")

structure = pd.DataFrame(
    {
        "column": raw.columns,
        "stored_as": ["text (all fields read as str)"] * raw.shape[1],
        "n_unique": [raw[c].nunique() for c in raw.columns],
        "n_dash": [(raw[c] == "-").sum() for c in raw.columns],
        "n_empty": [(raw[c].str.strip() == "").sum() for c in raw.columns],
        "example": [
            next((v for v in raw[c] if v not in ("-", "")), "") for c in raw.columns
        ],
    }
)
print()
print(structure.to_string(index=False))
W.write_table(structure, "audit_01_column_structure.csv", index=False)

rule("A2. CATEGORICAL DOMAINS")
for col in [
    "Disease", "Animal Category", "Species", "Serotype/Subtype/Genotype",
    "Measuring units", "Semester",
]:
    vc = raw[col].replace("", "(blank)").value_counts()
    print(f"\n--- {col}: {len(vc)} distinct ---")
    print(vc.to_string())

print("\n--- Event_id / Outbreak_id coverage ---")
for col in ["Event_id", "Outbreak_id"]:
    populated = (raw[col] != "-").sum()
    print(
        f"{col}: populated on {populated}/{len(raw)} rows "
        f"({100 * populated / len(raw):.1f}%); distinct ids = "
        f"{raw.loc[raw[col] != '-', col].nunique()}"
    )
print(
    "\n=> Both identifier fields are effectively empty. Event/outbreak linkage\n"
    "   CANNOT be reconstructed from ids; it must be inferred from the\n"
    "   Year x Semester x Location x Disease x Serotype reporting block."
)

# ---------------------------------------------------------------- B. MISSINGNESS
rule("B. MISSINGNESS (raw file, all 1,112 rows)")
rows = []
for col in W.COUNT_COLS:
    s = raw[col]
    rows.append(
        {
            "variable": col,
            "n_rows": len(s),
            "n_dash": int((s == "-").sum()),
            "pct_dash": round(100 * (s == "-").mean(), 1),
            "n_empty_string": int((s.str.strip() == "").sum()),
            "n_true_null": int(s.isna().sum()),
            "n_zero": int((s == "0").sum()),
            "n_positive": int((~s.isin(["-", "0"]) & (s.str.strip() != "")).sum()),
        }
    )
for col in [
    "Administrative Division", "Disease", "Animal Category", "Species",
    "Serotype/Subtype/Genotype", "Event_id", "Outbreak_id",
]:
    s = raw[col]
    rows.append(
        {
            "variable": col,
            "n_rows": len(s),
            "n_dash": int((s == "-").sum()),
            "pct_dash": round(100 * (s == "-").mean(), 1),
            "n_empty_string": int((s.str.strip() == "").sum()),
            "n_true_null": int(s.isna().sum()),
            "n_zero": np.nan,
            "n_positive": np.nan,
        }
    )
miss = pd.DataFrame(rows)
print(miss.to_string(index=False))
W.write_table(miss, "audit_02_missingness_all_rows.csv", index=False)

print(
    "\nNOTE: there are ZERO true nulls and ZERO empty strings in the seven count\n"
    "columns. Every non-integer entry is the literal sentinel '-'. '-' and '0'\n"
    "are therefore distinct encodings and are kept distinct: '-' = not reported,\n"
    "'0' = reported as none. 'New outbreaks' never takes the value 0 anywhere in\n"
    "the file, which confirms the two are not interchangeable."
)

rule("B2. MISSINGNESS BY ROW TYPE")
for rt in ["outbreak_row", "animal_row"]:
    sub = raw[df["row_type"].values == rt]
    tab = pd.DataFrame(
        {
            "n_dash": [(sub[c] == "-").sum() for c in W.COUNT_COLS],
            "pct_dash": [round(100 * (sub[c] == "-").mean(), 1) for c in W.COUNT_COLS],
            "n_zero": [(sub[c] == "0").sum() for c in W.COUNT_COLS],
            "n_positive": [(~sub[c].isin(["-", "0"])).sum() for c in W.COUNT_COLS],
        },
        index=W.COUNT_COLS,
    )
    print(f"\n--- {rt} (n={len(sub)}) ---")
    print(tab.to_string())
    W.write_table(tab, f"audit_03_missingness_{rt}.csv")

# ------------------------------------------------------------- C. DUPLICATES
rule("C. DUPLICATE ASSESSMENT (no rows are deleted)")
exact = raw.duplicated(keep=False)
print(f"C1. Exact duplicate rows (all 19 columns identical): {int(exact.sum())}")

key = ["year", "Semester", "location_raw", "Disease", "Serotype/Subtype/Genotype"]
blocks = df.groupby(key, dropna=False).agg(
    n_rows=("row_index_raw", "size"),
    n_outbreak_rows=("species_blank", "sum"),
)
blocks["n_animal_rows"] = blocks["n_rows"] - blocks["n_outbreak_rows"]
print(f"\nC2. Reporting blocks (Year x Semester x Location x Disease x Serotype): {len(blocks)}")
print("    Outbreak (header) rows per block:")
print(blocks["n_outbreak_rows"].value_counts().sort_index().to_string())
print("    Animal (detail) rows per block:")
print(blocks["n_animal_rows"].value_counts().sort_index().to_string())
print(
    "\n=> No block ever carries two header rows, so 'New outbreaks' is never\n"
    "   repeated within a block. Repeated Disease/Location/Year combinations\n"
    "   arise from (a) the two semesters of a year, (b) multiple species or\n"
    "   animal categories inside one block, and (c) two blocks distinguished\n"
    "   only by virus subtype. None of these is a duplicated outbreak count."
)

print("\nC3. Blocks with animal counts but NO outbreak row (header-less blocks):")
headerless = blocks[blocks["n_outbreak_rows"] == 0]
print(headerless.to_string())
W.write_table(headerless.reset_index(), "audit_04_headerless_blocks.csv", index=False)
print(
    "\n=> These are six-monthly follow-up reports on animals affected by\n"
    "   previously notified events with no NEW outbreak in that semester.\n"
    "   They must NOT be imputed as 'New outbreaks = 0' nor dropped: they\n"
    "   carry valid animal-level data."
)

print("\nC4. Year x Semester x Location x Disease strata split across TWO blocks by subtype:")
sero = df.groupby(
    ["year", "Semester", "location_raw", "Disease"], dropna=False
)["Serotype/Subtype/Genotype"].nunique()
split = sero[sero > 1]
for k in split.index:
    m = (
        (df["year"] == k[0]) & (df["Semester"] == k[1])
        & (df["location_raw"] == k[2]) & (df["Disease"] == k[3])
    )
    print()
    print(
        df.loc[m, ["year", "Semester", "location_raw", "disease",
                   "Serotype/Subtype/Genotype", "Animal Category", "Species",
                   "new_outbreaks", "cases", "deaths"]].to_string(index=False)
    )

# --------------------------------------------- PHASE 2. ROW-STRUCTURE PROOF
rule("PHASE 2. WAHIS ROW STRUCTURE")
print("Cross-tabulation: Species blank  x  'New outbreaks' populated")
print(pd.crosstab(df["species_blank"], df["new_outbreaks"].notna()))
print("\nCross-tabulation: 'New outbreaks' populated  x  any animal count populated")
any_animal = df[[W.COUNT_RENAME[c] for c in W.ANIMAL_COUNT_COLS]].notna().any(axis=1)
print(pd.crosstab(df["new_outbreaks"].notna(), any_animal))
print("\nCross-tabulation: Measuring units x Species blank")
print(pd.crosstab(raw["Measuring units"], df["species_blank"]))

both = df[df["new_outbreaks"].notna() & any_animal]
print(f"\nRows carrying BOTH an outbreak count and animal counts: {len(both)}")
print(
    both[["year", "location_raw", "disease", "Animal Category", "Species",
          "Event_id", "Outbreak_id", "new_outbreaks", "susceptible", "cases",
          "deaths"]].to_string(index=False)
)
print(
    "\n=> All such rows fall in 2026, carry Event_id/Outbreak_id, and reflect the\n"
    "   post-relaunch WAHIS export format (one row per outbreak, ADM2 location).\n"
    "   None falls inside the 2006-2023 study period."
)

print("\nWorked example of the pre-2024 block structure "
      "(Bauchi, Jul-Dec 2012, rabies):")
ex = df[(df["year"] == 2012) & (df["location_raw"] == "Bauchi")
        & (df["disease"] == "Rabies")]
print(
    ex[["Semester", "Serotype/Subtype/Genotype", "Animal Category", "Species",
        "row_type", "new_outbreaks", "susceptible", "cases", "deaths"]]
    .to_string(index=False)
)
print(
    "\n=> The outbreak count (2 + 2) sits ONLY on the two header rows; the four\n"
    "   species rows carry animal counts and '-' for New outbreaks. Summing the\n"
    "   'New outbreaks' column over every row therefore does NOT double-count,\n"
    "   because detail rows contribute NaN, not a repeated total. Summing\n"
    "   animal counts over every row likewise does not double-count, because\n"
    "   header rows contribute NaN. The real hazard is the opposite one:\n"
    "   converting '-' to 0 before aggregating, which would fabricate zeros."
)

print("\nHeader-row 'Animal Category' label by year (reporting-format change):")
print(pd.crosstab(df.loc[df["species_blank"], "year"],
                  df.loc[df["species_blank"], "Animal Category"]).to_string())
print(
    "\n=> Before 2020 the header is always labelled 'Both animal categories';\n"
    "   from 2020 a 'Domestic'-labelled header appears and from 2024 it is the\n"
    "   only form. Row type must therefore be identified by a blank Species\n"
    "   field, NOT by the Animal Category label."
)

# -------------------------------------------- PHASE 3. NATIONAL VS STATE
rule("PHASE 3. GEOGRAPHIC STRUCTURE")
print("Administrative Division values by inferred level:")
geo = (
    df.groupby(["geo_level", "location_raw"])
    .agg(n_rows=("row_index_raw", "size"), first_year=("year", "min"),
         last_year=("year", "max"))
    .sort_values(["geo_level", "n_rows"], ascending=[True, False])
)
print(geo.to_string())
W.write_table(geo.reset_index(), "audit_05_geographic_levels.csv", index=False)

print(f"\nADM1 reference list has {len(W.NIGERIA_ADM1)} units (36 states + FCT).")
present = set(df.loc[df["geo_level"] == "state", "location_std"])
print(f"ADM1 units absent from the whole extract: {sorted(set(W.NIGERIA_ADM1) - present)}")
print(f"Labels that are neither ADM1 nor 'Nigeria': "
      f"{sorted(set(df['location_raw']) - set(W.NIGERIA_ADM1) - {'Nigeria'})}")

print("\nNational ('Nigeria') rows in the full extract:")
print(
    df[df["geo_level"] == "national"][
        ["year", "Semester", "disease", "Animal Category", "Species",
         "row_type", "new_outbreaks", "susceptible", "cases", "deaths"]
    ].to_string(index=False)
)
print(
    "\n=> 'Nigeria' rows are structurally identical to state rows (same header +\n"
    "   detail block) but carry no subnational location. They are country-level\n"
    "   reports where no state was specified -- NOT a national total that\n"
    "   aggregates the state rows. They must still be excluded from state\n"
    "   rankings, because they cannot be assigned to a state."
)

print("\nSub-state (ADM2 / LGA) labels:")
print(
    df[df["geo_level"] == "sub_state"][
        ["year", "Semester", "location_raw", "disease", "Event_id",
         "Outbreak_id", "new_outbreaks", "cases", "deaths"]
    ].to_string(index=False)
)
print(
    "\n=> Batagarawa (Katsina), Gwale and Ungogo (Kano), Jos North (Plateau) and\n"
    "   Toro (Bauchi) are Local Government Areas, not states. They appear only\n"
    "   in Jan-Jun 2026, i.e. entirely outside the study period. They are\n"
    "   flagged, not remapped: rolling them up to their parent state would mix\n"
    "   two geographic grains."
)

rule("PHASE 3b. EVIDENCE FOR THE ONE LOCATION RECODE (Nassarawa -> Nasarawa)")
nas = df[df["location_raw"].isin(["Nasarawa", "Nassarawa"])]
co = pd.crosstab(
    [nas["year"], nas["Semester"], nas["disease"]], nas["location_raw"]
)
print(co.to_string())
overlap = ((co.get("Nasarawa", 0) > 0) & (co.get("Nassarawa", 0) > 0)).sum()
print(f"\nStrata where BOTH spellings appear: {overlap}")
print(
    f"'Nasarawa' years : {sorted(nas.loc[nas['location_raw'] == 'Nasarawa', 'year'].unique())}\n"
    f"'Nassarawa' years: {sorted(nas.loc[nas['location_raw'] == 'Nassarawa', 'year'].unique())}"
)
print(
    "\n=> The two spellings never co-occur and their year ranges are disjoint\n"
    "   either side of the 2021 WAHIS relaunch. Both carry state-grain blocks.\n"
    "   This is a label change for one state, not two places, so the single\n"
    "   recode Nassarawa -> Nasarawa is applied. 03_descriptive.py reports a\n"
    "   sensitivity analysis in which the recode is withheld."
)

# ------------------------------------------------ INTERNAL CONSISTENCY
rule("D. INTERNAL CONSISTENCY OF THE ANIMAL-COUNT FIELDS")
det = df[df["row_type"] == "animal_row"]
checks = [
    ("cases", "susceptible", "Cases > Susceptible"),
    ("deaths", "cases", "Deaths > Cases"),
    ("deaths", "susceptible", "Deaths > Susceptible"),
    ("killed_disposed", "cases", "Killed & disposed of > Cases"),
    ("killed_disposed", "susceptible", "Killed & disposed of > Susceptible"),
]
out = []
for a, b, label in checks:
    m = det[a].notna() & det[b].notna()
    viol = int((det.loc[m, a] > det.loc[m, b]).sum())
    out.append({"check": label, "comparable_rows": int(m.sum()),
                "violations": viol,
                "pct": round(100 * viol / m.sum(), 1) if m.sum() else np.nan})
cons = pd.DataFrame(out)
print(cons.to_string(index=False))
W.write_table(cons, "audit_06_internal_consistency.csv", index=False)
print(
    "\n=> 'Killed and disposed of' exceeds 'Cases' on 12% of comparable rows.\n"
    "   That is expected, not an error: culling removes healthy in-contact\n"
    "   birds as a CONTROL measure. It is a response indicator, not a measure\n"
    "   of disease. The small number of Cases>Susceptible and Deaths>Cases\n"
    "   violations are genuine source-data inconsistencies and are retained\n"
    "   and flagged rather than corrected."
)

rule("AUDIT COMPLETE")
print(f"Audit tables written to {W.TABLES}")
