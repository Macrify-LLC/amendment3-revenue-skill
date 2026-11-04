# Florida Amendment 3 Revenue Replacement Skill

An AI skill for Florida counties and cities working out what to do about the 2026 Amendment 3 homestead exemption.

Give it the government's budget and the state tax roll. It will:

1. Measure the property tax revenue the exemption takes away, parcel by parcel.
2. Map that loss onto the services it pays for.
3. Find candidates to replace it with special assessments and user fees, with the governing legal tests and authorities, the cost base, apportionment, sample rates, and who pays more and who pays less.
4. Lay out the adoption calendar (the tax-bill deadline for a new assessment comes early: a resolution of intent before January 1, or March 1 by agreement).
5. Draft the resolutions, ordinances, notices and supporting studies.

**It does not decide what is legally allowable.** It sets out the tests and the record, and the attorney using it makes every legal call. Every draft is marked for counsel's review.

## Using it

- **Claude (claude.ai, Claude Code, Claude Desktop):** add the `skill/` folder as a skill.
- **ChatGPT or another assistant:** upload `skill/SKILL.md` and the `references/` and `templates/` files to a project (or paste `SKILL.md` as the instructions). Run `scripts/exemption_impact.py` in the assistant's code tool, or locally with Python 3 (no packages needed).

The tax roll comes from the Florida Department of Revenue's public NAL files. See `skill/references/data-sources.md`.

## Contents

```
skill/
  SKILL.md                      workflow and ground rules
  references/
    amendment3.md               what HJR 1-F actually says
    legal-framework.md          fee / assessment / tax tests, verified authorities
    revenue-options.md          catalog of replacement tools
    procedure.md                enactment, uniform method, calendar
    data-sources.md             where to get the data
    nal-fields.md               tax roll fields used
  scripts/exemption_impact.py   parcel-level exemption impact calculator
  templates/                    starting drafts of the adopting documents
```

## Caveats

This is not legal advice. The legal references were checked on the date shown in each file, and statutes and cases change. A Florida-licensed attorney must review every draft before anything is adopted.
