"""Generate the Power BI project (PBIP) for the PHC Performance Dashboard.

    python scripts/build_powerbi.py

Reads data/phc_2026_deidentified.csv and writes power-bi/, a Power BI Project
that opens in Power BI Desktop (File > Open > PHC_Performance_Dashboard.pbip).
The data is embedded in the model's Power Query, so the project needs no file
paths or connections: open it, select Refresh, then File > Save As to get a .pbix.
"""
import base64
import json
import shutil
import uuid
import zlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "power-bi"
NAME = "PHC_Performance_Dashboard"
SM = f"{NAME}.SemanticModel"
RP = f"{NAME}.Report"
NS = uuid.UUID("6f1c2f4e-2d0b-4b8e-9a59-0c6a1c3f7e21")  # stable ids across rebuilds

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
V_VISUAL = f"{SCHEMA}/item/report/definition/visualContainer/2.2.0/schema.json"
V_PAGE = f"{SCHEMA}/item/report/definition/page/2.0.0/schema.json"
V_REPORT = f"{SCHEMA}/item/report/definition/report/3.0.0/schema.json"

THEMES = {
    "power": "Power / electricity", "infrastructure": "Infrastructure & space",
    "commodities": "Drugs & commodities", "staffing": "Staffing & training",
    "wash": "Water & sanitation", "equipment": "Equipment & cold chain",
    "transport": "Transport & referral", "funding": "Funding & incentives",
    "network": "Phone network", "data": "Data & reporting", "security": "Security",
}


def uid(*parts):
    return str(uuid.uuid5(NS, "|".join(parts)))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path, obj):
    write(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# Semantic model (TMDL)
# --------------------------------------------------------------------------

def embed(df):
    """Raw-deflate + base64 a CSV, the same encoding Power BI's Enter Data uses."""
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = co.compress(df.to_csv(index=False).encode("utf-8")) + co.flush()
    return base64.b64encode(raw).decode("ascii")


def m_source(df, types):
    cols = ", ".join(f'{{"{c}", {t}}}' for c, t in types)
    return [
        "let",
        f'    Source = Csv.Document(Binary.Decompress(Binary.FromText("{embed(df)}", BinaryEncoding.Base64), Compression.Deflate), [Delimiter = ",", Columns = {len(df.columns)}, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
        "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
        f"    Typed = Table.TransformColumnTypes(Promoted, {{{cols}}})",
        "in",
        "    Typed",
    ]


def tq(name):
    """Quote a TMDL object name when needed."""
    simple = name.replace("_", "a").isalnum() and not name[0].isdigit()
    return name if simple else "'" + name.replace("'", "''") + "'"


def column(table, name, dtype, source, hidden=False, fmt=None, sort_by=None, calc=False):
    lines = [f"\tcolumn {tq(name)}", f"\t\tdataType: {dtype}"]
    if hidden:
        lines.append("\t\tisHidden")
    if fmt:
        lines.append(f"\t\tformatString: {fmt}")
    lines.append(f"\t\tlineageTag: {uid(table, 'col', name)}")
    lines.append("\t\tsummarizeBy: none")
    if calc:
        lines.append("\t\tisNameInferred")
        lines.append(f"\t\tsourceColumn: [{source}]")
    else:
        lines.append(f"\t\tsourceColumn: {source}")
    if sort_by:
        lines.append(f"\t\tsortByColumn: {tq(sort_by)}")
    lines += ["", "\t\tannotation SummarizationSetBy = User", ""]
    return lines


def m_table(name, df, cols):
    """cols: list of (source column, model name, dataType, hidden, sortBy)."""
    mtype = {"string": "type text", "int64": "Int64.Type"}
    lines = [f"table {tq(name)}", f"\tlineageTag: {uid(name)}", ""]
    for src, nm, dt, hidden, sort_by in cols:
        lines += column(name, nm, dt, src, hidden=hidden, fmt="0" if dt == "int64" else None, sort_by=sort_by)
    body = m_source(df[[c[0] for c in cols]], [(c[0], mtype[c[2]]) for c in cols])
    lines += [f"\tpartition {tq(name)} = m", "\t\tmode: import", "\t\tsource ="]
    lines += ["\t\t\t\t" + ln for ln in body]
    lines += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(lines)


def calc_table(name, cols, rows, hidden=False):
    """Small DAX DATATABLE. cols: list of (name, dataType, sortBy)."""
    daxtype = {"string": "STRING", "int64": "INTEGER"}
    lines = [f"table {tq(name)}"]
    if hidden:
        lines.append("\tisHidden")
    lines += [f"\tlineageTag: {uid(name)}", ""]
    for nm, dt, sort_by in cols:
        lines += column(name, nm, dt, nm, sort_by=sort_by, calc=True, fmt="0" if dt == "int64" else None)

    def lit(v):
        return f'"{v}"' if isinstance(v, str) else str(v)
    header = ", ".join(f'"{nm}", {daxtype[dt]}' for nm, dt, _ in cols)
    data = ",\n".join("\t\t\t\t\t\t{" + ", ".join(lit(v) for v in r) + "}" for r in rows)
    lines += [f"\tpartition {tq(name)} = calculated", "\t\tmode: import", "\t\tsource = ```",
              f"\t\t\t\tDATATABLE ( {header},", "\t\t\t\t\t{", data, "\t\t\t\t\t}", "\t\t\t\t)", "\t\t\t\t```", ""]
    return "\n".join(lines)


MEASURES = []  # (folder, name, dax, format, description)


def measure(folder, name, dax, fmt="#,0", desc=None):
    MEASURES.append((folder, name, dax, fmt, desc))


def define_measures():
    s = lambda c: f"SUM ( Reports[{c}] )"
    # Coverage
    measure("1 Coverage", "Reports Received", "COUNTROWS ( Reports )", desc="Facility-month reports received.")
    measure("1 Coverage", "Facilities Reporting", "DISTINCTCOUNT ( Reports[Facility Code] )")
    measure("1 Coverage", "Facilities in Scope", "COUNTROWS ( Facility )")
    measure("1 Coverage", "Expected Reports", "COUNTROWS ( Facility ) * COUNTROWS ( 'Month' )",
            desc="Facilities in the selection multiplied by months in the selection.")
    measure("1 Coverage", "Reporting Completeness", "DIVIDE ( [Reports Received], [Expected Reports] )", "0.0%")
    # Volume
    measure("2 Service volume", "Patients Seen", s("gen_att"))
    measure("2 Service volume", "OPD Attendance", s("opd_att"))
    measure("2 Service volume", "OPD Share", "DIVIDE ( [OPD Attendance], [Patients Seen] )", "0%")
    measure("2 Service volume", "Immunisation Doses", s("imm_doses_u1"),
            desc="Antigen doses to children under 1 (BCG, Penta 1-3, Vitamin A, MCV1). June includes the immunisation outreach.")
    measure("2 Service volume", "Outreaches", s("outreaches"))
    measure("2 Service volume", "SBA Deliveries", s("sba_deliveries"))
    # Maternal
    for n, c in [("ANC1", "anc1"), ("ANC4", "anc4"), ("ANC8", "anc8"), ("IPT1", "ipt1"), ("IPT2", "ipt2"), ("IPT3", "ipt3")]:
        measure("3 Antenatal care", n, s(c))
    measure("3 Antenatal care", "ANC4 Retention", "DIVIDE ( [ANC4], [ANC1] )", "0%")
    measure("3 Antenatal care", "ANC8 Retention", "DIVIDE ( [ANC8], [ANC1] )", "0%")
    measure("3 Antenatal care", "IPTp3 Completion", "DIVIDE ( [IPT3], [IPT1] )", "0%")
    measure("3 Antenatal care", "ANC Cascade", """SWITCH (
				    SELECTEDVALUE ( 'ANC Step'[Step] ),
				    "ANC1", [ANC1],
				    "ANC4", [ANC4],
				    "ANC8", [ANC8]
				)""")
    measure("3 Antenatal care", "IPTp Cascade", """SWITCH (
				    SELECTEDVALUE ( 'IPTp Step'[Step] ),
				    "IPT1", [IPT1],
				    "IPT2", [IPT2],
				    "IPT3", [IPT3]
				)""")
    # Malaria
    for n, c in [("U5 Tested", "u5_tested"), ("U5 Positive", "u5_pos"), ("U5 Treated", "u5_treated"),
                 ("Adult Tested", "ad_tested"), ("Adult Positive", "ad_pos"), ("Adult Treated", "ad_treated")]:
        measure("4 Malaria", n, s(c))
    measure("4 Malaria", "U5 Positivity", "DIVIDE ( [U5 Positive], [U5 Tested] )", "0%")
    measure("4 Malaria", "Adult Positivity", "DIVIDE ( [Adult Positive], [Adult Tested] )", "0%")
    measure("4 Malaria", "U5 Treatment Coverage", "DIVIDE ( [U5 Treated], [U5 Positive] )", "0%")
    measure("4 Malaria", "Adult Treatment Coverage", "DIVIDE ( [Adult Treated], [Adult Positive] )", "0%")
    measure("4 Malaria", "Malaria Cases", """VAR _Group = SELECTEDVALUE ( 'Malaria Step'[Group] )
				VAR _Step = SELECTEDVALUE ( 'Malaria Step'[Step] )
				RETURN
				    SWITCH (
				        TRUE (),
				        _Group = "Under 5" && _Step = "Tested", [U5 Tested],
				        _Group = "Under 5" && _Step = "Positive", [U5 Positive],
				        _Group = "Under 5" && _Step = "Treated", [U5 Treated],
				        _Group = "Adults" && _Step = "Tested", [Adult Tested],
				        _Group = "Adults" && _Step = "Positive", [Adult Positive],
				        _Group = "Adults" && _Step = "Treated", [Adult Treated]
				    )""")
    # Family planning
    measure("5 Family planning", "FP Counselled", s("fp_counselled"))
    measure("5 Family planning", "FP Acceptors", s("fp_acceptors"))
    measure("5 Family planning", "FP Acceptance", "DIVIDE ( [FP Acceptors], [FP Counselled] )", "0%")
    methods = [("Injectables", "fp_injectables"), ("Male condoms", "fp_male_condom"), ("Implants", "fp_implants"),
               ("Pills", "fp_pills"), ("Female condoms", "fp_female_condom"), ("IUD", "fp_iud")]
    measure("5 Family planning", "FP Method Total", " + ".join(s(c) for _, c in methods),
            desc="Acceptors with a method recorded. Lower than FP Acceptors because many reports omit the breakdown.")
    measure("5 Family planning", "FP Method Acceptors", "SWITCH (\n\t\t\t\t    SELECTEDVALUE ( 'FP Method'[Method] ),\n"
            + ",\n".join(f'\t\t\t\t    "{n}", {s(c)}' for n, c in methods) + "\n\t\t\t\t)")
    measure("5 Family planning", "FP Method Share", "DIVIDE ( [FP Method Acceptors], [FP Method Total] )", "0%")
    # Mortality
    deaths = [("Infant", "deaths_infant"), ("Under-5", "deaths_u5"), ("Neonatal", "deaths_neonatal"), ("Maternal", "deaths_maternal")]
    for n, c in deaths:
        measure("6 Mortality", f"{n} Deaths", s(c))
    measure("6 Mortality", "Reported Deaths", "[Infant Deaths] + [Under-5 Deaths] + [Neonatal Deaths] + [Maternal Deaths]",
            desc="Sum of the four separately reported death fields.")
    measure("6 Mortality", "Deaths by Category", "SWITCH (\n\t\t\t\t    SELECTEDVALUE ( 'Death Category'[Category] ),\n"
            + ",\n".join(f'\t\t\t\t    "{n}", [{n} Deaths]' for n, _ in deaths) + "\n\t\t\t\t)")
    # Barriers
    measure("7 Barriers", "Reports Answering", 'CALCULATE ( [Reports Received], Reports[Challenge Status] <> "not_answered" )')
    measure("7 Barriers", "Reports Naming a Challenge", 'CALCULATE ( [Reports Received], Reports[Challenge Status] = "challenge" )')
    measure("7 Barriers", "Challenge Share", "DIVIDE ( [Reports Naming a Challenge], [Reports Answering] )", "0%")
    measure("7 Barriers", "Theme Mentions", "COUNTROWS ( 'Challenge Themes' )")
    measure("7 Barriers", "Theme Share", "DIVIDE ( [Theme Mentions], [Reports Naming a Challenge] )", "0%",
            desc="Share of reports naming any challenge that mention this theme.")
    # Data quality
    checks = [("Zone entered inconsistently", "dq_zone_mismatch"), ("More positives than tests", "dq_pos_gt_tested"),
              ("More treated than confirmed", "dq_treated_gt_pos"), ("More FP acceptors than counselled", "dq_fp_acc_gt_counselled"),
              ("Attendance spike (not June)", "dq_spike_attendance"), ("Immunisation spike (not June)", "dq_spike_immunisation"),
              ("FP method breakdown missing", "dq_fp_no_method")]
    measure("8 Data quality", "Flagged Reports", "CALCULATE ( [Reports Received], Reports[dq_any] = 1 )",
            desc="Reports failing at least one consistency or outlier check. June volumes are not treated as spikes because of the immunisation outreach.")
    measure("8 Data quality", "Flagged Share", "DIVIDE ( [Flagged Reports], [Reports Received] )", "0.0%")
    measure("8 Data quality", "Reports Failing Check", "SWITCH (\n\t\t\t\t    SELECTEDVALUE ( 'DQ Check'[Check] ),\n"
            + ",\n".join(f'\t\t\t\t    "{n}", CALCULATE ( [Reports Received], Reports[{c}] = 1 )' for n, c in checks) + "\n\t\t\t\t)")
    measure("8 Data quality", "Report Status", """VAR _Reports = [Reports Received]
				VAR _Flagged = [Flagged Reports]
				RETURN
				    SWITCH (
				        TRUE (),
				        ISBLANK ( _Reports ), "✗ missing",
				        _Flagged > 0, "⚠ flagged",
				        "✓"
				    )""", fmt=None, desc="Matrix cell status: report received, flagged by a check, or missing.")
    # Narrative
    measure("0 Headline", "Headline", """VAR _Pos = FORMAT ( [U5 Positivity], "0%" )
				VAR _Drop = FORMAT ( 1 - [ANC4 Retention], "0%" )
				VAR _Comp = FORMAT ( [Reporting Completeness], "0.0%" )
				RETURN
				    _Pos & " of under-5 malaria tests are positive. "
				        & _Drop & " of women who start ANC do not reach a fourth visit. "
				        & _Comp & " of expected monthly reports were received."
				""", fmt=None)
    return checks, methods, deaths


def build_model(df):
    checks, methods, deaths = define_measures()
    d = OUT / SM / "definition"

    write(d / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n\n")
    tables = ["Reports", "Facility", "Month", "Challenge Themes", "ANC Step", "IPTp Step",
              "Malaria Step", "FP Method", "Death Category", "DQ Check"]
    write(d / "model.tmdl", "\n".join([
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        "annotation PBI_QueryOrder = " + json.dumps(["Reports", "Facility", "Challenge Themes"]),
        "",
    ] + [f"ref table {tq(t)}" for t in tables] + [""]))

    # Reports (fact)
    ind = [c for c in df.columns if df[c].dtype.kind in "iu" and c not in ("month_num",)]
    rep = df.rename(columns={"facility_code": "Facility Code", "month_num": "Month Number",
                             "challenge_status": "Challenge Status"})
    cols = [("Facility Code", "Facility Code", "string", True, None),
            ("Month Number", "Month Number", "int64", True, None),
            ("Challenge Status", "Challenge Status", "string", True, None)]
    cols += [(c, c, "int64", True, None) for c in ind]
    text = m_table("Reports", rep, cols)
    # measures go into the fact table, grouped by display folder
    mlines = []
    for folder, name, dax, fmt, desc in MEASURES:
        if desc:
            mlines.append(f"\t/// {desc}")
        if "\n" in dax:
            mlines.append(f"\tmeasure {tq(name)} = ```")
            # measure bodies sit two levels below the declaration (three tabs)
            mlines += ["\t\t\t" + ln.lstrip("\t") for ln in dax.split("\n")]
            mlines.append("\t\t\t```")
        else:
            mlines.append(f"\tmeasure {tq(name)} = {dax}")
        if fmt:
            mlines.append(f"\t\tformatString: {fmt}")
        mlines.append(f"\t\tdisplayFolder: {folder}")
        mlines.append(f"\t\tlineageTag: {uid('measure', name)}")
        if fmt is None:
            mlines += ["", "\t\tannotation PBI_FormatHint = {\"isText\":true}"]
        mlines.append("")
    head, rest = text.split("\n", 3)[:3], text.split("\n", 3)[3]
    write(d / "tables" / "Reports.tmdl", "\n".join(head) + "\n" + "\n".join(mlines) + "\n" + rest)

    # Facility dimension
    fac = (df.groupby("facility_code").agg(zone=("zone", "first"), partner=("partner", "first")).reset_index())
    fac.columns = ["Facility Code", "Zone", "Partner"]
    write(d / "tables" / "Facility.tmdl", m_table("Facility", fac, [
        ("Facility Code", "Facility Code", "string", False, None),
        ("Zone", "Zone", "string", False, None),
        ("Partner", "Partner", "string", False, None)]))

    # Challenge themes (long)
    long = []
    for k, label in THEMES.items():
        sub = df[df[f"ch_{k}"] == 1][["facility_code", "month_num"]]
        long += [(r.facility_code, int(r.month_num), label) for r in sub.itertuples()]
    ch = pd.DataFrame(long, columns=["Facility Code", "Month Number", "Theme"])
    write(d / "tables" / "Challenge Themes.tmdl", m_table("Challenge Themes", ch, [
        ("Facility Code", "Facility Code", "string", True, None),
        ("Month Number", "Month Number", "int64", True, None),
        ("Theme", "Theme", "string", False, None)]))

    months = ["January", "February", "March", "April", "May", "June", "July", "August"]
    write(d / "tables" / "Month.tmdl", calc_table("Month", [
        ("Month Number", "int64", None), ("Month", "string", "Month Number"),
        ("Month Short", "string", "Month Number"), ("Quarter", "string", None), ("Programme Event", "string", None)],
        [(i + 1, m, m[:3], f"Q{i // 3 + 1}", "Immunisation outreach" if i == 5 else "") for i, m in enumerate(months)]))
    write(d / "tables" / "ANC Step.tmdl", calc_table("ANC Step", [("Step", "string", "Order"), ("Order", "int64", None)],
                                                     [("ANC1", 1), ("ANC4", 2), ("ANC8", 3)]))
    write(d / "tables" / "IPTp Step.tmdl", calc_table("IPTp Step", [("Step", "string", "Order"), ("Order", "int64", None)],
                                                      [("IPT1", 1), ("IPT2", 2), ("IPT3", 3)]))
    write(d / "tables" / "Malaria Step.tmdl", calc_table("Malaria Step", [
        ("Group", "string", "Group Order"), ("Step", "string", "Step Order"), ("Group Order", "int64", None), ("Step Order", "int64", None)],
        [(g, st, gi, si) for gi, g in enumerate(["Under 5", "Adults"], 1) for si, st in enumerate(["Tested", "Positive", "Treated"], 1)]))
    write(d / "tables" / "FP Method.tmdl", calc_table("FP Method", [("Method", "string", "Order"), ("Order", "int64", None)],
                                                      [(n, i) for i, (n, _) in enumerate(methods, 1)]))
    write(d / "tables" / "Death Category.tmdl", calc_table("Death Category", [("Category", "string", "Order"), ("Order", "int64", None)],
                                                           [(n, i) for i, (n, _) in enumerate(deaths, 1)]))
    write(d / "tables" / "DQ Check.tmdl", calc_table("DQ Check", [("Check", "string", "Order"), ("Order", "int64", None)],
                                                     [(n, i) for i, (n, _) in enumerate(checks, 1)]))

    rels = [("Reports", "Facility Code", "Facility", "Facility Code"),
            ("Reports", "Month Number", "Month", "Month Number"),
            ("Challenge Themes", "Facility Code", "Facility", "Facility Code"),
            ("Challenge Themes", "Month Number", "Month", "Month Number")]
    write(d / "relationships.tmdl", "\n".join(
        f"relationship {uid('rel', a, b, c)}\n\tfromColumn: {tq(a)}.{tq(b)}\n\ttoColumn: {tq(c)}.{tq(e)}\n"
        for a, b, c, e in rels))

    write_json(OUT / SM / "definition.pbism", {
        "$schema": f"{SCHEMA}/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}})
    write_json(OUT / SM / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": uid("semanticmodel")}})


# --------------------------------------------------------------------------
# Report (PBIR)
# --------------------------------------------------------------------------

def lit(v):
    if isinstance(v, bool):
        return {"expr": {"Literal": {"Value": "true" if v else "false"}}}
    if isinstance(v, (int, float)):
        return {"expr": {"Literal": {"Value": f"{v}D"}}}
    return {"expr": {"Literal": {"Value": "'" + v.replace("'", "''") + "'"}}}


def field(kind, entity, prop):
    return {kind: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def proj(kind, entity, prop, active=False):
    p = {"field": field(kind, entity, prop), "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if active:
        p["active"] = True
    return p


M = lambda name: ("Measure", "Reports", name)
C = lambda table, name: ("Column", table, name)


class Page:
    def __init__(self, name, display):
        self.name, self.display, self.visuals = name, display, []

    def add(self, vname, x, y, w, h, visual):
        z = len(self.visuals)
        self.visuals.append({
            "$schema": V_VISUAL, "name": vname,
            "position": {"x": x, "y": y, "z": z * 1000, "height": h, "width": w, "tabOrder": z * 1000},
            "visual": visual})


def chart(vtype, roles, title=None, sort=None, objects=None, sync=None):
    qs = {}
    for role, fields in roles.items():
        qs[role] = {"projections": [proj(k, e, p, active=(role in ("Category", "Rows", "Columns") and i == 0))
                                    for i, (k, e, p) in enumerate(fields)]}
    v = {"visualType": vtype, "query": {"queryState": qs}}
    if sort:
        (k, e, p), direction = sort
        v["query"]["sortDefinition"] = {"sort": [{"field": field(k, e, p), "direction": direction}], "isDefaultSort": True}
    if objects:
        v["objects"] = objects
    vco = {}
    if title:
        vco["title"] = [{"properties": {"show": lit(True), "text": lit(title)}}]
    if vco:
        v["visualContainerObjects"] = vco
    if sync:
        v["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
    v["drillFilterOtherVisuals"] = True
    return v


def textbox(title, subtitle):
    runs = [{"textRuns": [{"value": title, "textStyle": {"fontFamily": "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif", "fontSize": "20pt", "color": "#15201C"}}]},
            {"textRuns": [{"value": subtitle, "textStyle": {"fontFamily": "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif", "fontSize": "10pt", "color": "#4A5852"}}]}]
    return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": runs}}]},
            "visualContainerObjects": {"title": [{"properties": {"show": lit(False)}}],
                                       "background": [{"properties": {"show": lit(False)}}],
                                       "border": [{"properties": {"show": lit(False)}}]},
            "drillFilterOtherVisuals": True}


def slicer(entity, prop, title):
    v = chart("slicer", {"Values": [C(entity, prop)]}, title=title, sync=f"{entity} {prop}",
              objects={"data": [{"properties": {"mode": lit("Dropdown")}}]})
    return v


def card(name, title=None):
    return chart("card", {"Values": [M(name)]}, title=title)


W, H, G = 1280, 720, 12  # page size and gutter


def header(page, title, subtitle):
    page.add("page_title", 16, 8, 760, 60, textbox(title, subtitle))
    for i, (e, p, t) in enumerate([("Month", "Month", "Month"), ("Facility", "Zone", "Zone"), ("Facility", "Partner", "Partner")]):
        page.add(f"slicer_{p.lower()}", 816 + i * 152, 8, 144, 60, slicer(e, p, t))


def card_row(page, names, y=80, h=92):
    n = len(names)
    w = (W - 32 - (n - 1) * 8) / n
    for i, nm in enumerate(names):
        page.add(f"card_{nm.lower().replace(' ', '_').replace('-', '_')}", round(16 + i * (w + 8)), y, round(w), h, card(nm))


def build_report():
    pages = []

    p = Page("overview", "Overview")
    header(p, "PHC Performance Dashboard", "60 primary health care facilities · 6 zones · Jan–Aug 2026 · de-identified edition")
    card_row(p, ["Reporting Completeness", "Patients Seen", "SBA Deliveries", "ANC4 Retention",
                 "IPTp3 Completion", "U5 Positivity", "FP Acceptance", "Reported Deaths"])
    p.add("attendance_line", 16, 184, 616, 262, chart("lineChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("Patients Seen"), M("OPD Attendance")]},
        title="Monthly attendance (June: immunisation outreach)", sort=(C("Month", "Month Short"), "Ascending")))
    p.add("immunisation_column", 648, 184, 616, 262, chart("clusteredColumnChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("Immunisation Doses")]},
        title="Immunisation doses, children under 1 (June: outreach)", sort=(C("Month", "Month Short"), "Ascending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("reporting_column", 16, 458, 400, 254, chart("clusteredColumnChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("Facilities Reporting")]},
        title="Facilities reporting each month", sort=(C("Month", "Month Short"), "Ascending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("outreach_column", 428, 458, 400, 254, chart("clusteredColumnChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("Outreaches")]},
        title="Community outreaches conducted", sort=(C("Month", "Month Short"), "Ascending")))
    p.add("headline_card", 840, 458, 424, 254, chart("card", {"Values": [M("Headline")]}, title="Headline for this selection",
          objects={"labels": [{"properties": {"fontSize": lit(14)}}],
                   "categoryLabels": [{"properties": {"show": lit(False)}}],
                   "wordWrap": [{"properties": {"show": lit(True)}}]}))
    pages.append(p)

    p = Page("maternal_malaria", "Maternal & malaria")
    header(p, "Antenatal care and malaria", "Where women drop out of ANC and IPTp, and how malaria is tested and treated")
    card_row(p, ["ANC4 Retention", "ANC8 Retention", "IPTp3 Completion", "U5 Positivity", "Adult Positivity", "U5 Treatment Coverage"])
    p.add("anc_cascade", 16, 184, 400, 262, chart("clusteredBarChart", {
        "Category": [C("ANC Step", "Step")], "Y": [M("ANC Cascade")]}, title="ANC visit cascade",
        sort=(C("ANC Step", "Step"), "Ascending"), objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("iptp_cascade", 428, 184, 400, 262, chart("clusteredBarChart", {
        "Category": [C("IPTp Step", "Step")], "Y": [M("IPTp Cascade")]}, title="IPTp dose cascade",
        sort=(C("IPTp Step", "Step"), "Ascending"), objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("malaria_chain", 840, 184, 424, 262, chart("clusteredColumnChart", {
        "Category": [C("Malaria Step", "Group")], "Series": [C("Malaria Step", "Step")], "Y": [M("Malaria Cases")]},
        title="Malaria: tested, positive, treated", sort=(C("Malaria Step", "Group"), "Ascending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("positivity_line", 16, 458, 616, 254, chart("lineChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("U5 Positivity"), M("Adult Positivity")]},
        title="Malaria test positivity by month", sort=(C("Month", "Month Short"), "Ascending")))
    p.add("retention_line", 648, 458, 616, 254, chart("lineChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("ANC4 Retention"), M("IPTp3 Completion")]},
        title="ANC4 retention and IPTp3 completion by month", sort=(C("Month", "Month Short"), "Ascending")))
    pages.append(p)

    p = Page("zones_facilities", "Zones & facilities")
    header(p, "Zones and facilities", "Compare zones, then sort facilities to plan supportive supervision")
    p.add("zone_table", 16, 80, 1248, 236, chart("tableEx", {"Values": [
        C("Facility", "Zone"), M("Facilities in Scope"), M("Reporting Completeness"), M("Patients Seen"),
        M("ANC4 Retention"), M("IPTp3 Completion"), M("U5 Positivity"), M("FP Acceptance"), M("Flagged Reports")]},
        title="Performance by geopolitical zone", sort=(M("ANC4 Retention"), "Ascending")))
    p.add("facility_table", 16, 328, 816, 384, chart("tableEx", {"Values": [
        C("Facility", "Facility Code"), C("Facility", "Zone"), C("Facility", "Partner"), M("Reports Received"),
        M("Patients Seen"), M("SBA Deliveries"), M("ANC4 Retention"), M("IPTp3 Completion"), M("U5 Positivity"),
        M("Flagged Reports")]}, title="Facilities (lowest ANC4 retention first)", sort=(M("ANC4 Retention"), "Ascending")))
    p.add("zone_anc4_bar", 844, 328, 420, 384, chart("clusteredBarChart", {
        "Category": [C("Facility", "Zone")], "Y": [M("ANC4 Retention")]}, title="ANC4 retention by zone",
        sort=(M("ANC4 Retention"), "Ascending"), objects={"labels": [{"properties": {"show": lit(True)}}]}))
    pages.append(p)

    p = Page("fp_mortality_barriers", "FP, mortality & barriers")
    header(p, "Family planning, mortality and barriers", "Method mix, reported deaths and the challenges facilities name")
    card_row(p, ["FP Counselled", "FP Acceptors", "FP Acceptance", "Reported Deaths", "Challenge Share"])
    p.add("fp_method_bar", 16, 184, 400, 528, chart("clusteredBarChart", {
        "Category": [C("FP Method", "Method")], "Y": [M("FP Method Acceptors")]},
        title="FP acceptors by method (where reported)", sort=(M("FP Method Acceptors"), "Descending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("deaths_bar", 428, 184, 400, 528, chart("clusteredBarChart", {
        "Category": [C("Death Category", "Category")], "Y": [M("Deaths by Category")]},
        title="Reported deaths by category", sort=(M("Deaths by Category"), "Descending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("themes_bar", 840, 184, 424, 528, chart("clusteredBarChart", {
        "Category": [C("Challenge Themes", "Theme")], "Y": [M("Theme Mentions")]},
        title="Challenges facilities report", sort=(M("Theme Mentions"), "Descending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    pages.append(p)

    p = Page("data_quality", "Data quality")
    header(p, "Data quality", "Reporting completeness and automated consistency checks. June volumes reflect the immunisation outreach.")
    card_row(p, ["Reporting Completeness", "Reports Received", "Expected Reports", "Flagged Reports", "Flagged Share"])
    p.add("status_matrix", 16, 184, 816, 528, chart("pivotTable", {
        "Rows": [C("Facility", "Facility Code")], "Columns": [C("Month", "Month Short")], "Values": [M("Report Status")]},
        title="Report status by facility and month (✓ received · ⚠ flagged · ✗ missing)"))
    p.add("checks_bar", 844, 184, 420, 258, chart("clusteredBarChart", {
        "Category": [C("DQ Check", "Check")], "Y": [M("Reports Failing Check")]},
        title="Reports failing each check", sort=(M("Reports Failing Check"), "Descending"),
        objects={"labels": [{"properties": {"show": lit(True)}}]}))
    p.add("completeness_line", 844, 454, 420, 258, chart("lineChart", {
        "Category": [C("Month", "Month Short")], "Y": [M("Reporting Completeness")]},
        title="Reporting completeness by month", sort=(C("Month", "Month Short"), "Ascending")))
    pages.append(p)

    r = OUT / RP
    defn = r / "definition"
    write_json(r / "definition.pbir", {
        "$schema": f"{SCHEMA}/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{SM}"}}})
    write_json(r / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": uid("report")}})
    write_json(defn / "version.json", {
        "$schema": f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write_json(defn / "report.json", {
        "$schema": V_REPORT,
        "themeCollection": {
            "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": {"visual": "1.8.95", "report": "2.0.95", "page": "1.3.95"}, "type": "SharedResources"},
            "customTheme": {"name": "PHC_Theme.json", "reportVersionAtImport": {"visual": "2.2.0", "report": "3.0.0", "page": "2.0.0"}, "type": "RegisteredResources"}},
        "objects": {"outspacePane": [{"properties": {"expanded": lit(False)}}]},
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": "PHC_Theme.json", "path": "PHC_Theme.json", "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True}})
    write_json(defn / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [pg.name for pg in pages], "activePageName": pages[0].name})
    for pg in pages:
        write_json(defn / "pages" / pg.name / "page.json", {
            "$schema": V_PAGE, "name": pg.name, "displayName": pg.display,
            "displayOption": "FitToPage", "height": H, "width": W})
        for v in pg.visuals:
            write_json(defn / "pages" / pg.name / "visuals" / v["name"] / "visual.json", v)

    res = r / "StaticResources"
    for src, dest in [("CY24SU10.json", res / "SharedResources" / "BaseThemes"),
                      ("PHC_Theme.json", res / "RegisteredResources")]:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "scripts" / "powerbi" / src, dest / src)


def main():
    df = pd.read_csv(ROOT / "data" / "phc_2026_deidentified.csv")
    if OUT.exists():
        shutil.rmtree(OUT)
    build_model(df)
    build_report()
    write_json(OUT / f"{NAME}.pbip", {
        "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": RP}}], "settings": {"enableAutoRecovery": True}})
    write(OUT / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    shutil.copy(ROOT / "scripts" / "powerbi" / "README.md", OUT / "README.md")
    zip_base = ROOT / f"{NAME}_PowerBI"
    shutil.make_archive(str(zip_base), "zip", root_dir=OUT.parent, base_dir=OUT.name)
    print(f"wrote {OUT.relative_to(ROOT)}/ with {len(MEASURES)} measures, and {zip_base.name}.zip")


if __name__ == "__main__":
    main()
