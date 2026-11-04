# DOR NAL fields used by this skill

From the 2026 NAL/SDF/NAP User's Guide (Florida Department of Revenue, Property Tax Oversight). Confirm against the guide for the roll year you are using, because the layout changes from year to year.

| Field | Name | Meaning |
|---|---|---|
| 1 | `CO_NO` | County number |
| 2 | `PARCEL_ID` | Parcel ID |
| 8 | `DOR_UC` | DOR land-use code, 000-099 (000-009 residential, 010-039 commercial, 040-049 industrial, 050-069 agricultural, 070-079 institutional, 080-089 governmental, 090-099 misc./centrally assessed) |
| 11 | `JV` | Just (market) value |
| 14 / 15 | `AV_SD` / `AV_NSD` | Assessed value, school / non-school (differ because of the non-homestead caps that apply only to non-school levies) |
| 16 / 17 | `TV_SD` / `TV_NSD` | Taxable value, school / non-school. `TV_NSD` is the **county** taxable value; exemptions adopted only by a municipality are not applied to it |
| 18 / 19 | `JV_HMSTD` / `AV_HMSTD` | Just / assessed value of the part of the parcel under Save Our Homes (homestead) |
| 50 | `TOT_LVG_AREA` | Total living (heated) area, sq ft |
| 52 | `NO_RES_UNTS` | Number of residential units (for per-unit apportionment) |
| 44 | `LND_SQFOOT` | Land square footage |
| 94 | `TAX_AUTH_CD` | Taxing-authority code (property appraiser's own coding of which municipality/districts levy on the parcel) |
| 110 | `EXMPT_01` | Homestead exemption, first $25,000 (all levies). **> 0 means a homestead** |
| 111 | `EXMPT_02` | Additional homestead exemption, up to $26,411 in 2026, non-school levies, applied to value between $50,000 and ~$76,411 |
| 112 / 113 | `EXMPT_03` / `EXMPT_04` | Low-income senior exemption: county-adopted / municipality-adopted |
| 148 / 149 | `EXMPT_39` / `EXMPT_40` | Long-term low-income senior exemption: county / municipality |
| 119 / 120 | `EXMPT_10` / `EXMPT_11` | Historic commercial/nonprofit: county / municipality |
| — | `EXMPT_22`/`23`, `24`/`25`, `45`/`46` | Economic development, historic, affordable housing local options: county / municipality |
| 140-143 | `EXMPT_31`-`34` | $500 exemptions (blind, widow(er), disabled) — check the guide for the current amounts |
| 144 | `EXMPT_35` | $5,000 disabled ex-servicemember |

**Municipal taxable value** ≈ `TV_NSD` + county-only exemptions − municipality-only exemptions. `exemption_impact.py` does this adjustment.

**What the file cannot tell you:** residency date (for the new-resident $50,000 phase-in), owner income, the fire/EMS call history, impervious area. Get those elsewhere (see `data-sources.md`).
