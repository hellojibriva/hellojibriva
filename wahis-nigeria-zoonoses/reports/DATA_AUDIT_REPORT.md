# DATA AUDIT REPORT

**Study:** Mapping the Temporal and Geographic Patterns of Zoonotic Animal Diseases in Nigeria: A One Health Surveillance Analysis
**Source dataset:** `Quantitative_data_20260905.csv` (WOAH WAHIS quantitative extract, Nigeria)
**MD5:** `d6ebeda431ba0319bc07649c7e954153`
**Audit date:** 2026-09-05
**Status:** Phase 1–10 complete. **Awaiting approval before any manuscript writing.**

> **One issue requires a decision before the analysis is finalised.** The
> trypanosomosis series cannot cover 2006–2023 as the protocol assumes; its
> structural observation window is **2008–2021**. See [§15.1](#151-stop-issue-the-research-question-cannot-be-answered-as-written-for-trypanosomosis)
> and the recommendation in [§16](#16-proposed-final-analysis-plan).

---

## 1. Dataset overview

| Property | Value |
|---|---|
| Filename | `Quantitative_data_20260905.csv` |
| Encoding | UTF-8 with BOM |
| Rows | 1,112 (excluding header) |
| Columns | 19 |
| Country | Nigeria only (1,112/1,112) |
| World region | Africa only |
| Year range in file | 2005–2026 |
| Time granularity | **Semester** (`Jan-Jun YYYY` / `Jul-Dec YYYY`) — 40 distinct semesters |
| Diseases | Exactly the three target diseases; **no other disease is present, so no substitution was possible or made** |
| Administrative Division values | 44 distinct labels |
| Species values | 13 named + blank |
| Animal categories | `Both animal categories`, `Domestic`, `Wild` |
| Rows in study period (2006–2023) | 947 |
| Rows excluded by period | 165 (2005: 4 rows; 2024–2026: 161 rows) |

**Disease row counts (whole file):**

| WAHIS disease label | Short name | Rows | Years present |
|---|---|---|---|
| `Rabies virus (Inf. with)` | Rabies | 566 | 2005–2025 |
| `High pathogenicity avian influenza viruses (Inf. with) (poultry)` | HPAI | 436 | 2006–2026 |
| `Trypanosomosis (tsetse-transmitted) (-2021)` | Trypanosomosis | 110 | 2008–2021 |

Note that the extract runs to 2026 and therefore contains 161 rows *after* the
protocol's study window. They are retained in the annotated master dataset and
excluded from analysis, so the window can be widened later without re-extracting.

---

## 2. Variables and meanings

| Column | Meaning as used in WAHIS | Role in this study |
|---|---|---|
| `Year` | Calendar year of the six-monthly report | Analytical time variable |
| `Semester` | `Jan-Jun` / `Jul-Dec` reporting period | Sub-annual grain; defines the reporting block |
| `World region`, `Country` | Constant (Africa / Nigeria) | Not analytical |
| `Administrative Division` | ADM1 state/FCT, **or** the country name, **or** (2026 only) an ADM2 LGA | Geographic variable; requires levelling (§4) |
| `Disease` | WOAH-listed disease name **including validity suffix** | Stratifier; the `(-2021)` suffix is itself information |
| `Serotype/Subtype/Genotype` | Virus subtype (`H5N1`, `RABV`, …); may be a `;`-joined list | Splits reporting blocks; descriptive only |
| `Animal Category` | `Domestic` / `Wild` / `Both animal categories` | **Not** a reliable row-type marker (§7) |
| `Event_id`, `Outbreak_id` | WAHIS event / outbreak identifiers | **Effectively empty — unusable** (§3) |
| `Species` | Host species of the detail record; **blank on block header rows** | **The definitive row-type marker** (§7) |
| `Measuring units` | `Animal` on detail rows, `-` on header rows | Confirms row type |
| `New outbreaks` | Count of NEW outbreaks notified in that semester | **PRIMARY OUTCOME** |
| `Susceptible` | Animals at risk in affected epidemiological units | Secondary (denominator-like) |
| `Cases` | Animals meeting the case definition | Secondary |
| `Killed and disposed of` | Animals culled and destroyed | **Control-measure indicator, not disease impact** |
| `Slaughtered` | Animals slaughtered for consumption/salvage | Control measure; almost always 0 |
| `Deaths` | Animals that died of the disease | Secondary |
| `Vaccinated` | Animals vaccinated in response | Response indicator |

### Identifier fields are unusable

| Field | Populated | Distinct values |
|---|---|---|
| `Event_id` | 6 / 1,112 (0.5%) | 1 (`3533`) |
| `Outbreak_id` | 4 / 1,112 (0.4%) | 4 |

All six populated rows fall in **Jan-Jun 2026**. Event and outbreak linkage
therefore **cannot** be reconstructed from identifiers for any study-period
record; it must be inferred from the reporting-block key (§7).

---

## 3. Disease verification

All three protocol diseases are present under their exact expected labels and
**nothing else is**. The extract contains no near-miss labels (no generic
"Avian influenza", no "Trypanosoma", no "Rabies (Inf. with rabies virus)"), so
there is no risk of accidental substitution.

**Subtype/genotype composition (outbreak rows, study period):**

| Disease | Subtype values |
|---|---|
| Rabies | `RABV` (97 blocks), blank (89), `not typed` (13), `RABV;not typed` (1) |
| HPAI | `H5N1` (191), `H5N8` (4), `H5 (N untyped)` (1), `H5N1;H5N8` (1) |
| Trypanosomosis | blank (53) |

The `;`-joined values (`RABV;not typed`, `H5N1;H5N8`) show that the extract
collapses multiple outbreaks with different typing results into one row, which
is a further reason not to treat any single row as one outbreak.

**Host species (detail rows, study period):**

| Disease | Species |
|---|---|
| Rabies | Dogs (199), Cats (15), Cattle (10), Goats (3), Sheep (3), Swine (2), and 5 single records (Cercopithecidae, Crab-eating macaque, Equidae, Lion, Rabbits) |
| HPAI | Birds (202), Wildlife unspecified (1) |
| Trypanosomosis | Cattle (47), Dogs (3), Goats (3), Sheep (3), Swine (1) |

Only **4 rows in the entire study period are `Wild`** (1 HPAI, 3 rabies). Wild-
animal surveillance is essentially absent from this dataset — an important
limitation for a One Health framing.

---

## 4. Geographic structure

The `Administrative Division` field mixes **three geographic levels**:

| Level | n labels | n rows | Detail |
|---|---|---|---|
| ADM1 (state / FCT) | 38 labels → 37 units | 1,101 | All 36 states + FCT are represented; `Nasarawa` appears under two spellings |
| National | 1 (`Nigeria`) | 6 | 2005 (4 rows), 2014 (2 rows) |
| ADM2 (LGA) | 5 | 5 | Batagarawa, Gwale, Jos North, Toro, Ungogo — **all in Jan-Jun 2026 only** |

### 4.1 National records

`Nigeria` rows are **not national totals that aggregate the state rows.** They
have exactly the same header + detail block structure as a state record; they
are country-level reports in which no state was specified. Inside the study
period there is only **one** such outbreak record (2014, HPAI, 1 outbreak) plus
its animal detail row.

Decision: retained for the national annual series (Phase 7), excluded from all
state-level rankings and maps (Phases 8–9), never added to any state's total.
Because there is only one such record, this choice moves the national HPAI total
by 1 outbreak (1,232 → 1,231) and moves no state.

### 4.2 Sub-state (LGA) records

Batagarawa (Katsina), Gwale and Ungogo (Kano), Jos North (Plateau) and Toro
(Bauchi) are Local Government Areas. They appear **only** in Jan-Jun 2026, i.e.
entirely outside the study period, alongside the new one-row-per-outbreak export
format. They are **flagged, not rolled up** to their parent states: aggregating
them upward would silently mix two geographic grains. A filter is nonetheless
present in the pipeline so that widening the study period cannot reintroduce the
problem unnoticed.

### 4.3 The one location recode: `Nassarawa` → `Nasarawa`

This is the only name change applied anywhere, and the dataset itself justifies
it:

| Evidence | Finding |
|---|---|
| Co-occurrence | The two spellings appear in **zero** shared year × semester × disease strata |
| `Nasarawa` years | 2006, 2007, 2008, 2009, 2015, 2016, 2017, 2018 |
| `Nassarawa` years | 2021, 2022 only |
| Grain | Both carry the identical ADM1-level header + detail block structure |

The year ranges are disjoint either side of the 2021 WAHIS platform relaunch,
which is when the label changed. (A `Nassarawa` LGA does exist in Kano State,
but a Kano LGA would not carry state-grain blocks nor replace the Nasarawa State
series exactly when it stops.) A **sensitivity analysis withholding the recode is
reported** in `outputs/logs/03_descriptive.log`: it changes Nasarawa's own totals
only, changes no disease total, no annual total, and no state ranking outside
Nasarawa itself.

Full location table with per-label decisions: `data/processed/location_standardisation.csv`.

---

## 5. Missingness

### 5.1 The `-` sentinel

The seven count columns contain **zero true nulls and zero empty strings**.
Every non-numeric entry is the literal sentinel `-`.

| Variable | `-` | % `-` | blank/null | `0` | positive |
|---|---|---|---|---|---|
| New outbreaks | 582 | 52.3% | 0 | **0** | 530 |
| Susceptible | 576 | 51.8% | 0 | 0 | 536 |
| Cases | 573 | 51.5% | 0 | 1 | 538 |
| Killed and disposed of | 575 | 51.7% | 0 | 164 | 373 |
| Slaughtered | 560 | 50.4% | 0 | 533 | 19 |
| Deaths | 552 | 49.6% | 0 | 162 | 398 |
| Vaccinated | 670 | 60.3% | 0 | 415 | 27 |

**`-` and `0` are demonstrably different encodings and are kept different.**
The decisive evidence: `New outbreaks` **never takes the value 0 anywhere in the
file**. If `-` meant zero, the column would contain zeros; it does not. Meanwhile
`Killed and disposed of`, `Slaughtered`, `Deaths` and `Vaccinated` all carry
explicit `0` values *alongside* `-` values, which is only coherent if `0` means
"reported as none" and `-` means "not reported". `-` is therefore parsed to `NaN`
throughout and **never imputed as zero**.

### 5.2 Missingness is structural, not random

Roughly half of every count column is `-` because the file interleaves two
different kinds of row (§7). Within row type the picture is completely different:

**Outbreak (header) rows, n = 524:** `New outbreaks` 0% missing; all six animal
count columns 100% missing.

**Animal (detail) rows, n = 588:** `New outbreaks` 99.0% missing (the 1% are the
six 2026 rows); animal counts 2–25% missing:

| Variable | % `-` on detail rows |
|---|---|
| Susceptible | 2.0% |
| Cases | 2.6% |
| Deaths | 6.1% |
| Killed and disposed of | 8.5% |
| Slaughtered | 13.4% |
| Vaccinated | 25.2% |

So the apparent ~50% missingness in the raw file is an artefact of the row
structure. Genuine item non-response is modest for `Susceptible`, `Cases` and
`Deaths`, and material for `Vaccinated`.

**18 detail rows (study period) carry no count at all** — every one of the six
animal columns is `-`. They are retained and flagged
(`all_counts_missing = True`), because they still record that a given species was
involved in a given event. They are not dropped and not zero-filled.

### 5.3 Internal consistency

| Check | Comparable rows | Violations | % |
|---|---|---|---|
| Cases > Susceptible | 508 | 4 | 0.8% |
| Deaths > Cases | 532 | 5 | 0.9% |
| Deaths > Susceptible | 529 | 4 | 0.8% |
| **Killed & disposed of > Cases** | 530 | **65** | **12.3%** |
| Killed & disposed of > Susceptible | 508 | 1 | 0.2% |

The 12.3% figure is **expected and not an error**: culling removes healthy
in-contact birds. It confirms that `Killed and disposed of` measures the control
response, not the disease. The ~1% logical violations on the other checks are
genuine source-data inconsistencies; they are flagged and retained, not silently
corrected.

---

## 6. Duplicate / event structure

| Duplication type | Count | Interpretation |
|---|---|---|
| **Exact duplicate rows** (all 19 columns) | **0** | The extract contains no literal duplicates |
| Repeated Disease × Location × Year | Common | Almost always the **two semesters** of the year, which are genuinely different reports |
| Repeated Disease × Location × Year × Semester | 539 blocks total | Multiple rows per block by design (§7) |
| Multiple rows for different species / animal categories in one block | 44 blocks have ≥2 detail rows (39 have 2; 5 have 3) | Species breakdown of the **same** outbreaks — must not be counted as extra outbreaks |
| Two blocks split only by virus subtype | 2 strata | Bauchi Jul-Dec 2012 rabies (`not typed` 2 + `RABV;not typed` 2); Kano Jan-Jun 2017 HPAI (`H5N1` 1 + `H5N8` 1) |
| Blocks with animal data but **no** outbreak row | 15 file-wide, **7 in study period** | Follow-up reporting on previously notified events with no new outbreak that semester |

**No block anywhere in the file carries two header rows.** The outbreak count is
therefore never repeated within a block.

The two subtype-split strata deserve a note. In Bauchi Jul-Dec 2012, the same
state-semester carries two rabies blocks with 2 outbreaks each. Because
`RABV;not typed` is itself a joined label, we cannot rule out that these two
blocks partly describe the same underlying events. This affects at most 4
outbreaks nationally (0.4% of the rabies total) and is documented rather than
adjusted.

The 7 study-period header-less blocks (Bauchi 2013 rabies; Kano 2016, Rivers
2017 ×2, Bauchi 2017, Sokoto 2019 HPAI; Gombe 2023 rabies) are **not** imputed as
`New outbreaks = 0` and **not** dropped.

---

## 7. WAHIS row-structure findings

**This is the central structural finding of the audit.**

The file is not one row per outbreak. It is a **block** structure:

> **Reporting block = Year × Semester × Administrative Division × Disease × Serotype**

Each block contains:

* exactly **one header row** — `Species` is **blank**, `Measuring units` is `-`,
  it carries the block's `New outbreaks` count, and **all six animal count
  columns are `-`**; and
* **one or more detail rows** — `Species` is populated, `Measuring units` is
  `Animal`, `New outbreaks` is `-`, and the animal counts are populated.

The separation is perfect and verifiable:

| | `New outbreaks` populated | `New outbreaks` = `-` |
|---|---|---|
| **Species blank** (n=524) | 524 | 0 |
| **Species populated** (n=588) | 6 | 582 |

| | any animal count populated | all animal counts `-` |
|---|---|---|
| **`New outbreaks` populated** (n=530) | 6 | 524 |
| **`New outbreaks` = `-`** (n=582) | 564 | 18 |

`Measuring units` cross-tabulates perfectly with the blank-Species rule
(524 `-` ↔ 524 blank; 588 `Animal` ↔ 588 populated).

**All six exceptions fall in Jan-Jun 2026** — the post-relaunch export format,
where one row is one outbreak, `Event_id`/`Outbreak_id` are populated, and the
location is an LGA. **None falls inside the study period.**

### Worked example (Bauchi, Jul-Dec 2012, rabies)

| Serotype | Animal Category | Species | Row type | New outbreaks | Susceptible | Cases | Deaths |
|---|---|---|---|---|---|---|---|
| not typed | Both animal categories | *(blank)* | header | **2** | – | – | – |
| not typed | Domestic | Dogs | detail | – | 1575 | 1575 | 78 |
| not typed | Domestic | Cattle | detail | – | – | – | – |
| RABV;not typed | Both animal categories | *(blank)* | header | **2** | – | – | – |
| RABV;not typed | Domestic | Cattle | detail | – | 31 | 6 | 2 |
| RABV;not typed | Domestic | Dogs | detail | – | – | 1 | 0 |

The 4 outbreaks sit only on the two header rows; the four species rows carry
animal counts. This is exactly the pattern the protocol asked us to find: *an
outbreak count on one row, animal-level case/death information on another.*

### `Animal Category` is NOT the row-type marker

Header rows are labelled `Both animal categories` up to 2019, but from 2020 a
`Domestic`-labelled header appears, and from 2024 it is the only form:

| Header label | 2005–2019 | 2020 | 2021 | 2022 | 2023 | 2024–2025 |
|---|---|---|---|---|---|---|
| `Both animal categories` | all | 16 | 22 | 28 | 23 | 0 |
| `Domestic` | 0 | 11 | 44 | 31 | 9 | all |

Any pipeline that identified header rows by `Animal Category == "Both animal
categories"` would silently drop 95 outbreak records in 2020–2023 — precisely the
years with the heaviest rabies reporting. **Row type must be determined by the
blank `Species` field.**

---

## 8. Recommended analytical unit

**Analytical unit: the reporting block header, i.e. one
Year × Semester × Administrative Division × Disease × Serotype record.**

Rationale:

1. It is the unit at which WAHIS actually reports `New outbreaks`.
2. It is uniquely identified — no block has two headers, and there are no exact
   duplicate rows.
3. It is the finest grain at which outbreak counts can be recovered, since
   `Event_id` and `Outbreak_id` are unusable.
4. It cleanly separates the outbreak signal from the animal-count signal.

**Aggregation rule for the primary outcome:** sum `New outbreaks` over header
rows only, after filtering to the required year/geography stratum. Semesters are
summed to years (each semester reports *new* outbreaks in that semester, so the
two are additive). Do **not** sum across serotypes and then also across
"Both animal categories"/"Domestic" labels as if they were separate strata — the
serotype split is the only legitimate within-stratum split.

**Do not** use "number of rows" as a proxy for outbreak count. Rows-per-block
varies from 1 to 4 for reasons (species breakdown, subtype splits) that have
nothing to do with outbreak frequency.

---

## 9. Recommended primary and secondary indicators

### PRIMARY — Reported new outbreaks ✅ RECOMMENDED

| Question | Answer |
|---|---|
| What it measures | Count of new outbreaks **notified to WAHIS** in a semester for a disease in a location |
| Unit / denominator | Outbreaks per state-semester. **No population denominator exists in this dataset** |
| Comparable across diseases? | **Partly.** The unit is the same, but detection pathways differ hugely (commercial poultry sector vs. dog-bite presentation vs. herd screening). Comparable as *reporting activity*, not as burden |
| Should it be summed? | **Yes** — over header rows only, across semesters, states and subtypes |
| Analyse separately by disease? | **Yes**, always; a combined total is presented only as context |
| Major limitations | Reflects reporting effort as much as disease occurrence; a year with no report is not a year with no disease; the definition of an "outbreak" (epidemiological unit) differs between a commercial poultry farm and a village dog |

### SECONDARY — assessed one by one

| Indicator | Verdict | Reasoning |
|---|---|---|
| **Deaths** | ✅ Use, **per disease only** | 6.1% missing on detail rows; clear meaning. But HPAI deaths are counted in poultry flocks (1.23 M) and rabies deaths in individual animals (618) — **never rank these against each other** |
| **Cases** | ✅ Use, **per disease only** | 2.6% missing. Same non-comparability. 41 HPAI detail rows lack `Cases` despite reporting `Susceptible` |
| **Susceptible** | ⚠️ Use with care | It is *animals at risk in affected units*, **not** a population denominator. It cannot be used to compute incidence or prevalence |
| **Killed and disposed of** | ⚠️ Reframe | A **control-response** indicator. Exceeds `Cases` on 12.3% of comparable rows because healthy in-contact birds are culled. Report as "culling response", never as disease impact |
| **Vaccinated** | ⚠️ Descriptive only | 25.2% missing; 415 explicit zeros. Reflects reported response activity, not coverage (no denominator) |
| **Slaughtered** | ❌ Do not use as an outcome | 533 of 552 reported values are 0; only 19 non-zero rows nationally. Mention in passing at most |
| **Case fatality / mortality rates** | ❌ **Do not compute** | Ratios of two fields that are individually inconsistent (Deaths > Cases on 5 rows) and whose denominators are not true populations |
| **Incidence / prevalence** | ❌ **Do not compute** | No animal population denominators anywhere in the dataset |

---

## 10. Cleaning decisions

Every transformation is implemented in `scripts/` and logged to
`data/processed/transformation_log.csv`. **The raw file is set read-only and is
never modified.**

| # | Decision | Justification |
|---|---|---|
| 1 | Read every field as text; parse counts with `-` → `NaN` | Prevents `-` being coerced to 0 by any reader |
| 2 | **Never impute `-` as 0** | `New outbreaks` contains no zeros anywhere; other columns carry `0` and `-` side by side |
| 3 | Classify rows by **blank `Species`**, not `Animal Category` | The `Animal Category` header label changes in 2020 (§7) |
| 4 | Define the block key as Year × Semester × Location × Disease × Serotype | Recovers the event grain that `Event_id` cannot supply |
| 5 | Restrict analysis to 2006–2023 (947 of 1,112 rows) | Protocol. 165 excluded rows are **retained in the master dataset** |
| 6 | Level the geography into national / ADM1 / ADM2 | Three grains are mixed in one column |
| 7 | Exclude national `Nigeria` rows from state analysis; keep for national series | They cannot be assigned to a state; they are not state aggregates |
| 8 | Flag ADM2/LGA rows; **do not roll up** | Would mix grains. Zero such rows fall in the study period |
| 9 | Recode `Nassarawa` → `Nasarawa` (only recode applied) | Disjoint year ranges, never co-occur, identical grain (§4.3); sensitivity analysis reported |
| 10 | Retain the 18 all-missing detail rows, flagged | They record species involvement; dropping them would be a silent exclusion |
| 11 | Retain the 7 header-less blocks | They are valid follow-up reports, not zero-outbreak reports |
| 12 | Retain the ~1% logically inconsistent rows, flagged | Correcting source data is not defensible here |
| 13 | Represent a disease-year with no report as **missing**, never 0 | Central to the trypanosomosis interpretation |

**Outputs:** `wahis_ng_rows_annotated.csv` (1,112 rows, nothing dropped),
`analysis_outbreaks.csv` (450 header rows), `analysis_animal_counts.csv`
(497 detail rows), `location_standardisation.csv`, `transformation_log.csv`.

---

## 11. Potential double-counting risks

| Risk | Real? | Why |
|---|---|---|
| Summing `New outbreaks` over **all** rows | ❌ **No** | Detail rows contribute `NaN`. Verified: sum over all study-period rows = 2,285 = sum over header rows only |
| Multiple species rows inflating outbreaks | ❌ No | Species rows never carry `New outbreaks` |
| Two semesters of one year | ❌ No | They are genuinely distinct reporting periods; summing to a year is correct |
| **Converting `-` to 0 before aggregating** | ✅ **YES — the primary hazard** | Would fabricate ~582 zero outbreak-records and turn structural non-reporting into observed absence |
| **Writing "0" into a disease-year with no report** | ✅ **YES** | Would make the trypanosomosis series appear to fall to zero in 2022–2023 and the HPAI series to fall to zero in 2009–2013 |
| Adding national `Nigeria` rows to state totals | ✅ Yes, if not filtered | 1 outbreak in the study period; filtered |
| Rolling 2026 LGA rows into parent states | ✅ Yes, if not filtered | Outside the study period; filtered anyway |
| Subtype-split blocks describing the same events | ⚠️ Possible, small | 2 strata, ≤4 outbreaks (0.4% of rabies); documented, not adjusted |
| Counting rows instead of outbreaks | ✅ Yes, if done | Rows per block vary 1–4 for structural reasons |

The headline point is worth stating plainly: **the danger in this dataset is not
double-counting, it is zero-fabrication.**

---

## 12. Initial descriptive findings

*All figures below are counts of **reported** events. None is an estimate of
disease occurrence.*

### 12.1 Disease profile, 2006–2023

| | Rabies | HPAI | Trypanosomosis |
|---|---|---|---|
| Years with a report | 18 / 18 | 13 / 18 | 13 / 18 |
| First / last reporting year | 2006 / 2023 | 2006 / 2023 | **2008 / 2021** |
| States/FCT reporting | 35 / 37 | 35 / 37 | **17 / 37** |
| Reporting blocks | 200 | 197 | 53 |
| **Total reported new outbreaks** | **923** | **1,231** | **130** |
| Susceptible animals | 28,297 | 6,767,724 | 13,620 |
| Cases | 2,751 | 2,647,359 | 3,008 |
| Deaths | 618 | 1,234,097 | 285 |
| Killed and disposed of | 624 | 4,886,232 | 192 |
| Vaccinated | 4,985 | 1,500 | 0 |

*(State-level rows; national totals add 1 HPAI outbreak. `-` values excluded, never zeroed.)*

**The animal-level columns must not be compared across these three columns.**
HPAI counts commercial poultry flocks, rabies counts individually presented
animals, trypanosomosis counts herd-screened cattle.

### 12.2 Annual reported new outbreaks

`.` = no WAHIS report that year (**not** a reported zero).

| Year | Rabies | HPAI | Trypanosomosis |
|---|---|---|---|
| 2006 | 1 | 143 | . |
| 2007 | 2 | 150 | . |
| 2008 | 23 | 4 | 9 |
| 2009 | 24 | . | 15 |
| 2010 | 5 | . | 6 |
| 2011 | 11 | . | 1 |
| 2012 | 19 | . | 1 |
| 2013 | 31 | . | 11 |
| 2014 | 9 | 1 | 3 |
| 2015 | 2 | 251 | 3 |
| 2016 | 1 | 219 | . |
| 2017 | 51 | 44 | 2 |
| 2018 | 91 | 1 | 11 |
| 2019 | 71 | 2 | 14 |
| 2020 | 107 | 1 | 14 |
| 2021 | 147 | 257 | 40 |
| 2022 | 178 | 140 | . |
| 2023 | 150 | 19 | . |
| **Total** | **923** | **1,232** | **130** |

Observations:

* **Rabies** is the only disease reported in **every** study year. Reporting is
  low and flat until ~2016 (≤31/yr), then rises steeply and stays high:
  2017–2023 contribute 795 of 923 outbreaks (86%). Peak 2022 (178).
  Whether this is a change in rabies occurrence or a change in reporting
  behaviour **cannot be determined from this dataset**.
* **HPAI** shows two sharp epidemic waves separated by long silences —
  2006–2008 (297), a complete five-year gap 2009–2013, 2015–2017 (514),
  a near-silent 2018–2020 (4), then 2021–2023 (416). Peak 2021 (257).
  The wave structure is consistent with introduction–epidemic–elimination
  cycles rather than with a reporting artefact.
* **Trypanosomosis** is reported at a consistently low level (median 9/yr) from
  2008, **peaks in its final year (2021, 40 outbreaks)**, and then stops. See
  §12.4 and §15.1.

### 12.3 Geographic patterns

Cumulative reporting and persistence rank states differently, and both are
reported.

**Top 10 by cumulative reported outbreaks:**

| State | Total | Diseases |
|---|---|---|
| Plateau | 774 | 3 |
| Kano | 316 | 2 |
| Bauchi | 158 | 3 |
| Lagos | 143 | 3 |
| Kaduna | 140 | 2 |
| Niger | 70 | 3 |
| Rivers | 56 | 1 |
| Delta | 51 | 2 |
| Gombe | 51 | 3 |
| Katsina | 50 | 2 |

**Top 10 by persistence (sum of reporting years across diseases):**

| State | Disease-years | Diseases |
|---|---|---|
| Plateau | 23 | 3 |
| Bauchi | 21 | 3 |
| Kaduna | 19 | 2 |
| Kano | 19 | 2 |
| Niger | 16 | 3 |
| Federal Capital Territory | 13 | 3 |
| Gombe | 12 | 3 |
| Nasarawa | 11 | 3 |
| Osun | 11 | 3 |
| Benue | 10 | 2 |

Plateau leads on both metrics and is the only state above 700 cumulative
outbreaks (469 rabies, 303 HPAI, 2 trypanosomosis). FCT, Nasarawa and Osun enter
the persistence top ten without appearing in the cumulative top ten — they report
consistently rather than in large bursts. Rivers is the reverse: 56 outbreaks,
all HPAI, one disease only.

Disease-specific concentration:

* **Rabies** — Plateau (469) alone is 51% of the national total; the next state
  is Bauchi (93). 35 states report; **Abia and Rivers report none**.
* **HPAI** — Plateau (303), Kano (250) and Lagos (137) are 56% of the total.
  35 states report; **Cross River and Ondo report none**.
* **Trypanosomosis** — Niger (54) is 42% of the total; then Kwara (18), FCT (10).
  Only **17 of 37 states** ever report it, concentrated in the North-Central/
  Middle Belt tsetse belt.

**These are descriptions of reported surveillance activity, not of risk.** A
state may appear high because it has more veterinary capacity, a larger
commercial poultry sector, or a closer relationship with the national reporting
chain.

### 12.4 Disease × location overlap

| Diseases reported | States |
|---|---|
| **3** | 16 — Adamawa, Anambra, Bauchi, Enugu, FCT, Gombe, Jigawa, Kogi, Kwara, Lagos, Nasarawa, Niger, Osun, Oyo, Plateau, Zamfara |
| **2** | 18 |
| **1** | 3 — Rivers (HPAI only), Cross River (Rabies only), Abia (HPAI only) |

The 16 three-disease states are the clearest candidate set for integrated
surveillance planning, but note the driver: trypanosomosis is reported in only 17
states, so **"reported all three" is largely a statement about being inside the
tsetse-reporting belt**, not about carrying more zoonotic disease.

---

## 13. Recommended figures

Three draft figures are produced (`outputs/figures/`, PNG + PDF at 300 dpi).
They are drafts pending approval of this audit.

**Figure 1 — Temporal patterns, 2006–2023.** Two-part. Panel A places all three
series on one shared axis (legitimate: identical unit). Panel B repeats each on
its own scale so the trypanosomosis shape stays legible. **Years with no report
are drawn as line breaks and grey bands, never as zero**, and the trypanosomosis
classification end is annotated on the figure itself.

**Figure 2 — Geographic distribution.** Three disease-specific ranked bar panels
with **independent x-scales**, sorted within panel, each labelled with its own
total and the number of reporting states.

> **Choropleth maps not produced.** The geographic data (37 ADM1 units, all
> matched) would support mapping, but no Nigeria ADM1 boundary file is available
> in this environment and outbound access to boundary sources
> (geoBoundaries, GADM) is blocked by network policy. A choropleth version is
> straightforward once an ADM1 boundary file with documented provenance
> (GRID3 Nigeria, geoBoundaries gbOpen NGA-ADM1, or HDX/OCHA COD-AB) is added to
> `data/reference/`. Recommend doing this deliberately, with the source and
> vintage recorded, rather than pulling an arbitrary GeoJSON.

**Figure 3 — Disease × state matrix.** Two panels: (A) reported outbreaks, shaded
**within** each disease column with raw values printed, because the three
diseases differ by an order of magnitude; (B) number of reporting years on a
shared 0–18 scale, which *is* genuinely comparable. Having both makes the point
that cumulative burden and persistence rank states differently.

Colours are the validated three-slot categorical palette (blue/orange/aqua),
which clears all-pairs colour-vision-deficiency and normal-vision separation
thresholds; every figure is backed by a CSV in `outputs/tables/`.

---

## 14. Limitations identified from the dataset

**Reporting-system limitations**

1. WAHIS is a **passive, country-reported** system. Counts measure what Nigeria
   detected, confirmed and chose to notify — not what occurred.
2. The `Animal Category` header label changed in 2020 and completed the change by
   2024, and the export format changed entirely in 2026 (one row per outbreak,
   populated `Event_id`, ADM2 locations). **The 2021 WAHIS relaunch falls inside
   the study period.** Apparent trends around 2020–2021 may partly reflect this.
3. `Event_id` and `Outbreak_id` are unusable (0.5% populated), so true event
   linkage is impossible and outbreak counts must be reconstructed from block
   structure.
4. The "outbreak" (epidemiological unit) is not equivalent across diseases: one
   commercial poultry farm, one village dog case, and one screened cattle herd
   all count as one outbreak.

**Data-quality limitations**

5. Item non-response reaches 25% for `Vaccinated` and 8.5% for
   `Killed and disposed of`. 18 detail rows carry no counts at all.
6. ~1% of detail rows are logically inconsistent (Cases > Susceptible;
   Deaths > Cases).
7. `Killed and disposed of` exceeds `Cases` on 12.3% of rows, so it must not be
   read as disease impact.
8. Two strata are split by subtype in a way that may partly describe the same
   events (≤4 outbreaks).

**Geographic limitations**

9. Three geographic grains are mixed in one column. State is the finest usable
   grain for 2006–2023 — **there is no sub-state resolution in the study period**,
   so within-state heterogeneity is invisible.
10. `Nigeria` records cannot be assigned to a state (1 outbreak in period).
11. A state that never reports a disease is indistinguishable from a state that
    has the disease but does not report it.

**Disease-specific limitations**

12. **The `(-2021)` trypanosomosis suffix truncates that series at 2021** — the
    single most consequential limitation (§15.1).
13. HPAI has a complete five-year gap (2009–2013) that plausibly reflects genuine
    absence between epidemic waves, but this cannot be verified from the dataset.
14. Rabies reporting rises ~10-fold after 2016; occurrence change and reporting
    change are **completely confounded**.
15. Only 4 of 947 study-period rows are `Wild`. Wildlife surveillance is
    effectively absent.
16. Trypanosomosis covers only 17 states, so multi-disease overlap statistics are
    dominated by tsetse-belt geography.

**Inferential limitations**

17. **No population denominators exist** — no animal populations, no herd counts,
    no flock censuses. Incidence, prevalence and rates are impossible.
18. **No human health data.** The dataset cannot support any statement about
    human infection, exposure or risk.
19. No exposure, intervention, climate or livestock-density variables, so **no
    causal inference of any kind** is possible.
20. Reporting intensity is not adjusted for surveillance effort, which is itself
    unmeasured. Higher reporting may indicate better surveillance, not more
    disease.

---

## 15. Questions that cannot be answered with this dataset

### 15.1 STOP ISSUE: the research question cannot be answered as written for trypanosomosis

The protocol asks for patterns **2006–2023** for all three diseases. For
trypanosomosis this is not achievable, and treating it as achievable would
produce a materially misleading result.

**The evidence:**

* The WAHIS disease label is literally `Trypanosomosis (tsetse-transmitted) (-2021)`.
  The `(-2021)` suffix records that the disease ceased to be reportable under
  this name at the end of 2021.
* Reporting stops abruptly and completely after Jul-Dec 2021 — zero rows in 2022
  through 2026, while rabies and HPAI continue normally.
* **2021 is the series maximum (40 outbreaks), and Jul-Dec 2021 is its largest
  single semester (23 rows).** The series ends at its peak.

A naïve 2006–2023 series would show trypanosomosis rising to a record high and
then falling to zero for two years. That would be **an artefact of the WOAH
disease classification, not an epidemiological observation**, and it is exactly
the kind of finding that gets published and then repeated.

**Recommended resolution (requires your decision):** state the trypanosomosis
observation window as **2008–2021** throughout — in the research question, the
methods, every table, and every figure — and present 2022–2023 as *structurally
unobservable*, never as zero. The pipeline already stores these years as missing;
the change needed is to the study framing, not the code.

Options if you prefer otherwise:
1. **Keep 2006–2023 as the overall study window**, with an explicit per-disease
   observation window (Rabies 2006–2023, HPAI 2006–2023, Trypanosomosis
   2008–2021). *This is the recommended option.*
2. Narrow the whole study to 2006–2021 so all three diseases share one window —
   cleaner comparatively, but discards two years of strong rabies/HPAI data.
3. Analyse trypanosomosis as an explicitly right-censored series and drop it from
   any cross-disease temporal comparison after 2021.

A second, smaller framing point: trypanosomosis is first reported in **2008**, so
its window cannot start in 2006 regardless.

### 15.2 Other questions this dataset cannot answer

* **What is the true incidence or prevalence of any of these diseases?** No
  denominators.
* **Is disease increasing, or is reporting increasing?** Irreducibly confounded —
  this applies most acutely to the ~10-fold post-2016 rabies rise.
* **What is the human burden of rabies, HPAI or trypanosomosis in Nigeria?** No
  human data. Animal reports cannot be converted into human risk.
* **Which states have the highest disease risk?** Only reported surveillance
  activity is observable.
* **Did HPAI truly disappear in 2009–2013?** Absence of reports is not evidence of
  absence.
* **Where within a state did outbreaks occur?** No sub-state resolution in the
  study period.
* **What is the case fatality rate?** Denominators are affected-unit counts, not
  populations, and the fields are internally inconsistent on ~1% of rows.
* **What drove any observed pattern?** No exposure, climate, livestock-density or
  intervention variables.
* **Is wildlife a reservoir?** 4 wild-animal rows in 18 years.
* **Did control measures work?** `Vaccinated` is 25% missing with no denominator.

---

## 16. Proposed final analysis plan

**Pending your approval of this audit, and of the §15.1 decision.**

### Design
Descriptive, retrospective analysis of secondary passive animal-disease
surveillance data. **No modelling, no inference, no rates.**

### Study window
2006–2023 overall, with per-disease observation windows stated everywhere:
Rabies 2006–2023 · HPAI 2006–2023 · **Trypanosomosis 2008–2021** (option 1 above).

### Unit and outcome
Reporting block (Year × Semester × ADM1 × Disease × Serotype); primary outcome
`New outbreaks` summed over block headers. Secondary outcomes (Cases, Deaths,
Susceptible, Killed and disposed of) reported **per disease only**, never ranked
across diseases.

### Planned analyses
1. Reporting-coverage description — blocks, reporting years, reporting states per
   disease; explicit accounting of non-reporting years as missing.
2. Temporal — annual reported outbreaks per disease (Figure 1); peaks, sustained
   periods, silent periods; the 2021 platform relaunch marked on the timeline.
3. Geographic — state totals, reporting years, first/last year per disease
   (Figure 2); cumulative burden and persistence reported **separately**.
4. Disease × location overlap — the three-disease/two-disease/one-disease
   classification and per-disease reporting years (Figure 3).
5. Species and animal-category description per disease (dog-mediated rabies is
   84% of rabies detail rows; poultry is 99.5% of HPAI).
6. Data-quality sub-analysis — missingness, `-` vs `0`, internal consistency,
   header-less blocks — reported as a **result**, not hidden in the methods. The
   quality of a surveillance system is a legitimate One Health finding.

### Sensitivity analyses (already implemented)
Withholding the Nassarawa recode; including vs excluding national rows;
verifying that all-row summation equals header-row summation.

### Explicitly excluded
Incidence/prevalence, case fatality or mortality rates, R₀, forecasting, spatial
risk or cluster modelling, regression of counts on anything, any human-health
inference, any "high-risk state" designation.

### Language rules for the manuscript
"Reported surveillance activity" / "reported surveillance burden" throughout;
never "incidence", never "high-risk state", never "cases occurred". Interpretation
phrased as *"the observed concentration and repeated reporting may identify
locations where integrated One Health surveillance could be strengthened"* —
observed evidence, interpretation, and future research questions kept visibly
separate.

### One Health interpretation (Phase 12 — to be written after approval)
Grounded strictly in the observed reporting patterns: dog-mediated rabies
dominance and its implication for bite-case reporting interoperability between
veterinary and human health systems; HPAI's epidemic-wave structure and
concentration in commercial poultry states and their implication for
poultry-worker exposure surveillance; the tsetse-belt concentration of
trypanosomosis and the surveillance gap its 2021 delisting creates; the 16
three-disease states as candidate sites for integrated reporting; and the near-
total absence of wildlife surveillance as a system gap. Each stated as a
hypothesis for surveillance strengthening, not as a risk assessment.

### Deferred pending a decision
Choropleth maps (needs an ADM1 boundary file with documented provenance — §13).

---

## Reproducibility

```
wahis-nigeria-zoonoses/
├── data/
│   ├── raw/Quantitative_data_20260905.csv   read-only, never modified
│   └── processed/                           derived datasets + transformation log
├── scripts/
│   ├── wahis_common.py                      config, loader, derived columns
│   ├── 01_audit.py                          Phases 1–4
│   ├── 02_build_clean.py                    Phase 5
│   ├── 03_descriptive.py                    Phases 6–9 + sensitivity
│   └── 04_figures.py                        Phase 10
├── outputs/{tables,figures,logs}/
└── reports/DATA_AUDIT_REPORT.md             this document
```

Run in order: `python3 scripts/01_audit.py && python3 scripts/02_build_clean.py
&& python3 scripts/03_descriptive.py && python3 scripts/04_figures.py`.
Requires pandas, numpy, matplotlib. Full console output for each stage is
committed under `outputs/logs/`.
