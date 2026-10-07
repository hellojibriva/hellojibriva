"""Build the de-identified analysis dataset for the PHC Performance Dashboard.

Reads the cleaned facility-month sheet from the source workbook and writes a
public, de-identified copy:

    python scripts/build_dataset.py <source.xlsx> [--salt SECRET]

De-identification rules
-----------------------
* Facility names  -> random codes within zone (e.g. "PHC-SS-07").
* Adopter/partner -> "Partner A".."Partner D" (ordered by record count).
* State, LGA, ward -> dropped; only the geopolitical zone is kept. A facility
  takes its most frequently reported zone; the raw value is kept alongside.
* Free text (challenges, causes of death, FP methods) -> dropped. Challenges are
  kept only as keyword-derived theme flags, because the verbatim text names
  facilities, wards and funders.
* The name->code key is never written to disk. Codes are drawn with a secret
  salt, so they cannot be reversed from this script and the public CSV.
"""
import argparse
import hashlib
import json
import re
import secrets
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ZONE_CODES = {
    "North Central": "NC", "North East": "NE", "North West": "NW",
    "South East": "SE", "South South": "SS", "South West": "SW",
}
INDICATORS = {
    "General attendance": "gen_att", "OPD attendance": "opd_att",
    "Total ANC visits": "anc_total", "ANC 1": "anc1", "ANC 4": "anc4",
    "8th ANC visit": "anc8", "IPT1": "ipt1", "IPT2": "ipt2", "IPT3": "ipt3",
    "U5 malaria tested": "u5_tested", "U5 malaria positive": "u5_pos",
    "U5 malaria treated": "u5_treated", "Adult malaria tested": "ad_tested",
    "Adult malaria positive": "ad_pos", "Adult malaria treated": "ad_treated",
    "Deliveries by skilled birth attendant": "sba_deliveries",
    "Fully immunized children <1 year": "imm_doses_u1",
    "Children 0-9 months fully immunized (alt)": "fic_0_9m",
    "FP counselled": "fp_counselled", "FP acceptors": "fp_acceptors",
    "FP method: Male condoms": "fp_male_condom",
    "FP method: Female condoms": "fp_female_condom",
    "FP method: Pills": "fp_pills", "FP method: Injectables": "fp_injectables",
    "FP method: Implants": "fp_implants", "FP method: IUD": "fp_iud",
    "Outreaches conducted": "outreaches",
    "Neonatal mortality": "deaths_neonatal", "Infant mortality": "deaths_infant",
    "Total U5 mortality": "deaths_u5", "Maternal mortality": "deaths_maternal",
}

# Keyword themes for the free-text challenge field. A record can carry several.
NONE_RE = re.compile(r"^\s*(no|nil+|none|non|0|no challenges?|no complain(t|ts)?|"
                     r"not really|no any challenges|nill challenge|no, thank you)\W*$", re.I)
POSITIVE_RE = re.compile(r"thank|well done|excellent|satisfactory|^good\W*$|appreciat|bless", re.I)
THEMES = {
    "power": r"solar|electric|light|power|inverter|batter|generator|charging",
    "infrastructure": r"roof|leak|fenc|fence|(male|children|pediatric|maternity|new) wards?|wards\b|room|space|toilet|quarter|accommodation|"
                      r"building|renovat|ceiling|door|placenta|pit|shelter|block|maternity complex|"
                      r"record office|bath|erosion|infrastructure",
    "commodities": r"drug|commodit|consumable|stock|kit|rdt|vaccine|opv|rota|net\b",
    "staffing": r"staff|man ?power|midwife|nurse|chew|health workers|cleaner|gard|training|capacity",
    "wash": r"water|borehole|borehall|wash|sanitation",
    "equipment": r"equipment|refrigerator|frige|fridge|bed|wheel|wheal|wilchair|chair|gadget|device|"
                 r"ultrasound|sphygmo|shelf|fan|computer|tablet|laboratory|glaucometer",
    "transport": r"road|transport|ambulance|referral|access",
    "funding": r"fund|stipend|finance|free\b|for free",
    "network": r"network",
    "data": r"data|report|documentation",
    "security": r"secur|bandit|steal|stole|thie|theave",
}
THEME_LABELS = {
    "power": "Power / electricity", "infrastructure": "Infrastructure & space",
    "commodities": "Drugs & commodities", "staffing": "Staffing & training",
    "wash": "Water & sanitation", "equipment": "Equipment & cold chain",
    "transport": "Transport & referral", "funding": "Funding & incentives",
    "network": "Phone network", "data": "Data & reporting", "security": "Security",
}


def classify(text):
    if text is None or (isinstance(text, float) and pd.isna(text)) or not str(text).strip():
        return "not_answered", []
    t = str(text).strip()
    if NONE_RE.match(t):
        return "none", []
    themes = [k for k, pat in THEMES.items() if re.search(pat, t, re.I)]
    if themes:
        return "challenge", themes
    if POSITIVE_RE.search(t):
        return "positive", []
    if re.fullmatch(r"yes\W*", t, re.I):
        return "yes_no_detail", []
    return "other", []


def code_for(name, salt):
    return hashlib.sha256((salt + "|" + name).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--sheet", default="10_Clean_Data")
    ap.add_argument("--salt", default=None, help="secret salt; random if omitted")
    args = ap.parse_args()
    salt = args.salt or secrets.token_hex(16)

    df = pd.read_excel(args.source, sheet_name=args.sheet)
    df = df[df["Year"] == 2026].copy()

    # Facility codes: shuffle facilities within each zone by salted hash.
    fac = (df.groupby("Facility")["Geopolitical Zone"].agg(lambda s: s.mode()[0])
             .reset_index())
    fac["h"] = fac["Facility"].map(lambda n: code_for(n, salt))
    fac = fac.sort_values(["Geopolitical Zone", "h"])
    fac["n"] = fac.groupby("Geopolitical Zone").cumcount() + 1
    fac["code"] = fac.apply(lambda r: f"PHC-{ZONE_CODES[r['Geopolitical Zone']]}-{r['n']:02d}", axis=1)
    fac_map = dict(zip(fac["Facility"], fac["code"]))

    # Partners: A..D by record volume.
    order = df["Standardized Adopter"].value_counts().index.tolist()
    partner_map = {p: f"Partner {chr(65 + i)}" for i, p in enumerate(order)}

    out = pd.DataFrame({
        "month_num": df["Month Number"].astype(int),
        "month": df["Month"],
        # A facility's zone is its most frequent reported zone; one-off entry
        # errors are kept in zone_as_reported and flagged in the dashboard.
        "zone": df["Facility"].map(dict(zip(fac["Facility"], fac["Geopolitical Zone"]))),
        "zone_as_reported": df["Geopolitical Zone"],
        "facility_code": df["Facility"].map(fac_map),
        "partner": df["Standardized Adopter"].map(partner_map),
        "partner_imputed": (df["Adopter Imputed"] == "Y").astype(int),
    })
    for src, col in INDICATORS.items():
        out[col] = pd.to_numeric(df[src], errors="coerce").fillna(0).astype(int)

    cls = df["Reported challenge (verbatim)"].map(classify)
    out["challenge_status"] = cls.map(lambda x: x[0])
    for k in THEMES:
        out[f"ch_{k}"] = cls.map(lambda x, k=k: int(k in x[1]))

    out = out.sort_values(["facility_code", "month_num"]).reset_index(drop=True)

    # Safety net: no source name may leak into the output.
    blob = out.to_csv(index=False).lower()
    leaks = [n for n in list(fac_map) + list(partner_map) if n.lower() in blob]
    if leaks:
        sys.exit(f"Refusing to write: identifiers leaked: {leaks}")

    (ROOT / "data").mkdir(exist_ok=True)
    out.to_csv(ROOT / "data" / "phc_2026_deidentified.csv", index=False)
    payload = {"theme_labels": THEME_LABELS, "columns": list(out.columns),
               "rows": out.values.tolist()}
    js = "window.PHC_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n"
    (ROOT / "data" / "phc_2026_deidentified.js").write_text(js)

    print(f"rows={len(out)} facilities={out.facility_code.nunique()} partners={out.partner.nunique()}")
    print(out.challenge_status.value_counts().to_string())
    print(out[[f'ch_{k}' for k in THEMES]].sum().to_string())


if __name__ == "__main__":
    main()
