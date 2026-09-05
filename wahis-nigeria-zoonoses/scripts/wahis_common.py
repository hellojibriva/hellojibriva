"""
Shared configuration and loader for the WAHIS Nigeria zoonoses analysis.

Every transformation applied to the raw WAHIS extract is defined here or in the
numbered pipeline scripts. The raw file is opened read-only and is never
modified or overwritten.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "Quantitative_data_20260905.csv"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

# --- Study scope (pre-registered by the study protocol) -------------------
STUDY_START, STUDY_END = 2006, 2023

# The three target diseases, keyed by their exact WAHIS label. No other
# disease label is present in this extract; nothing is substituted.
DISEASE_LABELS = {
    "Rabies virus (Inf. with)": "Rabies",
    "High pathogenicity avian influenza viruses (Inf. with) (poultry)": "HPAI",
    "Trypanosomosis (tsetse-transmitted) (-2021)": "Trypanosomosis",
}
DISEASE_ORDER = ["Rabies", "HPAI", "Trypanosomosis"]

# Columns that WAHIS reports as counts. Read as text first so that the
# sentinel "-" is never silently coerced to 0.
COUNT_COLS = [
    "New outbreaks",
    "Susceptible",
    "Cases",
    "Killed and disposed of",
    "Slaughtered",
    "Deaths",
    "Vaccinated",
]
ANIMAL_COUNT_COLS = [c for c in COUNT_COLS if c != "New outbreaks"]

# Snake-case names used in the derived datasets.
COUNT_RENAME = {
    "New outbreaks": "new_outbreaks",
    "Susceptible": "susceptible",
    "Cases": "cases",
    "Killed and disposed of": "killed_disposed",
    "Slaughtered": "slaughtered",
    "Deaths": "deaths",
    "Vaccinated": "vaccinated",
}

# The 36 states plus the Federal Capital Territory: the reference list against
# which the Administrative Division field is validated.
NIGERIA_ADM1 = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "Federal Capital Territory", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano",
    "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun",
    "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe",
    "Zamfara",
]

# --- Location standardisation --------------------------------------------
# Only ONE recoding is applied, and only because the dataset itself supports
# it (see 01_audit.py, which re-tests the evidence at run time):
#   * "Nassarawa" and "Nasarawa" never co-occur in the same year-semester-
#     disease stratum;
#   * "Nasarawa" appears 2006-2018 and stops; "Nassarawa" appears 2021-2022
#     only, i.e. after the 2021 WAHIS platform relaunch;
#   * both carry the same state-grain block structure.
# No other name is recoded. The five 2026 labels (Batagarawa, Gwale, Jos
# North, Toro, Ungogo) are LGAs, not states; they are flagged, not remapped,
# and all fall outside the 2006-2023 study period.
LOCATION_RECODE = {"Nassarawa": "Nasarawa"}

NATIONAL_LABEL = "Nigeria"

# Administrative Division values seen in the extract that are neither an ADM1
# unit nor the national label. Identified in the audit as LGA (ADM2) names.
SUB_STATE_LABELS = ["Batagarawa", "Gwale", "Jos North", "Toro", "Ungogo"]


def file_checksum(path: Path = RAW_FILE) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_raw() -> pd.DataFrame:
    """Read the raw extract with every field as text.

    keep_default_na=False stops pandas turning empty strings into NaN, so the
    three distinct states present in the file -- an integer, the sentinel "-",
    and an empty string -- stay distinguishable.
    """
    return pd.read_csv(
        RAW_FILE, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )


def annotate(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns. No rows are dropped and no value is overwritten."""
    out = df.copy()
    out["row_index_raw"] = np.arange(len(out))
    out["year"] = out["Year"].astype(int)

    # Numeric twins of the count columns. "-" becomes NaN (missing/not
    # reported), NOT zero. A literal "0" stays 0.
    for col in COUNT_COLS:
        out[COUNT_RENAME[col]] = pd.to_numeric(
            out[col].replace("-", np.nan), errors="raise"
        )

    out["disease"] = out["Disease"].map(DISEASE_LABELS)

    # Row type. Established empirically in the audit: a blank Species field
    # identifies the block header row that carries "New outbreaks"; a
    # populated Species field identifies an animal-count detail row.
    out["species_blank"] = out["Species"].str.strip() == ""
    out["row_type"] = np.where(
        out["species_blank"], "outbreak_row", "animal_row"
    )

    # Geographic level.
    adm = out["Administrative Division"].str.strip()
    out["geo_level"] = np.select(
        [adm == NATIONAL_LABEL, adm.isin(SUB_STATE_LABELS)],
        ["national", "sub_state"],
        default="state",
    )
    out["location_raw"] = adm
    out["location_std"] = adm.replace(LOCATION_RECODE)
    out["location_recoded"] = out["location_std"] != out["location_raw"]

    # Reporting block: the unit within which a header row and its animal
    # detail rows belong together.
    out["block_id"] = (
        out["year"].astype(str) + "|" + out["Semester"] + "|"
        + out["location_raw"] + "|" + out["disease"].astype(str) + "|"
        + out["Serotype/Subtype/Genotype"]
    )

    out["in_study_period"] = out["year"].between(STUDY_START, STUDY_END)
    return out


def short_disease_cols(frame: pd.DataFrame) -> pd.DataFrame:
    """Reindex a disease-keyed frame into the canonical disease order."""
    cols = [c for c in DISEASE_ORDER if c in frame.columns]
    return frame[cols + [c for c in frame.columns if c not in cols]]


def write_table(frame: pd.DataFrame, name: str, index: bool = True) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    path = TABLES / name
    frame.to_csv(path, index=index)
    return path
