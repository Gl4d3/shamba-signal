# Shamba Signal Completion Slices

This is a finish plan, not an infrastructure roadmap. Every remaining slice must create a new
machine-learning or user-visible capability.

## Completed — Foundation and feasibility

Repository contracts, the FastAPI shell, source evidence, maize/Busia selection, and private source
handling are merged. They are enough. Do not add more foundation work.

## Completed — Official county-year modelling panel

The private panel contains 564 county-year rows across 47 counties for 2012-2023, with 563 usable
labels. NIPFN supplies 2012-2018 and the KNBS 2024 report supplies 2019-2023. The annual evidence
does not support county-season or mid-season claims.

## Completed — Temporal baselines

On provisional 2023, county historical mean is the strongest model at 0.2998 t/ha MAE. Ridge
(0.3615) beats previous year (0.4651) but not county mean. See
`docs/modelling/temporal-baseline-result.md`.

## Slice 4 — Weather feature value test

**Outcome:** one defensible weather feature source is joined to the fixed county-year panel and one
weather-informed tabular model is evaluated on the existing split.

**Minimum implementation:**

- use one source and a small documented feature set;
- cache source responses locally and preserve a reproducible build command;
- compare the existing baselines with one regularized or tree-based weather model;
- publish national and county-level evaluation artifacts; and
- keep the feature/model only if provisional-2023 MAE beats 0.2998 t/ha, otherwise publish no-go.

**Time/scope guardrail:** if a source cannot be made to work in a bounded attempt, switch once to
one official alternative. Do not restart broad data-source research.

## Slice 5 — Real-data evidence dashboard

**Outcome:** the status-only homepage becomes a polished researcher-facing dashboard backed by the
generated evaluation fixture.

**Minimum implementation:**

- national result and winning-model summary;
- compact baseline comparison;
- county selector with historical actuals and 2023 prediction/error;
- weather-feature and evidence/limitations panels;
- explicit provisional/no-go states; and
- desktop and mobile browser verification with committed screenshots.

No maps, authentication, database, backend service split, or deployment is required unless the
simple dashboard demonstrably cannot meet the journey without it.

## Slice 6 — Portfolio closeout

**Outcome:** another engineer, researcher, or hiring reviewer can understand and run the finished
project.

**Minimum implementation:**

- README rewritten around problem, data, method, result, UI, limitations, and local run commands;
- one concise local-to-AWS portability diagram, clearly labelled unimplemented;
- final screenshots and an honest CV-ready project summary; and
- focused verification, commit, merge, and push to `main`.

## Completion rule

Stop when Slices 4-6 meet the current PRD. Do not create additional slices for infrastructure,
production readiness, speculative modelling, or governance. The project is allowed to finish with
a scientifically useful negative model result.
