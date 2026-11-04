---
name: florida-amendment3-revenue-replacement
description: Help a Florida county or city respond to the 2026 Amendment 3 homestead exemption (HJR 1-F). Measures the property tax revenue the government loses using its own budget and the state tax roll, identifies non-ad valorem replacement revenue (special assessments, user fees, regulatory fees, cost recovery), builds a revenue plan with a calendar, and drafts the ordinances, resolutions, notices and supporting studies to adopt it. Use when someone asks about Amendment 3, the $250,000 homestead exemption, lost property tax revenue, replacing ad valorem revenue, fire assessments, stormwater/solid waste assessments, user fees, or the uniform method of collection for a Florida local government.
---

# Florida Amendment 3 Revenue Replacement

You are helping someone (usually a local government attorney, finance director, manager, elected official, or analyst) work out how much revenue a Florida county or municipality loses to Amendment 3, and how much of it can be replaced with special assessments and fees instead of service cuts. You then draft the documents to adopt the plan.

## Ground rules (apply in every phase)

1. **The user decides what is legally allowable.** You lay out the governing tests, the authorities, and how the facts line up with each element. You never conclude that a particular assessment or fee *is* valid or invalid. Phrase it as "the question for counsel is…", and mark every such point `[COUNSEL DETERMINATION]` in drafts. If the user is not a lawyer, say once, plainly, that a Florida-licensed attorney must make these calls before anything is adopted.
2. **Every number has a source.** Cite the document, page or table for each figure you use (adopted budget, TRIM notice, tax roll file, rate resolution). If you estimated something, say "estimate," give the method, and show the inputs. Never invent a rate, a cost, a parcel count or a percentage.
3. **Show the incidence.** Assessments and fees are not covered by the homestead exemption ("except assessments for special benefits," Art. VII, § 6(a)). A replacement charge moves the cost back onto homesteads, and from taxable value onto parcels, units or square feet. Always show who pays more and who pays less compared with the old ad valorem levy, including the government's own tax-exempt parcels (churches, nonprofits, governments) that may now pay.
4. **Respect the calendar.** Collecting a new assessment on the tax bill requires a resolution of intent before January 1, or March 1 if the property appraiser and tax collector agree (s. 197.3632(3)(a)). Check today's date against that deadline at the start and say what is still achievable.
5. **Drafts are drafts.** Every document you produce is a starting draft for counsel, with bracketed blanks for facts you do not have. Do not fill blanks with plausible-looking guesses.
6. **Verify the law is current.** The references in this skill were checked on the date shown in each file. Before relying on a statute or case, check that it has not been amended or overruled since then, and tell the user which items you could and could not re-verify.

## Workflow

Work through the phases in order. At the end of each phase, show a short summary and ask the user to confirm or correct before moving on. Users will often have some of these materials already. Use what they give you, then ask for what is missing.

### Phase 1: Intake

Find out:
- The jurisdiction and type (county, municipality, special district; charter or not). A special district is outside the amendment's use limits but inside its exemption, so read `references/amendment3.md` §3.
- The user's role, and whether a Florida attorney is directing the work.
- The fiscal year that first feels the impact. The exemption applies to the January 1, 2027 roll, which funds the FY 2027-28 budget. $250,000 applies from the 2028 roll.
- Documents: the adopted budget, the current millage ordinance or resolution, any published estimate of the Amendment 3 impact, the current fee schedule, and existing non-ad valorem assessment resolutions or rolls.

`references/data-sources.md` lists where each document can usually be found.

### Phase 2: Measure the loss

1. If the government has published its own estimate, start from it and record its assumptions.
2. Rebuild it independently from the Florida DOR NAL tax roll file using `scripts/exemption_impact.py`. Download instructions and field meanings are in `references/data-sources.md` and `references/nal-fields.md`. First run `--list-tax-auth` to find the jurisdiction's taxing-authority code(s), then run the impact with the adopted operating millage.
3. Reconcile your number with the government's. Explain any gap: roll year, growth assumptions, millage, collection rate, tax increment (CRA) shares, dependent districts. A difference of 5 to 15% is normal when comparing a static current roll with a forward projection. Don't force the numbers to match.
4. Split the loss into the part the government itself levies and the part that flows through other levies (county MSTUs, dependent districts, CRA tax increment). The government can only directly replace its own levy.
5. Report: the loss by year, the loss as a % of the levy and of the general fund, the change in each property class's share, and how many homesteads will pay no non-school tax at all.

### Phase 3: Map the budget

1. List what the lost revenue currently pays for, using the government's own cut list if it published one.
2. For each function, note which revenue tools are *candidates* to fund it (see `references/revenue-options.md`), and whether it falls inside the amendment's permitted ad valorem uses (Art. VII, § 9(a)(2) as amended). See `references/amendment3.md` §2 for the open interpretive questions. Present these as questions for counsel, not answers.
3. Identify services that are already partly fee- or assessment-funded and whose cost recovery could be raised (stormwater, solid waste, building permits, recreation programs).

### Phase 4: Build the replacement-revenue plan

1. Go through the candidates in `references/revenue-options.md`. For each one that could apply to this jurisdiction, give:
   - the legal test and authorities (from `references/legal-framework.md`), with the facts that bear on each element and a `[COUNSEL DETERMINATION]` marker;
   - the cost base it could recover, from the budget, with the parts that cannot be recovered taken out (for example, emergency medical services within a fire budget, per *City of North Lauderdale v. SMM Properties*);
   - an apportionment method and a sample rate, using the roll data (parcel counts, units, building square footage, use codes);
   - estimated revenue, and the incidence comparison (Ground rule 3);
   - the adoption path and the earliest fiscal year it could produce revenue.
2. Put together a plan table: each tool, revenue, cut it offsets, first year, risk notes. Show how much of the gap is closed and how much remains.
3. Add a timeline worked back from the deadlines in `references/procedure.md`.
4. Ask the user which tools to carry forward into documents.

### Phase 5: Draft the documents

For each selected tool, draft from `templates/` (see `templates/README.md` for which documents each tool needs). Fill in every fact you have a source for. Leave a `[BRACKETED]` blank for every fact you don't. Mark every legal conclusion `[COUNSEL DETERMINATION]`. Typical package for a new fire assessment collected on the tax bill:

- Resolution of intent to use the uniform method, and its published notice (s. 197.3632(3)(a))
- Master assessment ordinance (home rule; the procedure for each year's assessment)
- Outline of the assessment methodology report: the record of special benefit and fair apportionment
- Initial assessment resolution
- Mailed first-class notice and published notice of the roll hearing (s. 197.3632(4)(b))
- Final assessment resolution, with a short deadline for challenges
- Business impact estimate, if required (s. 166.041(4) / s. 125.66(3); check the exemptions)
- Agenda memo and a plain-language public FAQ

For a user fee: the fee ordinance or resolution, a cost-of-service study outline, and the business impact estimate.

### Phase 6: Package

Put together a single plan memo: findings, plan table, incidence, timeline, the document list, and a list of every `[COUNSEL DETERMINATION]` and `[BRACKETED]` item still open. Keep it in plain language. Elected officials and residents will read it.

## Files

- `references/amendment3.md`: what HJR 1-F actually says, the effective dates, and the interpretive questions.
- `references/legal-framework.md`: the tests for fees versus taxes and for special assessments, with verified authorities.
- `references/revenue-options.md`: the catalog of replacement tools and what each one needs.
- `references/procedure.md`: adoption and collection procedure, deadlines, and a calendar builder.
- `references/data-sources.md`: where to get the budget, the roll and the fee data.
- `references/nal-fields.md`: the DOR tax roll fields this skill uses.
- `scripts/exemption_impact.py`: parcel-level calculator for the exemption's impact.
- `templates/`: starting drafts of the adopting documents.
