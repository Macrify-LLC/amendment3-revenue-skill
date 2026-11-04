# Changelog

## 0.1.0-rc2 (2026-11-04)

- Drafts are filled in from the conversation and public sources before any blank is left. Each filled-in fact is cited, facts to double-check are marked `[[CONFIRM: ...]]`, and the skill asks for the rest.
- New `scripts/make_docx.py` (standard library only). It turns a Markdown draft into a Word file that uses Word's own numbering (SECTION 1, (a), (1)) and bullets, and highlights open items: yellow for a fact to fill in, turquoise for a counsel determination, green for a fact to confirm.
- Templates converted to the numbered-section syntax.

## 0.1.0-rc1 (2026-11-04)

- First release candidate. Tested on the City of Largo; see the [transcript](https://amendment3.macrify.me/largo/session.html).
- Workflow:
  - intake;
  - measure the loss (`exemption_impact.py`);
  - program screen;
  - two or three packages with incidence (`incidence.py`);
  - draft documents;
  - plan memo.
- References: Amendment 3 text, legal tests with verified authorities, procedure and calendar, revenue options, counties, data sources.
- Templates: 14 starting drafts, from the resolution of intent through the final assessment resolution, plus a decision log, staff data requests and a county letter.
