"""
Single source of truth for the DAX measures.

From ../data (anonymized CSVs only) this script:
  1. writes ../dax/measures.dax           – Tabular Editor DAX script (also copy-paste ready for Power BI Desktop)
  2. writes ../dax/DAX_MEASURES.md        – readable measure inventory
  3. writes ../validation/reference_values.csv – expected value of every numeric measure, computed independently
     in pandas, overall / by month / by quarter / by adopter / by zone, for checking the built report
  4. writes ../validation/dax_validation_queries.dax – DAX Studio queries returning the same slices
  5. runs a static lint of the DAX (balanced brackets, every [Measure] and 'Table'[Column] reference resolves)
"""
import os, re, json
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
D = lambda f: pd.read_csv(os.path.join(ROOT, 'data', f))
svc, rep, mort, dq = D('fact_service_delivery.csv'), D('fact_facility_reporting.csv'), D('fact_mortality_national_month.csv'), D('fact_data_quality.csv')
dfac, dad, dgeo, dind = D('dim_facility.csv'), D('dim_adopter.csv'), D('dim_geography.csv'), D('dim_indicator.csv')
code = dict(zip(dind.IndicatorKey, dind.IndicatorCode))
svc['Code'] = svc.IndicatorKey.map(code); mort['Code'] = mort.IndicatorKey.map(code)

# ------------------------------------------------------------------ schema (for lint) – CSV headers + DimDate built in Power Query
SCHEMA = {
    'FactServiceDelivery': list(svc.columns[:5]), 'FactFacilityReporting': list(rep.columns), 'FactMortality': list(mort.columns[:3]),
    'FactDataQuality': list(dq.columns), 'DimFacility': list(dfac.columns), 'DimAdopter': list(dad.columns),
    'DimGeography': list(dgeo.columns), 'DimIndicator': list(dind.columns),
    'DimDate': ['Date', 'Year', 'Quarter', 'Quarter Label', 'Month Number', 'Month Name', 'Month Short', 'Month Start', 'Year Month',
                'Is Programme Month'],
}

# ------------------------------------------------------------------ measure catalogue
M = []  # dict(name, folder, expr, fmt, desc, py)  py: f(ctx)->value  (ctx = dict of filtered frames)
def add(name, folder, expr, fmt, desc, py=None): M.append(dict(name=name, folder=folder, expr=expr.strip(), fmt=fmt, desc=desc, py=py))

def s_val(ctx, c):
    v = ctx['svc'][ctx['svc'].Code == c].Value
    return None if v.notna().sum() == 0 else float(v.sum())
def div(a, b): return None if a is None or b in (None, 0) else a / b

add('Service Value', '0 Base', "SUM ( 'FactServiceDelivery'[Value] )", '#,##0',
    'Sum of indicator values in the current filter context. Blank when every value is missing (no report / not captured) – never converted to zero.',
    lambda c: None if c['svc'].Value.notna().sum() == 0 else float(c['svc'].Value.sum()))
add('Values Recorded', '0 Base', "COUNT ( 'FactServiceDelivery'[Value] )", '#,##0', 'Number of facility-month-indicator cells that hold a value (zeros included).',
    lambda c: float(c['svc'].Value.notna().sum()))

VOL = [('General Attendance', 'GEN_ATT', 'Service contacts recorded as general attendance (visits, not unique patients).'),
       ('OPD Visits', 'OPD_ATT', 'Outpatient department attendance (visits, not unique patients).'),
       ('ANC Visits', 'ANC_TOT', 'All antenatal care contacts recorded (any visit number).'),
       ('ANC First Visits', 'ANC1', 'First antenatal care visits recorded in the period.'),
       ('ANC Fourth Visits', 'ANC4', 'Fourth antenatal care visits recorded in the period.'),
       ('ANC Eighth Visits', 'ANC8', 'Eighth antenatal care visits recorded in the period.'),
       ('IPTp Dose 1', 'IPT1', 'Pregnant women given intermittent preventive treatment dose 1.'),
       ('IPTp Dose 2', 'IPT2', 'Pregnant women given IPTp dose 2.'),
       ('IPTp Dose 3', 'IPT3', 'Pregnant women given IPTp dose 3.'),
       ('Skilled Birth Deliveries', 'SBA_DEL', 'Deliveries recorded as attended by a skilled birth attendant.'),
       ('Immunization Doses <1 Year', 'IMM_FIC', 'Source field "children immunized under 1 year" = SUM of antigen doses (BCG, Penta 1–3, Vit A, MCV1). Doses, NOT fully immunized children.'),
       ('Children 0-9m Fully Immunized', 'IMM_ALT', 'Alternative source field: children 0–9 months recorded as fully immunized.'),
       ('FP Clients Counselled', 'FP_COUN', 'Family planning clients counselled.'),
       ('FP Acceptors', 'FP_ACC', 'Family planning acceptors (clients accepting a method).'),
       ('FP Male Condom Acceptances', 'FP_MCON', 'Method field captured from June 2026 only.'),
       ('FP Female Condom Acceptances', 'FP_FCON', 'Method field captured from June 2026 only.'),
       ('FP Pill Acceptances', 'FP_PILL', 'Method field captured from June 2026 only.'),
       ('FP Injectable Acceptances', 'FP_INJ', 'Method field captured from June 2026 only.'),
       ('FP Implant Acceptances', 'FP_IMP', 'Method field captured from June 2026 only.'),
       ('FP IUD Acceptances', 'FP_IUD', 'Method field captured from June 2026 only.'),
       ('U5 Malaria Tests', 'MAL_U5_T', 'Malaria tests performed on children under 5.'),
       ('U5 Malaria Positive', 'MAL_U5_P', 'Positive malaria tests among children under 5.'),
       ('U5 Malaria Treated', 'MAL_U5_R', 'Children under 5 recorded as treated for malaria.'),
       ('Adult Malaria Tests', 'MAL_AD_T', 'Malaria tests performed on adults.'),
       ('Adult Malaria Positive', 'MAL_AD_P', 'Positive malaria tests among adults.'),
       ('Adult Malaria Treated', 'MAL_AD_R', 'Adults recorded as treated for malaria.'),
       ('Community Outreaches', 'OUTREACH', 'Community outreach sessions conducted.')]
for n, c, d in VOL:
    add(n, '1 Service volumes', f"CALCULATE ( [Service Value], REMOVEFILTERS ( 'DimIndicator' ), 'DimIndicator'[IndicatorCode] = \"{c}\" )",
        '#,##0', d + ' Unaffected by the Service category slicer.', (lambda c_: lambda ctx: s_val(ctx, c_))(c))
add('Malaria Tests (All Ages)', '1 Service volumes', '[U5 Malaria Tests] + [Adult Malaria Tests]', '#,##0', 'Under-5 plus adult malaria tests.',
    lambda c: None if s_val(c, 'MAL_U5_T') is None and s_val(c, 'MAL_AD_T') is None else (s_val(c, 'MAL_U5_T') or 0) + (s_val(c, 'MAL_AD_T') or 0))
add('Malaria Positive (All Ages)', '1 Service volumes', '[U5 Malaria Positive] + [Adult Malaria Positive]', '#,##0', 'Under-5 plus adult positive tests.',
    lambda c: None if s_val(c, 'MAL_U5_P') is None and s_val(c, 'MAL_AD_P') is None else (s_val(c, 'MAL_U5_P') or 0) + (s_val(c, 'MAL_AD_P') or 0))
add('FP Method Acceptances (All Methods)', '1 Service volumes',
    "CALCULATE ( [Service Value], REMOVEFILTERS ( 'DimIndicator' ), 'DimIndicator'[ServiceCategory] = \"Family planning methods\" )", '#,##0',
    'Sum of the six method fields (Jun–Sep only). Can exceed FP Acceptors because a client may accept more than one method.',
    lambda c: (lambda v: None if v.notna().sum() == 0 else float(v.sum()))(c['svc'][c['svc'].Code.str.startswith('FP_') & ~c['svc'].Code.isin(['FP_COUN', 'FP_ACC'])].Value))

RATES = [('U5 Malaria Test Positivity %', 'U5 Malaria Positive', 'U5 Malaria Tests', 'MAL_U5_P', 'MAL_U5_T', 'Under-5 positive tests ÷ under-5 tests (ratio of sums).'),
         ('Adult Malaria Test Positivity %', 'Adult Malaria Positive', 'Adult Malaria Tests', 'MAL_AD_P', 'MAL_AD_T', 'Adult positive tests ÷ adult tests.'),
         ('U5 Treated per Positive %', 'U5 Malaria Treated', 'U5 Malaria Positive', 'MAL_U5_R', 'MAL_U5_P', 'Under-5 treated ÷ under-5 positive. A record-keeping ratio, not a clinical treatment rate: values above 100% occur where treatments exceed recorded positives (see data-quality check DQ01).'),
         ('Adult Treated per Positive %', 'Adult Malaria Treated', 'Adult Malaria Positive', 'MAL_AD_R', 'MAL_AD_P', 'Adult treated ÷ adult positive. Can exceed 100% (see DQ02).'),
         ('FP Acceptors per Client Counselled %', 'FP Acceptors', 'FP Clients Counselled', 'FP_ACC', 'FP_COUN', 'FP acceptors ÷ clients counselled in the same period (service uptake, not population coverage).'),
         ('ANC4 to ANC1 Ratio %', 'ANC Fourth Visits', 'ANC First Visits', 'ANC4', 'ANC1', 'ANC4 visits ÷ ANC1 visits recorded in the SAME period. Cross-sectional continuation proxy, NOT cohort completion: the women counted differ.'),
         ('ANC8 to ANC1 Ratio %', 'ANC Eighth Visits', 'ANC First Visits', 'ANC8', 'ANC1', 'ANC8 ÷ ANC1 in the same period (cross-sectional proxy).'),
         ('IPTp3 to IPTp1 Ratio %', 'IPTp Dose 3', 'IPTp Dose 1', 'IPT3', 'IPT1', 'IPTp dose 3 ÷ dose 1 in the same period (cross-sectional proxy).'),
         ('OPD Share of General Attendance %', 'OPD Visits', 'General Attendance', 'OPD_ATT', 'GEN_ATT', 'OPD visits ÷ general attendance.')]
for n, a, b, ca, cb, d in RATES:
    add(n, '2 Rates (ratio of sums)', f'DIVIDE ( [{a}], [{b}] )', '0.0%', d + ' Computed from aggregated numerator and denominator – never an average of facility percentages.',
        (lambda ca_, cb_: lambda ctx: div(s_val(ctx, ca_), s_val(ctx, cb_)))(ca, cb))
add('Malaria Test Positivity % (All Ages)', '2 Rates (ratio of sums)', 'DIVIDE ( [Malaria Positive (All Ages)], [Malaria Tests (All Ages)] )', '0.0%',
    'All-age positive tests ÷ all-age tests.', lambda c: div(M_[('Malaria Positive (All Ages)')](c), M_['Malaria Tests (All Ages)'](c)))

add('Expected Reports', '3 Reporting', "SUM ( 'FactFacilityReporting'[Expected] )", '#,##0', 'Facility-months expected to report (60 facilities × months in context).',
    lambda c: float(c['rep'].Expected.sum()))
add('Reports Received', '3 Reporting', "SUM ( 'FactFacilityReporting'[Reported] )", '#,##0', 'Facility-months with a valid submission (a report with zero values counts as received).',
    lambda c: float(c['rep'].Reported.sum()))
add('Reports Not Received', '3 Reporting', '[Expected Reports] - [Reports Received]', '#,##0', 'Expected facility-months without a submission.',
    lambda c: float(c['rep'].Expected.sum() - c['rep'].Reported.sum()))
add('Reporting Completeness %', '3 Reporting', 'DIVIDE ( [Reports Received], [Expected Reports] )', '0.0%',
    'Reports received ÷ reports expected. Measures REPORTING, not service coverage or programme effectiveness.',
    lambda c: div(float(c['rep'].Reported.sum()), float(c['rep'].Expected.sum())))
add('Facilities Expected', '3 Reporting', "CALCULATE ( DISTINCTCOUNT ( 'FactFacilityReporting'[FacilityKey] ), 'FactFacilityReporting'[Expected] = 1 )", '#,##0',
    'Distinct facilities expected to report in the period.', lambda c: float(c['rep'][c['rep'].Expected == 1].FacilityKey.nunique()))
add('Facilities Reporting', '3 Reporting', "CALCULATE ( DISTINCTCOUNT ( 'FactFacilityReporting'[FacilityKey] ), 'FactFacilityReporting'[Reported] = 1 )", '#,##0',
    'Distinct facilities with at least one report in the period.', lambda c: float(c['rep'][c['rep'].Reported == 1].FacilityKey.nunique()))
add('Non-response Months Recorded as 0 in Source', '3 Reporting',
    "CALCULATE ( COUNTROWS ( 'FactFacilityReporting' ), 'FactFacilityReporting'[ReportingStatus] = \"Not reported (source recorded 0 under non-response rule)\" )",
    '#,##0', 'Facility-months the source workbook filled with zeros under its non-response rule. Treated as missing in this model.',
    lambda c: float((c['rep'].ReportingStatus == 'Not reported (source recorded 0 under non-response rule)').sum()))
add('Missing Report Months', '3 Reporting', "CALCULATE ( COUNTROWS ( 'FactFacilityReporting' ), 'FactFacilityReporting'[ReportingStatus] = \"Not reported (missing)\" )",
    '#,##0', 'Facility-months with no submission that the source left blank.', lambda c: float((c['rep'].ReportingStatus == 'Not reported (missing)').sum()))
add('General Attendance per Report', '3 Reporting', 'DIVIDE ( [General Attendance], [Reports Received] )', '#,##0.0',
    'General attendance ÷ reports received – a reporting-adjusted volume that removes the effect of missing reports.',
    lambda c: div(s_val(c, 'GEN_ATT'), float(c['rep'].Reported.sum())))

add('Indicator Value Completeness %', '5 Data quality',
    "VAR expected = CALCULATE ( COUNTROWS ( 'FactServiceDelivery' ), 'FactServiceDelivery'[ValueStatus] <> \"Not captured on form\" )\n"
    "VAR complete = CALCULATE ( COUNTROWS ( 'FactServiceDelivery' ), 'FactServiceDelivery'[ValueStatus] IN { \"Reported\", \"Reported zero\", \"Corrected upstream (documented)\" } )\n"
    "RETURN DIVIDE ( complete, expected )", '0.0%',
    'Share of expected indicator values (fields on the form for facility-months in context) that were actually reported. Excludes not-yet-captured fields.',
    lambda c: div(float(c['svc'].ValueStatus.isin(['Reported', 'Reported zero', 'Corrected upstream (documented)']).sum()), float((c['svc'].ValueStatus != 'Not captured on form').sum())))
add('Fields Blank in Submitted Reports', '5 Data quality',
    "CALCULATE ( COUNTROWS ( 'FactServiceDelivery' ), 'FactServiceDelivery'[ValueStatus] = \"Field blank in report (0 per source rule)\" )", '#,##0',
    'Indicator fields left blank inside a submitted report (source rule recorded 0).',
    lambda c: float((c['svc'].ValueStatus == 'Field blank in report (0 per source rule)').sum()))
add('Data Quality Exceptions', '5 Data quality', "COUNTROWS ( 'FactDataQuality' )", '#,##0', 'All flagged checks (DQ01–DQ11) in context.', lambda c: float(len(c['dq'])))
add('Logical Inconsistency Flags', '5 Data quality', "CALCULATE ( COUNTROWS ( 'FactDataQuality' ), 'FactDataQuality'[CheckType] = \"Logical consistency\" )", '#,##0',
    'Checks DQ01–DQ05 and DQ07: a value exceeds the value it should be a subset of.', lambda c: float((c['dq'].CheckType == 'Logical consistency').sum()))
add('Facility-Months with Logical Inconsistencies', '5 Data quality',
    "COUNTROWS ( SUMMARIZE ( FILTER ( 'FactDataQuality', 'FactDataQuality'[CheckType] = \"Logical consistency\" ), 'FactDataQuality'[FacilityKey], 'FactDataQuality'[MonthDate] ) )",
    '#,##0', 'Distinct facility-months with at least one logical-consistency flag.',
    lambda c: float(len(c['dq'][c['dq'].CheckType == 'Logical consistency'][['FacilityKey', 'MonthDate']].drop_duplicates())))

GUARD = "IF ( ISFILTERED ( 'DimFacility' ) || ISFILTERED ( 'DimAdopter' ) || ISFILTERED ( 'DimGeography' ), BLANK (), {x} )"
for n, c, d in [('Under-5 Deaths', 'DTH_U5', 'Recorded under-5 deaths.'), ('Maternal Deaths', 'DTH_MAT', 'Recorded maternal deaths.'),
                ('Neonatal Deaths', 'DTH_NEO', 'Recorded neonatal deaths (first 28 days).'), ('Infant Deaths', 'DTH_INF', 'Recorded infant deaths.'),
                ('All-Category Deaths (Upper Bound)', 'DTH_ALL', 'Sum of the four mortality fields; an upper bound because one death may be entered in more than one field.')]:
    add(n, '6 Mortality (national only)',
        GUARD.format(x=f"CALCULATE ( SUM ( 'FactMortality'[Deaths] ), REMOVEFILTERS ( 'DimIndicator' ), 'DimIndicator'[IndicatorCode] = \"{c}\" )"),
        '#,##0', d + ' Published at national-month level only (small numbers); blank whenever a facility, adopter or zone filter is active.',
        (lambda c_: lambda ctx: None if ctx['sub'] else float(ctx['mort'][ctx['mort'].Code == c_].Deaths.sum()))(c))
add('Deaths per 100 Reports', '6 Mortality (national only)',
    GUARD.format(x="DIVIDE ( [All-Category Deaths (Upper Bound)], [Reports Received] ) * 100"), '0.0',
    'All-category deaths per 100 facility reports received. A facility-level event rate, not a population mortality rate.',
    lambda c: None if c['sub'] else div(float(c['mort'][c['mort'].Code == 'DTH_ALL'].Deaths.sum()), float(c['rep'].Reported.sum())) * 100)

# time comparisons (monthly and quarterly)
TIME = [('General Attendance', '#,##0'), ('ANC Visits', '#,##0'), ('Skilled Birth Deliveries', '#,##0'), ('FP Acceptors', '#,##0'),
        ('Immunization Doses <1 Year', '#,##0'), ('Malaria Tests (All Ages)', '#,##0')]
for base, fmt in TIME:
    add(f'{base} Previous Month', '4 Time comparison', f"CALCULATE ( [{base}], DATEADD ( 'DimDate'[Date], -1, MONTH ) )", fmt,
        f'{base} in the month before the month in context (use with one month selected / on a monthly axis).', None)
    add(f'{base} MoM %', '4 Time comparison',
        f"VAR cur = [{base}]\nVAR prev = [{base} Previous Month]\nRETURN IF ( HASONEVALUE ( 'DimDate'[Month Start] ) && NOT ISBLANK ( prev ), DIVIDE ( cur - prev, prev ) )",
        '+0.0%;-0.0%;0.0%', f'Month-on-month relative change in {base}. Blank for January (no prior month in the data).', None)
    add(f'{base} QoQ %', '4 Time comparison',
        f"VAR cur = [{base}]\nVAR prev = CALCULATE ( [{base}], DATEADD ( 'DimDate'[Date], -1, QUARTER ) )\n"
        f"RETURN IF ( HASONEVALUE ( 'DimDate'[Quarter Label] ) && NOT ISBLANK ( prev ), DIVIDE ( cur - prev, prev ) )",
        '+0.0%;-0.0%;0.0%', f'Quarter-on-quarter relative change in {base} (Q2 vs Q1, Q3 vs Q2). Q3 2026 September reporting is incomplete – compare with General Attendance per Report.', None)
add('Reporting Completeness MoM (pp)', '4 Time comparison',
    "VAR cur = [Reporting Completeness %]\nVAR prev = CALCULATE ( [Reporting Completeness %], DATEADD ( 'DimDate'[Date], -1, MONTH ) )\n"
    "RETURN IF ( HASONEVALUE ( 'DimDate'[Month Start] ) && NOT ISBLANK ( prev ), ( cur - prev ) * 100 )", '+0.0" pp";-0.0" pp";0.0" pp"',
    'Change in reporting completeness versus the previous month, in percentage points.', None)

add('Selected Period Label', '7 Labels & narrative',
    "VAR mn = CALCULATE ( MIN ( 'FactFacilityReporting'[MonthDate] ) )\nVAR mx = CALCULATE ( MAX ( 'FactFacilityReporting'[MonthDate] ) )\n"
    "RETURN IF ( ISBLANK ( mn ), \"No period\", IF ( mn = mx, FORMAT ( mn, \"mmmm yyyy\" ), FORMAT ( mn, \"mmm\" ) & \"–\" & FORMAT ( mx, \"mmm yyyy\" ) ) )",
    None, 'Text label of the reporting months in context (based on months present in the facts, not the calendar).', None)
add('Executive Narrative', '7 Labels & narrative',
    "VAR p = [Selected Period Label]\nVAR ga = [General Attendance]\nVAR topTbl =\n    TOPN ( 1,\n        FILTER ( ALL ( 'DimIndicator'[Indicator], 'DimIndicator'[ServiceCategory] ),\n"
    "            NOT 'DimIndicator'[ServiceCategory] IN { \"Service utilisation\", \"Family planning methods\", \"Mortality (national only)\" } ),\n"
    "        CALCULATE ( [Service Value] ), DESC )\nVAR topName = MAXX ( topTbl, 'DimIndicator'[Indicator] )\n"
    "RETURN\n    IF ( ISBLANK ( ga ), \"No facility reports match the current selection.\",\n"
    "        p & \": \" & FORMAT ( ga, \"#,##0\" ) & \" general attendance contacts were recorded from \" & FORMAT ( [Reports Received], \"#,##0\" ) & \" of \" &\n"
    "        FORMAT ( [Expected Reports], \"#,##0\" ) & \" expected facility reports (\" & FORMAT ( [Reporting Completeness %], \"0.0%\" ) & \" reporting completeness). \" &\n"
    "        \"Highest-volume indicator outside general/OPD attendance: \" & topName & \". Figures are service contacts, not unique individuals; missing reports are not counted as zero.\" )",
    None, 'Dynamic executive summary built only from validated measures; updates with every slicer.', None)
add('Contacts Not Individuals Note', '7 Labels & narrative', '"Counts are service contacts / encounters, not unique individuals."', None,
    'Static caption for KPI cards.', None)

NAMES = {m['name'] for m in M}
M_ = {m['name']: m['py'] for m in M if m['py']}

# ------------------------------------------------------------------ 1/2. DAX script + markdown
def q(s): return s.replace('"', '""')
with open(os.path.join(ROOT, 'dax', 'measures.dax'), 'w') as f:
    f.write('// Primary Healthcare Performance & Service Delivery Analytics – DAX measures\n'
            '// Generated by scripts/build_model_assets.py. Tabular Editor DAX-script syntax: in Tabular Editor use File > Open > DAX script,\n'
            "// or copy each expression into Power BI Desktop (Modeling > New measure) on the 'Measures' table.\n\n")
    for m in M:
        f.write(f"MEASURE 'Measures'[{m['name']}] =\n")
        f.write('\n'.join('    ' + ln for ln in m['expr'].split('\n')) + '\n')
        if m['fmt']: f.write(f'    , FormatString = "{q(m["fmt"])}"\n')
        f.write(f'    , DisplayFolder = "{m["folder"]}"\n    , Description = "{q(m["desc"])}"\n\n')
with open(os.path.join(ROOT, 'dax', 'DAX_MEASURES.md'), 'w') as f:
    f.write('# DAX measure inventory\n\nAll measures live on a disconnected `Measures` table, are explicit (no implicit aggregation), use `DIVIDE()` for every ratio and compute ratios as ratio-of-sums. '
            f'Source: `measures.dax` ({len(M)} measures). Generated by `scripts/build_model_assets.py`.\n\n')
    for folder in sorted({m['folder'] for m in M}):
        f.write(f'## {folder}\n\n| Measure | Format | Definition / interpretation |\n|---|---|---|\n')
        for m in [x for x in M if x['folder'] == folder]:
            f.write(f"| **{m['name']}** | `{m['fmt'] or 'text'}` | {m['desc']} |\n")
        f.write('\n<details><summary>DAX expressions</summary>\n\n')
        for m in [x for x in M if x['folder'] == folder]:
            f.write(f"```dax\n{m['name']} =\n{m['expr']}\n```\n")
        f.write('\n</details>\n\n')

# ------------------------------------------------------------------ 3. reference values
svc_f = svc.merge(dfac, on='FacilityKey'); rep_f = rep.merge(dfac, on='FacilityKey'); dq_f = dq.merge(dfac, on='FacilityKey')
Q = {'2026-01-01': 'Q1 2026', '2026-02-01': 'Q1 2026', '2026-03-01': 'Q1 2026', '2026-04-01': 'Q2 2026', '2026-05-01': 'Q2 2026',
     '2026-06-01': 'Q2 2026', '2026-07-01': 'Q3 2026', '2026-08-01': 'Q3 2026', '2026-09-01': 'Q3 2026'}
for d_ in (svc_f, rep_f, dq_f, mort): d_['Quarter'] = d_.MonthDate.map(Q)
def ctx(sel=lambda d: d.index == d.index, sub=False, mort_sel=None):
    return dict(svc=svc_f[sel(svc_f)], rep=rep_f[sel(rep_f)], dq=dq_f[sel(dq_f)], sub=sub,
                mort=mort[mort_sel(mort)] if mort_sel else mort)
contexts = [('Overall (Jan–Sep 2026)', '', ctx())]
for md in sorted(rep.MonthDate.unique()):
    contexts.append(('Month', md, ctx(lambda d, md=md: d.MonthDate == md, mort_sel=lambda d, md=md: d.MonthDate == md)))
for qq in ['Q1 2026', 'Q2 2026', 'Q3 2026']:
    contexts.append(('Quarter', qq, ctx(lambda d, qq=qq: d.Quarter == qq, mort_sel=lambda d, qq=qq: d.Quarter == qq)))
for _, a in dad.iterrows():
    contexts.append(('Adopter', a.Adopter, ctx(lambda d, k=a.AdopterKey: d.AdopterKey == k, sub=True)))
for _, z in dgeo.iterrows():
    contexts.append(('Zone', z.Zone, ctx(lambda d, k=z.ZoneKey: d.ZoneKey == k, sub=True)))
rows = []
for kind, member, c in contexts:
    for m in M:
        if not m['py']: continue
        v = m['py'](c)
        rows.append({'Measure': m['name'], 'Context': kind, 'Member': member, 'ExpectedValue': '' if v is None else round(v, 6)})
# time-comparison references (monthly MoM and quarterly QoQ)
months = sorted(rep.MonthDate.unique())
for base, _ in TIME:
    f_ = M_[base]
    for i, md in enumerate(months):
        cur = f_(ctx(lambda d, md=md: d.MonthDate == md))
        prev = f_(ctx(lambda d, md=months[i - 1]: d.MonthDate == md)) if i else None
        rows.append({'Measure': f'{base} MoM %', 'Context': 'Month', 'Member': md, 'ExpectedValue': '' if prev in (None, 0) or cur is None else round((cur - prev) / prev, 6)})
    qs = ['Q1 2026', 'Q2 2026', 'Q3 2026']
    for i, qq in enumerate(qs):
        cur = f_(ctx(lambda d, qq=qq: d.Quarter == qq)); prev = f_(ctx(lambda d, qq=qs[i - 1]: d.Quarter == qq)) if i else None
        rows.append({'Measure': f'{base} QoQ %', 'Context': 'Quarter', 'Member': qq, 'ExpectedValue': '' if prev in (None, 0) or cur is None else round((cur - prev) / prev, 6)})
ref = pd.DataFrame(rows); ref.to_csv(os.path.join(ROOT, 'validation', 'reference_values.csv'), index=False)

# ------------------------------------------------------------------ 4. DAX Studio validation queries
num = [m['name'] for m in M if m['py']]
cols = ',\n    '.join(f'"{n}", [{n}]' for n in num)
with open(os.path.join(ROOT, 'validation', 'dax_validation_queries.dax'), 'w') as f:
    f.write('// Run in DAX Studio (connected to the open Power BI Desktop model). Compare each result with validation/reference_values.csv.\n\n')
    f.write(f'// 1. Overall\nEVALUATE ROW (\n    {cols}\n)\n\n')
    for lbl, col in [('2. By month', "'DimDate'[Month Start]"), ('3. By quarter', "'DimDate'[Quarter Label]"), ('4. By adopter', "'DimAdopter'[Adopter]"), ('5. By zone', "'DimGeography'[Zone]")]:
        f.write(f'// {lbl}\nEVALUATE SUMMARIZECOLUMNS (\n    {col},\n    {cols}\n)\nORDER BY {col}\n\n')

# ------------------------------------------------------------------ 5. static lint
problems = []
for m in M:
    e = m['expr']
    s = re.sub(r'"[^"]*"', '""', e)   # drop string literals
    for o, c in ('()', '{}'):
        if s.count(o) != s.count(c): problems.append((m['name'], f'unbalanced {o}{c}'))
    for t, col in re.findall(r"'([A-Za-z]+)'\[([^\]]+)\]", s):
        if t == 'Measures': continue
        if t not in SCHEMA or col not in SCHEMA[t]: problems.append((m['name'], f"unknown column '{t}'[{col}]"))
    for ref_ in re.findall(r"(?<!')(?<![A-Za-z\]])\[([^\]]+)\]", s):
        if ref_ not in NAMES: problems.append((m['name'], f'unknown measure [{ref_}]'))
    for t in re.findall(r"'([A-Za-z]+)'(?!\[)", s):
        if t not in SCHEMA: problems.append((m['name'], f"unknown table '{t}'"))
json.dump({'measures': len(M), 'reference_rows': len(ref), 'lint_problems': problems},
          open(os.path.join(ROOT, 'validation', 'dax_static_lint.json'), 'w'), indent=2, ensure_ascii=False)
print('measures', len(M), '| reference rows', len(ref), '| lint problems', problems)
