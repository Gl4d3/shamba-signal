# Shamba Signal MVP Definition

## Single sentence

Investigate whether one data-selected crop can support a defensible mid-season county-season yield forecast across Kenya, with one county deep dive, uncertainty, lineage, and explicit abstention when evidence is insufficient.

## Current state

The foundation implements product documentation, a FastAPI shell, a public status page, source catalogue, repository validation, tests, and CI definition. No target dataset, trained model, forecast fixture, research dashboard, advisory engine, scheduler, AWS deployment, or Druid benchmark exists yet.

## Primary user

Agricultural researchers and programme analysts. County extension leadership and food-security teams are secondary users of the same evidence. Farmer-facing workflows are outside the first release.

## Future supported output

For each county that passes evidence and model gates:

- estimated yield in tonnes per hectare;
- calibrated prediction bounds;
- historical baseline and anomaly;
- evidence-quality status;
- forecast cutoff, calendar, source, feature, and model lineage;
- explicit abstention when support is inadequate.

Ward and pixel layers may show relative yield potential or crop-stress indicators. They must never be labelled measured ward or farm yield without matching validation data.

## Immediate MVP critical path

1. Reproducible target dataset.
2. Honest baseline forecast or documented no-go result.
3. Minimal evidence UI driven by a real versioned fixture.
4. Remote-sensing complexity only after a precise improvement hypothesis.

## Acceptance criteria

- The crop and pilot county are provisionally selected by a reproducible metadata-level scorecard and confirmed or replaced using downloaded records.
- A clean environment rebuilds the county-season modelling table from documented, checksummed snapshots.
- Reported and derived yield remain distinguishable; derivation obeys positive-area, matching-period, matching-crop, matching-county, and compatible-unit rules.
- The baseline slice either beats mandatory naïve baselines on frozen geographic and temporal holdouts, or publishes an insufficiency/no-go result and abstains.
- Every supported forecast contains prediction bounds, evidence quality, cutoff, and lineage.
- The first UI uses real or unmistakably labelled versioned fixtures and exposes insufficient-evidence states.

## Explicit non-goals for the immediate delivery

- Farm-level or measured ward-level yield prediction.
- Multiple crops before one crop is validated.
- Temporal CNNs before the baseline research question is answered.
- Full national dashboard before a real forecast fixture exists.
- Advisory generation, scheduled operations, AWS deployment, SageMaker, Druid, or premature microservices.
- Automated resource allocation or farm-specific agronomic prescriptions.
