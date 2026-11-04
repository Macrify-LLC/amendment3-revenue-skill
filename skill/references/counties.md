# Notes for counties (and differences from cities)

Tested on Leon County's 2026 final roll (countywide levy). The skill was first built around a city, so check these points whenever the user is a county.

## Levies

- A county usually has **several levies**: the countywide general levy, plus MSTUs (municipal service taxing units) covering only part of the county: unincorporated fire, EMS, library, road districts, and so on. Each one loses revenue separately. Run `exemption_impact.py` once for each: `--levy county` with no `--tax-auth` for countywide, and with the MSTU's `TAX_AUTH_CD` code(s) for each MSTU. Ask the property appraiser which codes make up each MSTU.
- Dependent special districts and the county's share of CRA tax increment are separate again. List them, and ask the user whether to analyze them.
- **10-mill cap.** County purposes are capped at 10 mills (Art. VII, § 9(b)). A county "furnishing municipal services may, to the extent authorized by law, levy additional taxes within the limits fixed for municipal purposes," so MSTU millage for municipal-type services runs against a separate 10-mill municipal-purpose limit (see s. 200.071; confirm with counsel). If keeping a levy flat would take more than 10 mills, the calculator says so. In that case raising the tax rate can't close the gap by itself.

## Spending that is hard to change

- **Constitutional officers** (sheriff, clerk, property appraiser, tax collector, supervisor of elections) submit their own budgets, and the county must fund them within statutory processes. Ask the user what share of property tax already goes to them. Many counties find most of their property tax is spoken for (e.g., state mandates such as Medicaid, juvenile justice and court costs).
- Item (g) of the amended § 9(a)(2) expressly covers "the operations and administration of county officers and commissioners established under Article VIII," so constitutional officer budgets are an easier fit than discretionary programs.

## Tools that differ

- **MSBUs** (municipal service benefit units) under s. 125.01(1)(q): the county's usual vehicle for unincorporated fire, solid waste, stormwater, street lighting and road assessments.
- Counties have more general-law taxes available (local option gas taxes, some sales surtaxes, tourist development tax, which has restricted uses). List them in revenue-options §E. They are taxes, not fees, and many need a referendum or supermajority.
- **Fiscally constrained counties** receive state offset appropriations (ss. 218.12, 218.125, 218.136, re-enacted by CS/SB 4-F). Ask whether the county qualifies and include the offset.
- Enactment follows s. 125.66 (not s. 166.041). Chapter 170 is for municipalities. For counties, use home-rule ordinances or the MSBU route.

## Unincorporated vs. city residents

County decisions affect city residents (countywide levy) and unincorporated residents (MSTU/MSBU) differently. Show the incidence for both. Cities inside the county may also be asking the county to make up their losses in shared services (fire districts, EMS, library cooperatives). Note those requests, and the county's own position, as decisions for the user.
