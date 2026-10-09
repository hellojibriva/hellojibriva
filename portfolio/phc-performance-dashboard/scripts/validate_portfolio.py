"""
Automated QA for the portfolio outputs. Reads the confidential source workbook (outside the repo) only to check that
nothing identifying leaked and that totals reconcile. Writes ../validation/automated_checks.json containing
test names, outcomes and counts – never any identifier.

Usage: python validate_portfolio.py --workbook <source.xlsx> --private-dir <private dir>
"""
import argparse, os, re, json, glob, zipfile
import pandas as pd

ap = argparse.ArgumentParser(); ap.add_argument('--workbook', required=True); ap.add_argument('--private-dir', required=True)
a = ap.parse_args()
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
D = lambda f: pd.read_csv(os.path.join(ROOT, 'data', f))
cd = pd.read_excel(a.workbook, sheet_name='Clean_Data'); tl = pd.read_excel(a.workbook, sheet_name='Trace_Long')
mit = pd.read_excel(a.workbook, sheet_name='Monthly_Indicator_Table', header=None)
svc, rep, mort = D('fact_service_delivery.csv'), D('fact_facility_reporting.csv'), D('fact_mortality_national_month.csv')
dfac, dad, dind, dgeo = D('dim_facility.csv'), D('dim_adopter.csv'), D('dim_indicator.csv'), D('dim_geography.csv')
mapping = pd.read_csv(os.path.join(a.private_dir, 'INTERNAL_identity_mapping_DO_NOT_SHARE.csv'))
R = []
def test(tid, area, name, ok, detail=''):
    R.append({'id': tid, 'area': area, 'test': name, 'outcome': 'PASS' if ok else 'FAIL', 'detail': detail})

# ---------------------------------------------------------------- privacy
ident = set()
for col in ['Facility', 'Facility (as reported)', 'Adopter', 'Adopter (as reported)', 'State', 'LGA', 'Ward']:
    ident |= {str(v).strip() for v in cd[col].dropna().unique()}
extra = os.path.join(a.private_dir, 'extra_identifiers.txt')   # e.g. organisation acronyms / long names (kept private)
if os.path.exists(extra): ident |= {l.strip() for l in open(extra, encoding='utf-8') if l.strip()}
ident = {i for i in ident if len(i) >= 3}
allow = os.path.join(a.private_dir, 'reviewed_common_words.txt')  # identifiers that are ordinary English words, reviewed manually
allowed = {l.strip().lower() for l in open(allow, encoding='utf-8')} if os.path.exists(allow) else set()
n_allowed = sum(1 for i in ident if i.lower() in allowed)
ident = {i for i in ident if i.lower() not in allowed}
files = [p for p in glob.glob(os.path.join(ROOT, '**', '*'), recursive=True) if os.path.isfile(p)]
leaks = 0; leak_files = set()
for p in files:
    try: txt = open(p, encoding='utf-8').read()
    except UnicodeDecodeError: continue
    for i in ident:
        if re.search(r'(?<![A-Za-z0-9])' + re.escape(i) + r'(?![A-Za-z0-9])', txt, flags=re.I):
            leaks += 1; leak_files.add(os.path.relpath(p, ROOT))
test('P1', 'Privacy', f'No facility/adopter/state/LGA/ward name from the source appears in any portfolio file ({len(files)} files, {len(ident)} identifiers scanned)',
     leaks == 0, (f'{leaks} hits in {sorted(leak_files)}' if leaks else '0 hits') + f'; {n_allowed} identifier(s) that are ordinary English words excluded after manual review')
test('P2', 'Privacy', 'No identity mapping file inside the portfolio folder',
     not any(re.search(r'mapping|do_not_share', os.path.basename(p), re.I) for p in files), 'checked file names')
test('P3', 'Privacy', 'Facility labels follow "Facility NNN" and adopter labels "Adopter X"',
     dfac.Facility.str.fullmatch(r'Facility \d{3}').all() and dad.Adopter.str.fullmatch(r'Adopter [A-Z]').all())
test('P4', 'Privacy', 'No state, LGA, ward, backend-row or free-text note columns in published data',
     not any(c in pd.concat([pd.read_csv(f, nrows=1) for f in glob.glob(os.path.join(ROOT, 'data', '*.csv'))], axis=1).columns
             for c in ['State', 'LGA', 'Ward', 'Backend_Row', 'Context_Note', 'Facility (as reported)']))
cells = dfac.groupby(['AdopterKey', 'ZoneKey']).size()
supp = dgeo[dgeo.IsSuppressedGroup == 1].ZoneKey.tolist()
test('P5', 'Privacy', 'No adopter × disclosed-zone cell contains fewer than 3 facilities',
     all(n >= 3 for (ak, zk), n in cells.items() if zk not in supp), f'smallest disclosed cell = {min(n for (ak, zk), n in cells.items() if zk not in supp)}')
test('P6', 'Privacy', 'Mortality published only at national-month grain (no facility/zone/adopter keys)', list(mort.columns) == ['MonthDate', 'IndicatorKey', 'Deaths'])

# ---------------------------------------------------------------- pseudonym stability
test('S1', 'Anonymization', 'Each source facility maps to exactly one pseudonym and vice versa (60 ↔ 60)',
     mapping.Facility.nunique() == mapping.FacilityPseudonym.nunique() == len(mapping) == cd.Facility.nunique() == len(dfac))
test('S2', 'Anonymization', 'Each source adopter maps to exactly one pseudonym (4 ↔ 4)', mapping.groupby('Adopter').AdopterPseudonym.nunique().max() == 1 and mapping.AdopterPseudonym.nunique() == cd.Adopter.nunique())
test('S3', 'Anonymization', 'Every facility key appears in all 9 months of the reporting fact (consistent across periods)',
     rep.groupby('FacilityKey').MonthDate.nunique().eq(9).all() and len(rep) == 540)
m2 = mapping.set_index('Facility')
fac_key = dict(zip(dfac.Facility, dfac.FacilityKey))
src = cd.assign(FacilityKey=cd.Facility.map(lambda f: fac_key[m2.FacilityPseudonym[f]]), MonthDate=cd.Month_Num.map(lambda m: f'2026-{m:02d}-01'))
mm = src.merge(rep, on=['FacilityKey', 'MonthDate'])
test('S4', 'Anonymization', 'Facility-month reporting flags identical to source after pseudonymisation (540 rows)',
     len(mm) == 540 and (mm.Reported_Flag == mm.Reported).all() and (mm.Expected_Flag == mm.Expected).all())

# ---------------------------------------------------------------- integrity / reconciliation
test('I1', 'Integrity', 'No duplicate facility-month records', not rep.duplicated(['FacilityKey', 'MonthDate']).any())
test('I2', 'Integrity', 'No duplicate facility-month-indicator observations', not svc.duplicated(['FacilityKey', 'MonthDate', 'IndicatorKey']).any())
test('I3', 'Integrity', 'Service fact rows = 540 facility-months × 27 indicators', len(svc) == 540 * 27, f'{len(svc)} rows')
test('I4', 'Integrity', 'No negative values', (svc.Value.dropna() >= 0).all() and (mort.Deaths >= 0).all())
test('I5', 'Integrity', 'All dates are valid month starts within Jan–Sep 2026',
     svc.MonthDate.isin([f'2026-{m:02d}-01' for m in range(1, 10)]).all() and rep.MonthDate.nunique() == 9)
test('I6', 'Integrity', 'Every foreign key resolves (facility, adopter, zone, indicator)',
     svc.FacilityKey.isin(dfac.FacilityKey).all() and svc.IndicatorKey.isin(dind.IndicatorKey).all()
     and dfac.AdopterKey.isin(dad.AdopterKey).all() and dfac.ZoneKey.isin(dgeo.ZoneKey).all() and mort.IndicatorKey.isin(dind.IndicatorKey).all())
code_src = {'GEN_ATT': 'General attendance', 'OPD_ATT': 'OPD attendance', 'ANC_TOT': 'Total ANC visits', 'ANC1': 'ANC 1', 'ANC4': 'ANC 4', 'ANC8': '8th ANC visit',
            'IPT1': 'IPT1', 'IPT2': 'IPT2', 'IPT3': 'IPT3', 'SBA_DEL': 'Deliveries by skilled birth attendant', 'IMM_FIC': 'Fully immunized children <1 year',
            'IMM_ALT': 'Children 0-9 months fully immunized (alt)', 'FP_COUN': 'FP counselled', 'FP_ACC': 'FP acceptors', 'FP_MCON': 'FP method: Male condoms',
            'FP_FCON': 'FP method: Female condoms', 'FP_PILL': 'FP method: Pills', 'FP_INJ': 'FP method: Injectables', 'FP_IMP': 'FP method: Implants',
            'FP_IUD': 'FP method: IUD', 'MAL_U5_T': 'U5 malaria tested', 'MAL_U5_P': 'U5 malaria positive', 'MAL_U5_R': 'U5 malaria treated',
            'MAL_AD_T': 'Adult malaria tested', 'MAL_AD_P': 'Adult malaria positive', 'MAL_AD_R': 'Adult malaria treated', 'OUTREACH': 'Outreaches conducted',
            'DTH_U5': 'Total U5 mortality', 'DTH_MAT': 'Maternal mortality', 'DTH_NEO': 'Neonatal mortality', 'DTH_INF': 'Infant mortality', 'DTH_ALL': 'All-category deaths'}
svc['Code'] = svc.IndicatorKey.map(dict(zip(dind.IndicatorKey, dind.IndicatorCode)))
mort['Code'] = mort.IndicatorKey.map(dict(zip(dind.IndicatorKey, dind.IndicatorCode)))
bad = []
for c, s in code_src.items():
    for mth in range(1, 10):
        md = f'2026-{mth:02d}-01'
        v_src = float(cd[cd.Month_Num == mth][s].sum())
        v_new = float((svc if not c.startswith('DTH') else mort.rename(columns={'Deaths': 'Value'}))
                      .query('Code == @c and MonthDate == @md').Value.sum())
        if abs(v_src - v_new) > 1e-9: bad.append((c, mth, v_src, v_new))
test('R1', 'Reconciliation', 'Indicator × month totals equal the validated source (Clean_Data) for all 32 indicators × 9 months (288 checks)', not bad, f'{len(bad)} differences' + (f': {bad[:3]}' if bad else ''))
# Monthly_Indicator_Table Jan–Sep column (N) vs anonymized totals
labels = mit[0].astype(str).str.strip(); jan_sep_col = 13
diffs = []
for c, s in code_src.items():
    row = mit[labels == s]
    if row.empty: continue
    v_tab = float(row.iloc[0, jan_sep_col])
    v_new = float(svc[svc.Code == c].Value.sum()) if not c.startswith('DTH') else float(mort[mort.Code == c].Deaths.sum())
    if abs(v_tab - v_new) > 1e-9: diffs.append((c, v_tab, v_new))
test('R2', 'Reconciliation', "Jan–Sep totals equal the source workbook's Monthly_Indicator_Table (independent formula layer)", not diffs, f'{len(diffs)} differences')
z_src = cd.groupby('Geopolitical Zone')['General attendance'].sum()
z_new = svc[svc.Code == 'GEN_ATT'].merge(dfac, on='FacilityKey').merge(dgeo, on='ZoneKey').groupby('Zone').Value.sum()
supp_name = dgeo[dgeo.IsSuppressedGroup == 1].Zone.iloc[0]
test('R3', 'Reconciliation', 'Zone totals reconcile once the small-cell "Not disclosed" group is added back (general attendance)',
     abs(z_src.sum() - z_new.sum()) < 1e-9 and all(z_new[z] <= z_src[z] for z in z_src.index if z in z_new.index),
     f'disclosed zones + not-disclosed group = {z_new.sum():,.0f} vs source {z_src.sum():,.0f}')
test('R4', 'Reconciliation', 'Reports expected / received = 540 / 494 (source)', rep.Expected.sum() == cd.Expected_Flag.sum() == 540 and rep.Reported.sum() == cd.Reported_Flag.sum() == 494)

# ---------------------------------------------------------------- missing ≠ zero
no_rep_keys = set(map(tuple, rep[rep.Reported == 0][['FacilityKey', 'MonthDate']].values))
nr = svc[svc.apply(lambda r: (r.FacilityKey, r.MonthDate) in no_rep_keys, axis=1)]
test('M1', 'Missing data', 'Every value for a facility-month without a report is NULL (no zero imputation)', nr.Value.isna().all() and len(nr) == 46 * 27, f'{len(nr)} values')
fpm = svc[svc.Code.isin(['FP_MCON', 'FP_FCON', 'FP_PILL', 'FP_INJ', 'FP_IMP', 'FP_IUD']) & (svc.MonthDate < '2026-06-01')]
test('M2', 'Missing data', 'FP method fields Jan–May (not on the form) are NULL, not 0', fpm.Value.isna().all() and fpm.ValueStatus.isin(['Not captured on form', 'No report submitted']).all(), f'{len(fpm)} values; ' + str(fpm.ValueStatus.value_counts().to_dict()))
test('M3', 'Missing data', 'NULLs only where documented (no report / not captured)', svc[svc.Value.isna()].ValueStatus.isin(['No report submitted', 'Not captured on form']).all())

# ---------------------------------------------------------------- model assets
lint = json.load(open(os.path.join(ROOT, 'validation', 'dax_static_lint.json')))
test('D1', 'DAX', f"Static lint of {lint['measures']} measures: balanced brackets; every [measure], table and column reference resolves", not lint['lint_problems'], str(lint['lint_problems'][:3]))
ref = pd.read_csv(os.path.join(ROOT, 'validation', 'reference_values.csv'))
gv = lambda m, ctx='Overall (Jan–Sep 2026)', mem=None: float(ref[(ref.Measure == m) & (ref.Context == ctx) & ((ref.Member == mem) if mem else True)].ExpectedValue.iloc[0])
test('D2', 'DAX', 'Reference engine reproduces the validated workbook headline values (377,483 attendance; 91.5% reporting; Q3 −8.5% QoQ; 84.4% Q3 reporting)',
     gv('General Attendance') == 377483 and round(gv('Reporting Completeness %'), 3) == 0.915 and round(gv('General Attendance QoQ %', 'Quarter', 'Q3 2026'), 3) == -0.085
     and round(gv('Reporting Completeness %', 'Quarter', 'Q3 2026'), 3) == 0.844)
# ratio of sums vs average of ratios demonstration
w = svc[svc.Code.isin(['MAL_U5_P', 'MAL_U5_T'])].pivot_table(index=['FacilityKey', 'MonthDate'], columns='Code', values='Value')
w = w[w.MAL_U5_T > 0]; avg_ratio = (w.MAL_U5_P / w.MAL_U5_T).mean(); ros = w.MAL_U5_P.sum() / w.MAL_U5_T.sum()
test('D3', 'DAX', 'Ratios use ratio-of-sums (U5 positivity), not the mean of facility-month percentages', abs(gv('U5 Malaria Test Positivity %') - ros) < 1e-6,
     f'ratio of sums {ros:.4f} vs mean of facility-month ratios {avg_ratio:.4f}')
for q in ['FactServiceDelivery', 'FactFacilityReporting', 'FactMortality', 'FactDataQuality', 'DimFacility', 'DimAdopter', 'DimGeography', 'DimIndicator', 'DimDate', 'DataFolder']:
    pass
test('Q1', 'Power Query', 'Every M script types exactly the columns present in its CSV header', True, 'checked when scripts were generated (see powerquery/ALL_QUERIES.md); re-checked below')
import csv
okm = True
for p in glob.glob(os.path.join(ROOT, 'powerquery', 'Fact*.pq')) + glob.glob(os.path.join(ROOT, 'powerquery', 'Dim[!D]*.pq')):
    code = open(p).read(); f = re.search(r'data/(\S+\.csv)', code).group(1)
    hdr = next(csv.reader(open(os.path.join(ROOT, 'data', f)))); typed = re.findall(r'\{"([^"]+)", ', code)
    okm &= typed == hdr
R[-1]['outcome'] = 'PASS' if okm else 'FAIL'

json.dump(R, open(os.path.join(ROOT, 'validation', 'automated_checks.json'), 'w'), indent=2, ensure_ascii=False)
for r in R: print(r['outcome'], r['id'], r['test'], '|', r['detail'])
print(sum(r['outcome'] == 'PASS' for r in R), '/', len(R), 'passed')
