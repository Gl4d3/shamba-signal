# County-year modelling panel

Slice 2B now produces a private modelling package instead of stopping at a source audit.

- Grain: county x maize x year.
- Coverage: 47 counties, 2012-2023, 564 rows.
- Usable labels: 563; one historical workbook row remains divergent and unusable.
- Active series: NIPFN workbook for 2012-2018 and KNBS 2024 report for 2019-2023.
- Revision handling: the older 2020 workbook values remain in a separate comparison; they are not silently overwritten.
- Split: 2012-2021 train (470 rows), 2022 validation (47), 2023 test (47).
- Caveat: all 2023 test rows are provisional in the source report.
- Redistribution: private local-only while source terms remain under review.

The package contains `modelling_panel.csv`, `revision_comparison_2020.json`,
`package_manifest.json`, and `dataset_card.md`. The next slice trains temporal
baselines against this fixed split; no additional source search is required.
