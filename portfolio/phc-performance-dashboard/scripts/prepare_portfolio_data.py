"""
Prepare the anonymized, analysis-ready dataset for the Power BI portfolio dashboard.

Input  : the confidential programme workbook (sheets Clean_Data and Trace_Long) – NOT included in this repository.
Outputs: anonymized CSV files in ../data and an internal identity mapping written ONLY to a private folder
         outside the repository (never commit it).

Usage:
    python prepare_portfolio_data.py --workbook <path/to/source.xlsx> --private-dir <path/outside/repo> [--out ../data]

Pseudonymisation:
  * Facilities -> "Facility 001" … "Facility 060". Order = a seeded random shuffle (seed read from
    <private-dir>/seed.txt), so the numbering carries no information about names, states or source order.
  * Adopters   -> "Adopter A" … in descending order of facility count (ties broken by the seeded shuffle).
  * No names, states, LGAs, wards, backend row numbers or free-text notes are written to the outputs.
"""
import argparse, os, random
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument('--workbook', required=True)
ap.add_argument('--private-dir', required=True)
ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
seed = int(open(os.path.join(args.private_dir, 'seed.txt')).read().strip())

cd = pd.read_excel(args.workbook, sheet_name='Clean_Data')
tl = pd.read_excel(args.workbook, sheet_name='Trace_Long')

# ---------------------------------------------------------------- indicator catalogue
SERVICE = [  # (code, source indicator label, display name, category, unit)
    ('GEN_ATT', 'General attendance', 'General attendance', 'Service utilisation', 'Service contacts'),
    ('OPD_ATT', 'OPD attendance', 'OPD attendance', 'Service utilisation', 'Visits'),
    ('ANC_TOT', 'Total ANC visits', 'ANC visits (all)', 'Maternal & newborn health', 'Visits'),
    ('ANC1', 'ANC 1', 'ANC first visits', 'Maternal & newborn health', 'Visits'),
    ('ANC4', 'ANC 4', 'ANC fourth visits', 'Maternal & newborn health', 'Visits'),
    ('ANC8', '8th ANC visit', 'ANC eighth visits', 'Maternal & newborn health', 'Visits'),
    ('IPT1', 'IPT1', 'IPTp dose 1', 'Maternal & newborn health', 'Doses given'),
    ('IPT2', 'IPT2', 'IPTp dose 2', 'Maternal & newborn health', 'Doses given'),
    ('IPT3', 'IPT3', 'IPTp dose 3', 'Maternal & newborn health', 'Doses given'),
    ('SBA_DEL', 'Deliveries by skilled birth attendant', 'Deliveries by skilled birth attendant', 'Maternal & newborn health', 'Deliveries'),
    ('IMM_FIC', 'Fully immunized children <1 year', 'Immunization doses, children <1 year (antigen total)', 'Immunization', 'Antigen doses'),
    ('IMM_ALT', 'Children 0-9 months fully immunized (alt)', 'Children 0–9 months fully immunized', 'Immunization', 'Children'),
    ('FP_COUN', 'FP counselled', 'FP clients counselled', 'Family planning', 'Clients'),
    ('FP_ACC', 'FP acceptors', 'FP acceptors', 'Family planning', 'Clients'),
    ('FP_MCON', 'FP method: Male condoms', 'FP method – male condoms', 'Family planning methods', 'Method acceptances'),
    ('FP_FCON', 'FP method: Female condoms', 'FP method – female condoms', 'Family planning methods', 'Method acceptances'),
    ('FP_PILL', 'FP method: Pills', 'FP method – pills', 'Family planning methods', 'Method acceptances'),
    ('FP_INJ', 'FP method: Injectables', 'FP method – injectables', 'Family planning methods', 'Method acceptances'),
    ('FP_IMP', 'FP method: Implants', 'FP method – implants', 'Family planning methods', 'Method acceptances'),
    ('FP_IUD', 'FP method: IUD', 'FP method – IUD', 'Family planning methods', 'Method acceptances'),
    ('MAL_U5_T', 'U5 malaria tested', 'Under-5 malaria tests', 'Malaria', 'Tests'),
    ('MAL_U5_P', 'U5 malaria positive', 'Under-5 malaria positive tests', 'Malaria', 'Positive tests'),
    ('MAL_U5_R', 'U5 malaria treated', 'Under-5 malaria treated', 'Malaria', 'Treatments'),
    ('MAL_AD_T', 'Adult malaria tested', 'Adult malaria tests', 'Malaria', 'Tests'),
    ('MAL_AD_P', 'Adult malaria positive', 'Adult malaria positive tests', 'Malaria', 'Positive tests'),
    ('MAL_AD_R', 'Adult malaria treated', 'Adult malaria treated', 'Malaria', 'Treatments'),
    ('OUTREACH', 'Outreaches conducted', 'Community outreaches conducted', 'Outreach', 'Outreach sessions'),
]
MORT = [('DTH_U5', 'Total U5 mortality', 'Under-5 deaths'), ('DTH_MAT', 'Maternal mortality', 'Maternal deaths'),
        ('DTH_NEO', 'Neonatal mortality', 'Neonatal deaths'), ('DTH_INF', 'Infant mortality', 'Infant deaths'),
        ('DTH_ALL', 'All-category deaths', 'All-category deaths (upper bound)')]
FP_METHOD_FIRST_MONTH = 6  # FP method fields were added to the reporting form in June 2026

# ---------------------------------------------------------------- pseudonyms
rng = random.Random(seed)
facilities = sorted(cd['Facility'].unique())
order = facilities[:]; rng.shuffle(order)
fac_id = {f: i + 1 for i, f in enumerate(order)}
fac_label = {f: f'Facility {i:03d}' for f, i in fac_id.items()}
fac_n = cd.groupby('Adopter')['Facility'].nunique()
adopters = sorted(fac_n.index, key=lambda a: (-fac_n[a], rng.random()))
ad_key = {a: i + 1 for i, a in enumerate(adopters)}
ad_label = {a: f'Adopter {chr(64 + i)}' for a, i in ad_key.items()}

ZONES = ['North Central', 'North East', 'North West', 'South East', 'South South', 'South West']
SUPPRESSED_ZONE = 'Not disclosed (small cell)'
fac_info = cd.groupby('Facility').agg(Adopter=('Adopter', 'first'), Zone=('Geopolitical Zone', 'first'))
cell = fac_info.groupby(['Adopter', 'Zone']).size()
def public_zone(row):
    # suppress the zone when an adopter has fewer than 3 facilities in that zone (single-facility cells)
    return SUPPRESSED_ZONE if cell[(row.Adopter, row.Zone)] < 3 else row.Zone
fac_info['PublicZone'] = fac_info.apply(public_zone, axis=1)
zone_key = {z: i + 1 for i, z in enumerate(ZONES + [SUPPRESSED_ZONE])}

# private mapping (never inside the repository)
priv = fac_info.reset_index().assign(FacilityPseudonym=lambda d: d.Facility.map(fac_label), AdopterPseudonym=lambda d: d.Adopter.map(ad_label))
assert not os.path.abspath(args.private_dir).startswith(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))), 'private dir must be outside the portfolio'
priv.to_csv(os.path.join(args.private_dir, 'INTERNAL_identity_mapping_DO_NOT_SHARE.csv'), index=False)

# ---------------------------------------------------------------- dimensions
pd.DataFrame([{'AdopterKey': k, 'Adopter': ad_label[a], 'FacilitiesInProgramme': int(fac_n[a])} for a, k in ad_key.items()]) \
    .sort_values('AdopterKey').to_csv(os.path.join(args.out, 'dim_adopter.csv'), index=False)
pd.DataFrame([{'ZoneKey': k, 'Zone': z, 'ZoneSort': k, 'IsSuppressedGroup': int(z == SUPPRESSED_ZONE)} for z, k in zone_key.items()]) \
    .to_csv(os.path.join(args.out, 'dim_geography.csv'), index=False)
dim_fac = pd.DataFrame([{'FacilityKey': fac_id[f], 'Facility': fac_label[f], 'AdopterKey': ad_key[r.Adopter], 'ZoneKey': zone_key[r.PublicZone]}
                        for f, r in fac_info.iterrows()]).sort_values('FacilityKey')
dim_fac.to_csv(os.path.join(args.out, 'dim_facility.csv'), index=False)
ind_rows = [{'IndicatorKey': i + 1, 'IndicatorCode': c, 'Indicator': d, 'ServiceCategory': cat, 'Unit': u, 'SortOrder': i + 1,
             'Additive': 1, 'FirstMonthCaptured': f'2026-{FP_METHOD_FIRST_MONTH:02d}-01' if c.startswith('FP_') and c not in ('FP_COUN', 'FP_ACC') else '2026-01-01'}
            for i, (c, s, d, cat, u) in enumerate(SERVICE)]
n0 = len(ind_rows)
ind_rows += [{'IndicatorKey': n0 + i + 1, 'IndicatorCode': c, 'Indicator': d, 'ServiceCategory': 'Mortality (national only)', 'Unit': 'Deaths',
              'SortOrder': n0 + i + 1, 'Additive': 1, 'FirstMonthCaptured': '2026-01-01'} for i, (c, s, d) in enumerate(MORT)]
dim_ind = pd.DataFrame(ind_rows); dim_ind.to_csv(os.path.join(args.out, 'dim_indicator.csv'), index=False)
ikey = dict(zip(dim_ind.IndicatorCode, dim_ind.IndicatorKey))

# ---------------------------------------------------------------- facts
def month_date(m): return f'2026-{int(m):02d}-01'
rep = cd[['Facility', 'Month_Num', 'Expected_Flag', 'Reported_Flag', 'Reporting_Status']].copy()
rep['FacilityKey'] = rep.Facility.map(fac_id); rep['MonthDate'] = rep.Month_Num.map(month_date)
rep = rep.rename(columns={'Expected_Flag': 'Expected', 'Reported_Flag': 'Reported', 'Reporting_Status': 'SourceStatus'})
STATUS = {'Reported': 'Reported', 'Resumed Reporting': 'Reported (resumed after gap)',
          'Non-Reporting – Recorded as 0': 'Not reported (source recorded 0 under non-response rule)',
          'Non-Reporting – Missing (not imputed)': 'Not reported (missing)'}
rep['ReportingStatus'] = rep.SourceStatus.map(STATUS)
assert rep.ReportingStatus.notna().all()
rep[['FacilityKey', 'MonthDate', 'Expected', 'Reported', 'ReportingStatus']].sort_values(['FacilityKey', 'MonthDate']) \
    .to_csv(os.path.join(args.out, 'fact_facility_reporting.csv'), index=False)

src2code = {s: c for c, s, *_ in SERVICE}
t = tl[tl.Indicator.isin(src2code)].copy()
def treat(r):
    """returns (value, status) – documented in docs/DATA_PREPARATION.md"""
    st = r.Value_Status
    if st.startswith('Non-Reporting'):
        return None, 'No report submitted'                                   # no submission -> missing, never zero
    if src2code[r.Indicator].startswith('FP_') and src2code[r.Indicator] not in ('FP_COUN', 'FP_ACC') and r.Month_Num < FP_METHOD_FIRST_MONTH:
        return None, 'Not captured on form'                                  # field did not exist yet
    if st.startswith('Reported – field blank'):
        return r.Value, 'Field blank in report (0 per source rule)'
    if st.startswith('Corrected'):
        return r.Value, 'Corrected upstream (documented)'
    if st.startswith('Reported Zero'):
        return r.Value, 'Reported zero'
    return r.Value, 'Reported'
vs = t.apply(treat, axis=1, result_type='expand'); t['V'] = vs[0]; t['ValueStatus'] = vs[1]
fact = pd.DataFrame({'FacilityKey': t.Facility.map(fac_id), 'MonthDate': t.Month_Num.map(month_date),
                     'IndicatorKey': t.Indicator.map(lambda s: ikey[src2code[s]]), 'Value': t.V, 'ValueStatus': t.ValueStatus})
fact = fact.sort_values(['FacilityKey', 'MonthDate', 'IndicatorKey'])
fact['Value'] = fact['Value'].astype('Int64')
fact.to_csv(os.path.join(args.out, 'fact_service_delivery.csv'), index=False)

# national monthly mortality (rare events: facility / zone / adopter detail is not published)
m = tl[tl.Indicator.isin([s for _, s, _ in MORT])]
m = m[~m.Value_Status.str.startswith('Non-Reporting')]
mort = m.groupby(['Month_Num', 'Indicator'])['Value'].sum().reset_index()
code_of = {s: c for c, s, _ in MORT}
mort = pd.DataFrame({'MonthDate': mort.Month_Num.map(month_date), 'IndicatorKey': mort.Indicator.map(lambda s: ikey[code_of[s]]),
                     'Deaths': mort.Value.astype(int)}).sort_values(['MonthDate', 'IndicatorKey'])
mort.to_csv(os.path.join(args.out, 'fact_mortality_national_month.csv'), index=False)

# ---------------------------------------------------------------- data-quality exceptions (facility-month grain)
w = fact.pivot_table(index=['FacilityKey', 'MonthDate'], columns='IndicatorKey', values='Value', aggfunc='first')
w.columns = [dim_ind.set_index('IndicatorKey').IndicatorCode[c] for c in w.columns]
w = w.astype('float')
CHECKS = [
    ('DQ01', 'Under-5 treated exceeds under-5 positive', 'Logical consistency', lambda d: d.MAL_U5_R > d.MAL_U5_P),
    ('DQ02', 'Adult treated exceeds adult positive', 'Logical consistency', lambda d: d.MAL_AD_R > d.MAL_AD_P),
    ('DQ03', 'Under-5 positive exceeds under-5 tested', 'Logical consistency', lambda d: d.MAL_U5_P > d.MAL_U5_T),
    ('DQ04', 'Adult positive exceeds adult tested', 'Logical consistency', lambda d: d.MAL_AD_P > d.MAL_AD_T),
    ('DQ05', 'FP acceptors exceed FP clients counselled', 'Logical consistency', lambda d: d.FP_ACC > d.FP_COUN),
    ('DQ06', 'Sum of FP methods exceeds FP acceptors', 'Definition (multi-method counting)',
     lambda d: d[['FP_MCON', 'FP_FCON', 'FP_PILL', 'FP_INJ', 'FP_IMP', 'FP_IUD']].sum(axis=1, min_count=1) > d.FP_ACC),
    ('DQ07', 'ANC first visits exceed all ANC visits', 'Logical consistency', lambda d: d.ANC1 > d.ANC_TOT),
    ('DQ08', 'ANC4 exceeds ANC1 in the same month (cross-sectional, not invalid)', 'Interpretation', lambda d: d.ANC4 > d.ANC1),
]
rows = []
for code, name, typ, fn in CHECKS:
    hit = fn(w).fillna(False)
    for (fk, md) in w.index[hit.values]:
        rows.append({'FacilityKey': fk, 'MonthDate': md, 'CheckCode': code, 'Check': name, 'CheckType': typ})
fb = fact[fact.ValueStatus.str.startswith('Field blank')].groupby(['FacilityKey', 'MonthDate']).size()
for (fk, md), n in fb.items():
    rows.append({'FacilityKey': fk, 'MonthDate': md, 'CheckCode': 'DQ09', 'Check': f'Report submitted with {n} indicator field(s) blank (recorded as 0)', 'CheckType': 'Completeness'})
for _, r in rep[rep.Reported == 0].iterrows():
    rows.append({'FacilityKey': r.FacilityKey, 'MonthDate': r.MonthDate, 'CheckCode': 'DQ10',
                 'Check': 'No report submitted (' + ('source recorded 0 under non-response rule' if 'recorded 0' in r.ReportingStatus else 'missing') + ')',
                 'CheckType': 'Reporting'})
for _, r in fact[fact.ValueStatus.str.startswith('Corrected')].iterrows():
    rows.append({'FacilityKey': r.FacilityKey, 'MonthDate': r.MonthDate, 'CheckCode': 'DQ11', 'Check': 'Value corrected upstream (implausible raw entry)', 'CheckType': 'Accuracy'})
dq = pd.DataFrame(rows).sort_values(['CheckCode', 'FacilityKey', 'MonthDate'])
dq.to_csv(os.path.join(args.out, 'fact_data_quality.csv'), index=False)

print('facilities', len(dim_fac), '| adopters', len(ad_key), '| service rows', len(fact), '| mortality rows', len(mort), '| DQ rows', len(dq))
print('suppressed-zone facilities', int((fac_info.PublicZone == SUPPRESSED_ZONE).sum()))
