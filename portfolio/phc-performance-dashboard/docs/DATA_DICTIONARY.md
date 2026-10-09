# Data dictionary

**Source:** routine monthly facility reports (primary healthcare programme), January–September 2026, 60 facilities, 4 adopters (implementing partners), 6 geopolitical zones. Extracted 7 Oct 2026; September reporting incomplete at extraction.
**Reporting frequency:** monthly, facility level. **Grain of the service fact:** facility × month × indicator.
**Aggregation rule for every count:** SUM over facility-months in the filter context – never averaged. Missing reports and fields not on the form are NULL and are excluded, never counted as zero.
**Targets / benchmarks:** none exist in the source; none were created.

## 1. Base indicators (counts)

| Code | Indicator | Category | Definition | Unit | Limitations |
|---|---|---|---|---|---|
| `GEN_ATT` | General attendance | Service utilisation | All patient contacts recorded by the facility in the month (general attendance register). | Service contacts | Contacts, not unique patients. June 2026 peak coincides with an immunization outreach campaign. |
| `OPD_ATT` | OPD attendance | Service utilisation | Outpatient department attendances recorded in the month. | Visits | – |
| `ANC_TOT` | ANC visits (all) | Maternal & newborn health | All antenatal care contacts in the month, any visit number. | Visits | – |
| `ANC1` | ANC first visits | Maternal & newborn health | Antenatal care first visits in the month. | Visits | 2 facility-months record more first visits than total ANC visits (DQ07). |
| `ANC4` | ANC fourth visits | Maternal & newborn health | Antenatal care fourth visits in the month. | Visits | ANC4 > ANC1 in 92 facility-months: same-month counts refer to different women (DQ08). |
| `ANC8` | ANC eighth visits | Maternal & newborn health | Antenatal care eighth visits in the month. | Visits | – |
| `IPT1` | IPTp dose 1 | Maternal & newborn health | Pregnant women given intermittent preventive treatment of malaria in pregnancy (IPTp), dose 1. | Doses given | – |
| `IPT2` | IPTp dose 2 | Maternal & newborn health | IPTp dose 2. | Doses given | – |
| `IPT3` | IPTp dose 3 | Maternal & newborn health | IPTp dose 3. | Doses given | – |
| `SBA_DEL` | Deliveries by skilled birth attendant | Maternal & newborn health | Deliveries recorded by the facility. The source form field is "number of deliveries" and the source workbook reports it as deliveries by a skilled birth attendant. | Deliveries | – |
| `IMM_FIC` | Immunization doses, children <1 year (antigen total) | Immunization | Source field "Total number of children immunized under 1 year": per the source methodology this is the SUM of antigen doses (BCG, Penta 1–3, Vitamin A 6m, MCV1). It is a dose count, NOT the number of fully immunized children. | Antigen doses | June 2026 doubles (outreach campaign). Not a coverage measure: no target-population denominator. |
| `IMM_ALT` | Children 0–9 months fully immunized | Immunization | Children 0–9 months recorded as fully immunized (alternative source field). | Children | – |
| `FP_COUN` | FP clients counselled | Family planning | Family planning clients counselled. | Clients | – |
| `FP_ACC` | FP acceptors | Family planning | Family planning acceptors (clients who accepted a method). | Clients | 5 facility-months with acceptors > counselled (DQ05). |
| `FP_MCON` | FP method – male condoms | Family planning methods | Male condom acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `FP_FCON` | FP method – female condoms | Family planning methods | Female condom acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `FP_PILL` | FP method – pills | Family planning methods | Oral pill acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `FP_INJ` | FP method – injectables | Family planning methods | Injectable acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `FP_IMP` | FP method – implants | Family planning methods | Implant acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `FP_IUD` | FP method – IUD | Family planning methods | IUD acceptances. | Method acceptances | Field added to the form in June 2026: Jan–May = not captured (blank). Method totals exceed acceptors in 132 facility-months (multi-method counting, DQ06). |
| `MAL_U5_T` | Under-5 malaria tests | Malaria | Malaria tests (RDT/microscopy) performed on children under 5. | Tests | – |
| `MAL_U5_P` | Under-5 malaria positive tests | Malaria | Positive malaria tests, children under 5. | Positive tests | 4 facility-months with positive > tested (DQ03). |
| `MAL_U5_R` | Under-5 malaria treated | Malaria | Children under 5 treated for malaria. | Treatments | 11 facility-months with treated > positive (DQ01). |
| `MAL_AD_T` | Adult malaria tests | Malaria | Malaria tests performed on adults. | Tests | – |
| `MAL_AD_P` | Adult malaria positive tests | Malaria | Positive malaria tests, adults. | Positive tests | 5 facility-months with positive > tested (DQ04). |
| `MAL_AD_R` | Adult malaria treated | Malaria | Adults treated for malaria. | Treatments | 16 facility-months with treated > positive (DQ02). |
| `OUTREACH` | Community outreaches conducted | Outreach | Community outreach sessions conducted by the facility. | Outreach sessions | – |
| `DTH_U5` | Under-5 deaths | Mortality (national only) | Under-5 deaths recorded at the facility. | Deaths | Rare events; published nationally by month only (no facility/zone/adopter detail). |
| `DTH_MAT` | Maternal deaths | Mortality (national only) | Maternal deaths recorded. | Deaths | Rare events; published nationally by month only (no facility/zone/adopter detail). |
| `DTH_NEO` | Neonatal deaths | Mortality (national only) | Neonatal deaths (first 28 days) recorded. | Deaths | Rare events; published nationally by month only (no facility/zone/adopter detail). |
| `DTH_INF` | Infant deaths | Mortality (national only) | Infant deaths recorded. | Deaths | Rare events; published nationally by month only (no facility/zone/adopter detail). |
| `DTH_ALL` | All-category deaths (upper bound) | Mortality (national only) | Derived: neonatal + infant + under-5 + maternal deaths. An upper bound – one death may be entered in more than one field. | Deaths | Rare events; published nationally by month only. |

## 2. Derived indicators (ratios)

Every ratio = Σ numerator ÷ Σ denominator over the facility-months in context (ratio of sums), via `DIVIDE()` so a zero or blank denominator returns blank. Facility percentages are never averaged.

| Indicator (measure) | Numerator | Denominator | Unit | Interpretation and limitations |
|---|---|---|---|---|
| U5 Malaria Test Positivity % | U5 positive tests | U5 tests | % | Share of tests that were positive – a facility test-positivity rate, not disease prevalence or incidence. |
| Adult Malaria Test Positivity % | Adult positive tests | Adult tests | % | As above. |
| Malaria Test Positivity % (All Ages) | U5 + adult positive | U5 + adult tests | % | As above. |
| U5 Treated per Positive % | U5 treated | U5 positive | % | Record-keeping ratio; can exceed 100% because treatment is sometimes recorded without a matching positive test (DQ01). Not a clinical treatment-success rate. |
| Adult Treated per Positive % | Adult treated | Adult positive | % | As above (DQ02). |
| FP Acceptors per Client Counselled % | FP acceptors | FP clients counselled | % | Service uptake among counselled clients in the same period – not population contraceptive prevalence. |
| ANC4 to ANC1 Ratio % | ANC4 visits | ANC1 visits (same period) | % | Cross-sectional continuation proxy. NOT ANC4 completion/coverage: the women counted at ANC4 are mostly not those counted at ANC1 in the same month. |
| ANC8 to ANC1 Ratio % | ANC8 visits | ANC1 visits | % | As above. |
| IPTp3 to IPTp1 Ratio % | IPTp3 | IPTp1 | % | Cross-sectional proxy for IPTp continuation. |
| OPD Share of General Attendance % | OPD visits | General attendance | % | Composition of contacts. |
| Reporting Completeness % | Facility reports received | Facility reports expected | % | Reporting performance only – not service coverage or programme effectiveness. |
| Indicator Value Completeness % | Values reported (incl. true zeros) | Indicator fields expected on the form for facility-months in context | % | Excludes fields not yet on the form (FP methods Jan–May). |
| General Attendance per Report | General attendance | Reports received | Contacts per report | Reporting-adjusted volume: removes the arithmetic effect of missing reports when comparing periods. |
| Deaths per 100 Reports | All-category deaths (upper bound) | Reports received | Deaths per 100 reports | Facility event rate, national only. Not a population mortality rate. |

## 3. Not calculable from this source (deliberately omitted)

- **Population coverage** of ANC, immunization, deliveries or family planning – no catchment/target-population denominators.
- **Target achievement** – no programme targets exist.
- **Unique beneficiaries** – data are aggregate counts of contacts; no person-level identifiers or deduplication.
- **Year-on-year change** – only 2026 is available.
- **Late reports / timeliness** – no submission timestamps or due dates in the source.
- **Disease incidence or prevalence** – routine facility counts have no population denominator.

## 4. Dimension attributes

| Table | Column | Description |
|---|---|---|
| DimFacility | Facility | Stable pseudonym `Facility 001`–`Facility 060` (seeded random order; carries no information about names or location). |
| DimAdopter | Adopter | Implementing partner pseudonym `Adopter A`–`D`, lettered by number of facilities. |
| DimAdopter | FacilitiesInProgramme | Facilities supported by the adopter (49 / 5 / 4 / 2). |
| DimGeography | Zone | Nigerian geopolitical zone, or `Not disclosed (small cell)` for the 2 facilities whose adopter has <3 facilities in their zone. |
| DimIndicator | ServiceCategory | Grouping used by the Service-category slicer. |
| DimIndicator | FirstMonthCaptured | First month the field existed on the reporting form. |
| FactServiceDelivery | ValueStatus | Reported · Reported zero · Field blank in report (0 per source rule) · Corrected upstream (documented) · No report submitted (NULL) · Not captured on form (NULL). |
| FactFacilityReporting | ReportingStatus | Reported · Reported (resumed after gap) · Not reported (missing) · Not reported (source recorded 0 under non-response rule). |
| FactDataQuality | CheckCode / Check / CheckType | Data-quality exception at facility-month grain (DQ01–DQ11, see DATA_PREPARATION.md). |
