# Slice 2B Forecast-Readiness Decision

## Decision

Slice 2A is complete: it is a source-bound, private annual snapshot package, not a model-ready dataset. Slice 2B is the next gate. It must reconcile official annual source vintages and extend the annual panel before any modelling decision.

The supported target grain is **county-year**. No authoritative national county × season observed maize-yield panel was found. County-season is therefore an evidence-insufficiency result, and no crop calendar may disaggregate annual totals.

## Source audit

The accepted NIPFN workbook remains private and source-bound, SHA-256 `15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8`.

The KNBS *National Agriculture Production Report 2024* is a private candidate revision source, not accepted or merged. Its direct URL is <https://www.knbs.or.ke/wp-content/uploads/2025/01/National-Agriculture-Production-Report-2024.pdf>; its observed PDF is 12,398,810 bytes with SHA-256 `7d86dc4cbfa1d0b5204e2428fb8d84c3bada0fc1775bf0b7d557dfebcc4d70eb`. Terms and redistribution remain review-required.

The report covers annual county harvested area and production for 2019-2023, marks 2023 provisional, and reports no yield field. At a 0.1% overlap-comparison threshold, 24 of 47 county rows differ materially from the accepted workbook for 2020. Busia matches within rounding. Trans Nzoia changes from area 18,591 ha / production 11,251.1 t in the workbook to area 104,850 ha / production 489,056 t in the report.

KilimoSTAT and the Food Systems Dashboard are removed from the critical path because no current verified response contract is accessible.

## Required closure

Slice 2B must preserve both private source vintages, establish an evidence-backed precedence/reconciliation policy, extend the annual county panel only after reconciliation, and then decide whether county-year baseline feasibility is supportable. It does not authorize season labels, forecasting, or decision support.

## Closure outcome

The private Slice 2B build now closes this gate. It extracts all 235 county-year
records from the report, preserves the older 2020 vintage separately, and uses
the report as the active series for 2019-2023. Combined with the workbook's
2012-2018 records, this produces 564 county-year rows, 563 usable yield labels,
and fixed train/validation/test years of 2012-2021, 2022, and provisional 2023.

County-year baseline modelling is supportable and is the next implementation
slice. This decision still does not authorize county-season labels.
