# Data preparation, anonymization and validation log

Pipeline: `scripts/prepare_portfolio_data.py` (raw workbook → anonymized CSVs) → `scripts/build_model_assets.py` (DAX, reference values) → `scripts/validate_portfolio.py` (automated QA). The raw workbook, the identity mapping and the pseudonym seed are kept in a private folder **outside** this repository. They are never committed, and `.gitignore` blocks them.

## 1. Source used

| Item | Detail |
|---|---|
| Source | Programme Excel workbook (Q3 2026 dashboard), sheets `Clean_Data` (540 facility-month rows × 51 columns) and `Trace_Long` (17,280 facility × month × indicator rows with a per-value status). Not published. |
| Coverage | 60 facilities × 9 months (January–September 2026) = 540 expected facility-months, 4 adopters, 6 geopolitical zones, 32 indicators |
| Upstream cleaning already in the source | Adopter/facility/zone spelling standardised (documented in the source's Methodology sheet); blank fields inside submitted reports set to 0 ("reference rule"); one implausible raw ANC4 entry corrected. |
| Original files | Not modified. All outputs are new files. |

## 2. Anonymization rules

| Rule | Implementation |
|---|---|
| Facility names | Replaced by `Facility 001`–`Facility 060`. Numbers come from a seeded random shuffle, so they reveal nothing about name, state or source order. The same facility keeps the same key in every table and month (tests S1, S3, S4). |
| Adopter (implementing partner) names | Replaced by `Adopter A`–`Adopter D` in descending order of facility count (49, 5, 4, 2). |
| Removed columns | State, LGA, ward, facility/adopter/zone "as reported", backend row numbers, free-text context notes, year column. |
| Geography | Only the geopolitical zone (6 broad regions) is kept. Where an adopter has fewer than 3 facilities in a zone (2 facilities, each the only one of its adopter in its zone), the zone is published as **Not disclosed (small cell)**. National totals are unaffected; zone totals exclude these 2 facilities (test R3). |
| Mortality | Deaths are rare events with very small counts, so they are published **only as national monthly totals** (`fact_mortality_national_month.csv`). The DAX mortality measures return blank whenever a facility, adopter or zone filter is active. |
| Identity lookup | Written only to the private folder (`INTERNAL_identity_mapping_DO_NOT_SHARE.csv`). Not included in any deliverable. |
| Residual risk | Programme insiders could guess adopter identities from facility counts or zone patterns (e.g. one adopter's facilities are all in one zone, and its distinctive non-response pattern is visible). **Obtain the data owner's clearance before publishing.** Consider merging adopters B–D into "Other adopters" if clearance is not given. |

## 3. Treatment of values (missing ≠ zero)

| Situation (source status) | Values in this model | Count | Rationale |
|---|---|---|---|
| Reported | as reported | 10,575 | – |
| Reported zero | 0 | 1,033 | True zero in a submitted report. |
| Field blank in a submitted report | 0 (source rule), flagged `Field blank in report` | 1 | Ambiguous; source value preserved, flagged for transparency. |
| Corrected upstream | corrected value, flagged | 1 | One raw ANC4 entry was implausible and corrected in the source. The corrected value is kept. |
| No report submitted – source left blank | **NULL** | 14 facility-months (378 values) | No submission, so no service data. |
| No report submitted – source recorded 0 under its non-response rule | **NULL** (changed from 0) | 32 facility-months (864 values) | These months belong to one adopter that stopped reporting. The source's zeros are not evidence of zero service. Totals are unchanged because the source value was 0. |
| FP method fields, January–May | **NULL** (changed from 0) | 1,728 values | The six method fields were added to the form in June 2026. Zeros would imply no uptake. |

Effect on reconciliation: none on any total (every value changed to NULL was 0). Effect on interpretation: averages, per-report values, positivity and other ratios are no longer diluted by false zeros.

## 4. Validation checks on the data

| Check | Result | Treatment |
|---|---|---|
| Duplicate facility-month records | 0 | – |
| Duplicate facility-month-indicator observations | 0 | – |
| Missing reporting periods | none: every facility has 9 months of reporting records | – |
| Invalid dates | none: all values are month starts January–September 2026 | – |
| Inconsistent facility / adopter identifiers | resolved upstream (spelling variants merged; two facility-months whose adopter label disagreed with the facility's other months were reassigned in the source) | documented, kept |
| Negative values | 0 | – |
| Under-5 treated > under-5 positive (DQ01) | 11 facility-months | kept; flagged; ratio labelled "treated per positive", not a treatment-success rate |
| Adult treated > adult positive (DQ02) | 16 facility-months | as above |
| Positive > tested, U5 / adult (DQ03 / DQ04) | 4 / 5 facility-months | kept; flagged |
| FP acceptors > clients counselled (DQ05) | 5 facility-months | kept; flagged |
| Sum of FP methods > FP acceptors (DQ06) | 132 facility-months | definitional (a client can accept more than one method); methods are shown as "acceptances" |
| ANC first visits > all ANC visits (DQ07) | 2 facility-months | kept; flagged |
| ANC4 > ANC1 in the same month (DQ08) | 92 facility-months | not an error: different women. ANC4/ANC1 is presented only as a cross-sectional ratio, never as completion. |
| Fields blank inside submitted reports (DQ09) | 1 | flagged |
| No report submitted (DQ10) | 46 facility-months (14 missing + 32 recorded-as-0 non-response) | NULL values; reporting completeness 91.5% overall |
| Upstream correction (DQ11) | 1 value | flagged |
| Source totals vs anonymized totals | 288 indicator × month checks plus Jan–Sep totals against an independent formula layer: 0 differences | see validation report |
| Targets | none in the source | no target or achievement measures created |

No observation was deleted. All exceptions are kept and listed in `fact_data_quality.csv`, so the dashboard's data-quality page can show them.

## 5. Known limitations

1. **September 2026 is partially reported** (43 of 60 facilities at extraction), so Q3 totals understate activity. Use *General Attendance per Report* or reporting completeness when comparing Q3 with earlier quarters.
2. **June 2026 spike**: immunization doses and general attendance roughly double, coinciding with an immunization outreach campaign. Q2 is therefore inflated as a comparator.
3. **One adopter (5 facilities) stopped reporting progressively from February** and none of its facilities reported from June. Its totals reflect missing reports, not confirmed absence of services.
4. Counts are **service contacts**, not unique people. No deduplication is possible.
5. "Immunization doses <1 year" is a **dose sum**, not fully immunized children.
6. ANC and IPTp continuation ratios are **cross-sectional**, not cohort-based.
7. All-category deaths is an **upper bound**, because one death can appear in several fields.
8. No population denominators, so no coverage, incidence or prevalence.
