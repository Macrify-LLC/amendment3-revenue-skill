# Where to find the data

## Tax roll: Florida DOR NAL file (every county, free)

- Portal: floridarevenue.com → Property Tax Oversight → Data Portal → "Tax Roll Data Files" → `NAL` → year folder (`2026F` = 2026 final roll, `2026P` = preliminary).
- File name pattern: `<County> <CO_NO> Final NAL <year>.zip` (e.g. `Pinellas 62 Final NAL 2026.zip`), containing `NAL<CO_NO>F<year>01.csv`. County numbers are listed in the User's Guide.
- The folder listing is drawn by JavaScript. If a page shows nothing, use the SharePoint REST endpoint:
  `https://floridarevenue.com/property/dataportal/_api/web/GetFolderByServerRelativeUrl('/property/dataportal/Documents/PTO%20Data%20Portal/Tax%20Roll%20Data%20Files/NAL/2026F')/Files` with header `Accept: application/json;odata=nometadata`.
- Field definitions: the "NAL SDF NAP Users Guide" for the matching year (same portal, `User Guides`). The fields this skill uses are in `nal-fields.md`.
- Sizes: large counties run 200 MB+ uncompressed. The script streams the file, so memory is not a problem.
- **Identifying the jurisdiction:** `TAX_AUTH_CD` is assigned by each property appraiser. Run `exemption_impact.py --list-tax-auth --city <NAME>` to see the codes in an area, then confirm the right code(s) against the property appraiser's taxing-district/millage table. Mailing city (`PHY_CITY`) is **not** the city limits. Unincorporated addresses often carry the city's name.
- Property appraisers often post richer extracts (building characteristics, unit counts, TRIM data) that are useful for apportionment. Check the county PA's "data downloads" page.

## Millage and taxable value

- Property appraiser: certified taxable values (Form DR-420) for each taxing authority, adopted millage table.
- Department of Revenue: millage and taxes levied by each taxing authority (the "Florida Property Valuations and Tax Data" book).
- The jurisdiction's own TRIM / final millage resolution (September).

## Budget

- The adopted budget book (usually the "Financial Center" / "Budget" page), the CAFR/ACFR, and the OpenGov or OpenBook transparency portal if there is one.
- **Published Amendment 3 impact analyses.** Many governments released them before the November 2026 vote (alternative budgets, workshop presentations, FAQ pages). Search the agenda portal (CivicWeb, Granicus, Legistar) for "Amendment 3," "homestead," "alternative budget," "property tax reform."
- Florida League of Cities / Florida Association of Counties per-jurisdiction data packets.
- Office of Economic and Demographic Research (EDR): local government financial data, Revenue Estimating Conference impact estimates.

## Existing fees and assessments

- Fee schedule resolution/ordinance (often in the code of ordinances appendix, on Municode or American Legal).
- Utility rate resolutions (water, sewer, stormwater, solid waste).
- Non-ad valorem assessment rolls: the tax collector's bill for any parcel shows the non-ad valorem charges, and the property appraiser or tax collector can supply the certified roll list.
- Existing assessment ordinances and methodology reports (agenda archives, usually adopted in spring or summer).

## Service data for apportionment

- Fire/EMS: incident data by property use (NFIRS), call types (fire vs. medical), unit hour use, ISO/PPC rating. Request it from the fire department.
- Stormwater: impervious area by parcel (GIS), ERU definition.
- Solid waste: units served, tonnage, contract rates.
- Recreation: program participation and cost recovery reports.

## Legal sources

- Florida Statutes: leg.state.fl.us (current text) / flsenate.gov (bills, enrolled text, analyses).
- Constitution as amended: the enrolled HJR 1-F, and later the Division of Elections certification.
- Cases: Florida Supreme Court and DCA opinions (supremecourt.flcourts.gov, the DCA sites), CourtListener, Justia, Google Scholar.
