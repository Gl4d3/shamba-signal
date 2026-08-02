# Fallback Source Investigation

## Decision rule

Fallback research must not silently replace the selected official county-season target. A candidate is recorded here only to show why it was rejected or what separate research question it could support.

## KCHSP 2020 Q1-Q2 Crop Output

**Decision: rejected for the yield target.**

The official KeNADA data dictionary lists 20 fields covering county, sub-county, interview period, crop identifier, crop sales, sale units, prices, and input-purchase questions. It does not expose total crop production or harvested area. Maize is present as a crop category, but quantity sold is not production and cannot be divided by an absent area field to create yield.

This dataset may later support market participation or sales-price analysis. It must not enter the supervised yield target.

## KIHBS 2005-2006 Agriculture Modules

**Decision: research-only candidate.**

The official Agriculture Output module contains crop code, total crop area in acres, quantity harvested, and harvested units. The crop code includes several maize categories. That makes it interesting for testing household/parcel linkage, unit conversion, and historical yield-construction rules.

It is not a replacement for the current target because:

- it is a 2005-2006 household survey rather than a continuing county-season statistics panel;
- the catalog describes representativeness at national, urban/rural, provincial, and district levels, not current counties;
- parcel/crop linkage, survey weighting, anonymization, harvested-unit conversion, and access restrictions require separate validation;
- even a successful historical microdata experiment would not validate a current mid-season county forecast.

Any use requires a separate approved research artifact and must preserve the archive's access, confidentiality, citation, and copyright conditions.

## Current conclusion

Neither candidate unblocks Slice 2's production target today. KCHSP is an explicit no-go for yield labels. KIHBS is a useful historical research lead, but only as a bounded experiment after the official county-statistics acquisition path is exhausted or independently blocked with evidence.
