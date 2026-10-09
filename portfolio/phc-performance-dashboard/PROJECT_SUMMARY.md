# Project summary – Primary Healthcare Performance & Service Delivery Analytics

**Business problem.** A primary healthcare programme receives monthly service reports from 60 facilities run with 4 implementing partners. Managers and donors needed one trustworthy view of:
- what services are being delivered;
- where reporting is breaking down;
- which numbers can be trusted.

The existing spreadsheet dashboard mixed missing reports with zero activity and could not be shared outside the programme.

**Approach.**
1. **Inspect.** I inventoried a 16-sheet programme workbook (540 facility-months, 32 indicators) and its methodology rules.
2. **Protect.** I pseudonymised facilities and partners, removed location detail and free text, suppressed one small-cell group, and published rare-event mortality only nationally. An automated scan confirms that none of 208 source identifiers appears in the deliverables.
3. **Validate.** I wrote 11 data-quality checks (315 exceptions logged, none deleted) and corrected the missing-vs-zero treatment: 2,592 false zeros became NULL. Totals reconcile exactly with the source: 288 monthly checks plus all Jan–Sep totals.
4. **Model.** I designed a star schema with two fact grains (service values and facility reporting), national mortality and a data-quality fact, using one-to-many single-direction relationships and a proper date table.
5. **Measure.** I wrote 84 documented DAX measures:
   - volumes;
   - ratio-of-sums rates;
   - reporting completeness;
   - indicator completeness;
   - MoM and QoQ change;
   - a dynamic narrative.

   An independent Python engine produced reference values for every measure.
6. **Design.** I specified five executive pages (overview, MNCH, immunization & FP, malaria, data quality), plus drill-through, tooltips and a reset bookmark, on a consistent accessible theme.

**Insights the dashboard surfaces** (validated, Jan–Sep 2026):
- **Reporting completeness fell** from 97.2% in Q1 to 84.4% in Q3. One partner's facilities stopped reporting entirely from June.
- **Attendance per report received kept rising** (667 → 820 contacts) even though total Q3 attendance fell 8.5%. The apparent decline is largely a reporting effect.
- **Malaria test positivity rose in Q3** (under-5s 72%, adults 67%). Treatment recording broadly matches positives, but 27 facility-months record more treatments than positive tests.
- **The June immunization peak** (about double the usual doses) coincides with an outreach campaign, which inflates Q2 as a comparator.
- **The cross-sectional ANC4-to-ANC1 ratio** rose from 52% to 70% (a continuation signal worth investigating; not a completion rate). FP conversion fell from 58% to 51%.

**Skills demonstrated.** Health information systems and MEL indicator design · data anonymization and disclosure control · data-quality auditing · Power Query (M) · dimensional modelling · DAX (time intelligence, context control, dynamic text) · dashboard UX for executives · reproducible Python QA.

**Status.** Complete build kit with validated data, model, measures and specification. Assembling the `.pbix` and taking screenshots needs Power BI Desktop, which the build environment lacked.
