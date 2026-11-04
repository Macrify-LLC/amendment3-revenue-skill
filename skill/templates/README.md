# Templates

These are starting drafts, not forms to adopt as-is. Fill in as many blanks as the conversation and public sources allow before handing a draft over (SKILL.md, Phase 5). Conventions:
- `[BRACKETS]` = a fact still to fill in (highlighted yellow in Word). Fill it from a cited source. Never fill one with a guess.
- `[[CONFIRM: value]]` = a fact filled in from a source that the user should double-check (green).
- `[COUNSEL DETERMINATION: …]` = a legal judgment for the attorney (turquoise).
- `{County|City}` = pick the government type (yellow until resolved). Section references assume a municipality. Swap in s. 125.66 / ch. 125 for a county.
- Follow the local charter, code, and preferred form (recitals, signature blocks, attestation). These templates use a generic layout.

Markdown syntax for `scripts/make_docx.py`, which builds the Word file with Word's own numbering:
- `# ORDINANCE NO. [__]`: centered title. `##` / `###`: headings.
- `§ **HEADING.** Text`: a numbered section (Word numbers it SECTION 1, 2, 3…).
- `1.` list items after a section become its (a), (b), (c), and indented ones (1), (2), (3). Elsewhere they are 1, 2, 3. Write `1.` for every item; Word does the counting.
- `-` items are bullets. `>` lines are the shaded plain-language summary. `|` rows are a table. `---` starts a new page (put the drafting notes after it). End a line with two spaces to keep a line break (signature blocks).

Working documents, used throughout:
- `00-decision-log.md`: every decision the user makes, with reasons. It becomes the public record trail and the start of the legislative findings.
- `11-staff-data-requests.md`: numbers that aren't published, as requests to the right department.
- `12-letter-to-county-and-interlocal-terms.md`: when part of the loss sits in another government's levy.

Adopting documents:

| Document | Fire / solid waste / stormwater assessment on the tax bill | Capital improvement (ch. 170) | User fee | Regulatory fee |
|---|---|---|---|---|
| `01-resolution-of-intent.md` (s. 197.3632(3)(a)) | ✔ | ✔ if collected on the tax bill | | |
| `02-notice-of-intent.md` (4-week publication) | ✔ | ✔ if collected on the tax bill | | |
| `03-master-assessment-ordinance.md` | ✔ | optional | | |
| `04-methodology-report-outline.md` | ✔ | ✔ (engineer's report) | | |
| `05-initial-assessment-resolution.md` | ✔ | use s. 170.03 resolution | | |
| `06-roll-hearing-notices.md` (s. 197.3632(4)(b)) | ✔ | use s. 170.07 notice | | |
| `07-final-assessment-resolution.md` | ✔ | use s. 170.08 | | |
| `08-fee-ordinance-and-cost-study.md` | | | ✔ | ✔ |
| `09-business-impact-estimate.md` | ✔ (ordinance) | ✔ | ✔ | ✔ |
| `10-agenda-memo-and-faq.md` | ✔ | ✔ | ✔ | ✔ |
