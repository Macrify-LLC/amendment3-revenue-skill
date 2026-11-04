# Florida Amendment 3 Revenue Replacement Skill

A free AI skill for Florida counties and cities working through the 2026 Amendment 3 homestead exemption.

**Website:** [amendment3.macrify.me](https://amendment3.macrify.me) · **Worked example:** [the Largo session](https://amendment3.macrify.me/largo/session.html)

Give it the government's adopted budget and the state tax roll. It will:

1. Measure the property tax revenue the exemption takes away, parcel by parcel, and check the result against the government's own estimate.
2. Go through the government's programs with you. Amendment 3 also limits what property tax can be spent on. For each program that seems to fall outside those uses, you decide whether you agree. If you do, you choose whether to redesign it, fund it another way, shrink it, or stop it.
3. Put together two or three packages to compare, showing what each keeps or cuts and what typical homes and businesses would pay. Replacement revenue candidates (special assessments, user fees and others) come with the governing legal tests, the cost base, apportionment, sample rates, and who pays more and who pays less.
4. Lay out the adoption calendar. The tax-bill deadline for a new assessment comes early: a resolution of intent before January 1, or March 1 by agreement.
5. Draft the resolutions, ordinances, notices and supporting studies as Word files. It fills in as many blanks as the record allows, uses Word's own section numbering and bullets, and highlights everything still open.

**It does not decide what is legally allowable.** It sets out the tests and the record. The attorney using it makes every legal call, and every draft is marked for counsel's review.

## See it in action

We ran the skill on the City of Largo using only public records: the state tax roll, the City's website and budget documents, news coverage, and state law. In 18 minutes it went from one question to 16 draft documents.
- [Full transcript](https://amendment3.macrify.me/largo/session.html)
- [The drafts](https://amendment3.macrify.me/#documents)

It was an independent demonstration. It was not commissioned, reviewed or endorsed by the City of Largo.

## Install

Download `florida-amendment3-revenue-replacement-<version>.zip` from [Releases](../../releases), or use the `skill/` folder from this repository.

- **Claude (desktop app or claude.ai):** Settings → Capabilities → Skills → upload the zip. Then start a conversation, for example: *"Estimate how much property tax revenue my city will lose from Amendment 3 and help me save as many programs as possible."*
- **Claude Code:** copy `skill/` to `~/.claude/skills/florida-amendment3-revenue-replacement/`.
- **ChatGPT or another assistant:**
  - Upload `skill/SKILL.md` and the `references/` and `templates/` files to a project, or paste `SKILL.md` in as the instructions.
  - The scripts need an assistant that can run Python, or you can run them yourself.

The scripts need Python 3 and nothing else. The tax roll is the Florida Department of Revenue's public NAL file for your county; see `skill/references/data-sources.md`.

**Before you start:** in Florida, a chat about government business is likely a public record (ch. 119, Fla. Stat.). Keep it, and leave out anything confidential or privileged. Board members shouldn't share or discuss it with each other outside a noticed meeting (s. 286.011).

## Contents

```
skill/
  SKILL.md                      workflow and ground rules
  references/
    amendment3.md               what HJR 1-F actually says
    program-screen.md           program-by-program uses, priorities and options
    legal-framework.md          fee / assessment / tax tests, verified authorities
    revenue-options.md          catalog of replacement tools
    procedure.md                enactment, uniform method, calendar
    counties.md                 what is different for counties
    data-sources.md             where to get the data
    nal-fields.md               tax roll fields used
  scripts/
    exemption_impact.py         parcel-level exemption impact calculator
    incidence.py                revenue and who pays more / less for a package
    make_docx.py                Markdown draft -> Word file with real numbering
                                and highlighted open items
  templates/                    decision log, staff data requests, county letter,
                                and starting drafts of the adopting documents
site/                           the amendment3.macrify.me website and the Largo example
```

## Status

Release candidate. The legal references were checked against primary sources on the date shown in each file (November 2026). Statutes, implementing legislation and cases will change; the skill tells the user to re-check before relying on them.

Found a legal error, an outdated citation, or a bug? [Open an issue](../../issues). Corrections to the legal references are especially welcome.

## Not legal advice

This is not legal advice and creates no attorney-client relationship. The skill and its drafts are starting points. A Florida-licensed attorney must review every legal question and every document before anything is adopted.

## License

MIT. See [LICENSE](LICENSE). Published by [Macrify LLC](https://macrify.me).
