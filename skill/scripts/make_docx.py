#!/usr/bin/env python3
"""Turn a Markdown draft into a Word (.docx) file. Standard library only.

Why this exists: attorneys edit drafts in Word. A draft whose numbers and
bullets are typed characters ("1.", "(a)", "•") falls apart the moment someone
inserts a section. This converter uses Word's own list numbering, so sections,
subsections and bullets renumber themselves when the document is edited. It
also highlights every open item so nothing gets adopted with a blank in it.

Usage:
    python make_docx.py draft.md "01 Resolution of Intent.docx"
    python make_docx.py draft.md out.docx --font "Times New Roman" --size 12 --no-key

Markdown it understands:
    # Title                      centered bold title
    ## Heading / ### Subheading  bold headings
    § **RECITALS.** Text          a numbered SECTION paragraph ("SECTION 1.",
                                 "SECTION 2." ... numbered by Word)
    1. item / 2. item            a numbered list. Once a § paragraph has appeared
                                 (until the next # / ## heading or ---), list
                                 items become that section's (a), (b), (c), and
                                 nested items (1), (2), (3). Elsewhere they are
                                 1., 2., 3. with (a)/(i) for nested levels.
    - item / * item              bullets (indent two spaces to nest)
    > text                       a shaded box (use it for the plain-language summary)
    | a | b |                    a table (first row is the header)
    ---                          page break (put drafting notes after one)
    **bold**  *italic*  `code`
    a line ending in two spaces  forces a line break (signature blocks)

Highlighting (automatic):
    [ANY BRACKETED TEXT]               yellow: a fact still to be filled in
    {City|County}                      yellow: a choice still to be made
    [COUNSEL DETERMINATION ...]        turquoise: a legal judgment for counsel
    [[CONFIRM: value]]                 green: filled in from a source, but the
                                       user should confirm it (brackets dropped,
                                       the value stays)
    [link text](url)                   rendered as plain link text, not highlighted

It prints a count of each kind of open item, and the yellow items themselves, so
they can be listed in the plan memo.
"""
import argparse
import datetime
import re
import sys
import zipfile
from xml.sax.saxutils import escape

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

BULLET_ABS, DECIMAL_ABS, SECTION_ABS = 1, 2, 3
BULLET_NUM, SECTION_NUM = 1, 2  # decimal lists get fresh numIds from 3 up


# ---------------------------------------------------------------- inline text

def parse_inline(text, open_items):
    """Return runs: list of (text, bold, italic, highlight, line_break_after)."""
    runs = []
    bold = italic = False
    hl_stack = []
    buf = []

    def flush():
        if buf:
            runs.append(["".join(buf), bold, italic, hl_stack[-1] if hl_stack else None])
            buf.clear()

    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n and text[i + 1] in "[]*`{}\\|":
            buf.append(text[i + 1]); i += 2; continue
        if c == "`":  # strip backticks, keep content (brackets inside still highlight)
            i += 1; continue
        if text.startswith("**", i):
            flush(); bold = not bold; i += 2; continue
        if c == "*" and (i + 1 < n and not text[i + 1].isspace() or italic):
            flush(); italic = not italic; i += 1; continue
        if text.startswith("[[CONFIRM:", i):
            end = text.find("]]", i)
            if end != -1:
                flush()
                value = text[i + len("[[CONFIRM:"):end].strip()
                open_items["confirm"].append(value)
                hl_stack.append("green")
                runs.extend(parse_inline_plain(value, bold, italic, "green"))
                hl_stack.pop()
                i = end + 2; continue
        if c == "[":
            end = _match(text, i, "[", "]")
            if end != -1 and end + 1 < n and text[end + 1] == "(":
                close = text.find(")", end + 1)
                if close != -1:  # markdown link: keep the text only
                    flush()
                    runs.extend(parse_inline(text[i + 1:end], {"yellow": [], "cyan": [], "confirm": []}))
                    i = close + 1; continue
            if end != -1:
                flush()
                inner = text[i + 1:end]
                color = hl_stack[-1] if hl_stack else (
                    "cyan" if inner.lstrip().upper().startswith("COUNSEL") else "yellow")
                if not hl_stack:
                    open_items[color].append(inner.strip())
                hl_stack.append(color)
                buf.append("[")
                sub = parse_inline(inner, {"yellow": [], "cyan": [], "confirm": []})
                flush()
                for r in sub:
                    runs.append([r[0], r[1] or bold, r[2] or italic, color])
                buf.append("]")
                flush()
                hl_stack.pop()
                i = end + 1; continue
        if c == "{":
            end = text.find("}", i)
            if end != -1 and "|" in text[i:end]:
                flush()
                if not hl_stack:
                    open_items["yellow"].append(text[i:end + 1])
                runs.append([text[i:end + 1], bold, italic, hl_stack[-1] if hl_stack else "yellow"])
                i = end + 1; continue
        buf.append(c); i += 1
    flush()
    return runs


def parse_inline_plain(text, bold, italic, hl):
    return [[text, bold, italic, hl]]


def _match(text, start, open_c, close_c):
    depth = 0
    for j in range(start, len(text)):
        if text[j] == "\\":
            continue
        if text[j] == open_c:
            depth += 1
        elif text[j] == close_c:
            depth -= 1
            if depth == 0:
                return j
    return -1


def runs_xml(segments, base_bold=False):
    """segments: list of (text, bold, italic, hl) or "BR" for a line break."""
    out = []
    for seg in segments:
        if seg == "BR":
            out.append("<w:r><w:br/></w:r>")
            continue
        t, b, it, hl = seg
        if not t:
            continue
        rpr = []
        if b or base_bold:
            rpr.append("<w:b/>")
        if it:
            rpr.append("<w:i/>")
        if hl:
            rpr.append(f'<w:highlight w:val="{hl}"/>')
        rpr_xml = f"<w:rPr>{''.join(rpr)}</w:rPr>" if rpr else ""
        out.append(f'<w:r>{rpr_xml}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>')
    return "".join(out)


def inline_with_breaks(lines, open_items):
    segs = []
    for k, line in enumerate(lines):
        hard = line.endswith("  ") or line.endswith("\\")
        content = line.rstrip("\\").strip()
        segs.extend(parse_inline(content, open_items))
        if k < len(lines) - 1:
            segs.append("BR" if hard else [" ", False, False, None])
    return segs


# ---------------------------------------------------------------- paragraphs

def para(segments, style=None, num=None, align=None, keep_next=False, base_bold=False,
         shade=False, page_break_before=False):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        ppr.append("<w:keepNext/>")
    if page_break_before:
        ppr.append("<w:pageBreakBefore/>")
    if num:
        ppr.append(f'<w:numPr><w:ilvl w:val="{num[1]}"/><w:numId w:val="{num[0]}"/></w:numPr>')
    if shade:
        ppr.append('<w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="808080"/></w:pBdr>'
                   '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>'
                   '<w:ind w:left="240" w:right="240"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{runs_xml(segments, base_bold)}</w:p>"


def table_xml(rows, open_items):
    ncols = max(len(r) for r in rows)
    width = 9360 // ncols
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in range(ncols))
    out = [f'<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="5000" w:type="pct"/>'
           f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>']
    for ri, row in enumerate(rows):
        trpr = "<w:trPr><w:tblHeader/></w:trPr>" if ri == 0 else ""
        out.append(f"<w:tr>{trpr}")
        for ci in range(ncols):
            cell = row[ci] if ci < len(row) else ""
            segs = parse_inline(cell.strip(), open_items)
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>' if ri == 0 else ""
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}</w:tcPr>'
                       f'{para(segs, style="TableText", base_bold=(ri == 0))}</w:tc>')
        out.append("</w:tr>")
    out.append("</w:tbl>")
    out.append(para([]))  # Word needs a paragraph between a table and what follows
    return "".join(out)


LIST_RE = re.compile(r"^(\s*)([-*+•]|\d+[.)]|[a-z][.)])\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def convert(md, open_items):
    lines = md.replace("\r\n", "\n").split("\n")
    body = []
    decimal_nums = []          # numIds created for separate numbered lists
    next_num = [3]
    in_section = False         # a § paragraph has been seen since the last heading
    current_list_num = None    # numId of the numbered list in progress
    indent_stack = []          # indentation of open list levels
    pending_break = False
    i = 0

    def end_list():
        nonlocal current_list_num
        current_list_num = None
        indent_stack.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            # a blank line ends a list only if the next non-blank line is not a list item
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or not LIST_RE.match(lines[j]):
                end_list()
            i += 1
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            pending_break = True
            in_section = False
            end_list()
            i += 1
            continue

        def take_break():
            nonlocal pending_break
            b, pending_break = pending_break, False
            return b

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            end_list()
            level = len(m.group(1))
            in_section = False if level <= 2 else in_section
            segs = parse_inline(m.group(2), open_items)
            style = {1: "Title", 2: "Heading1", 3: "Heading2", 4: "Heading3"}[level]
            body.append(para(segs, style=style, keep_next=True, page_break_before=take_break()))
            i += 1
            continue

        if stripped.startswith("|"):
            end_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = lines[i].strip()
                if not TABLE_SEP_RE.match(row):
                    cells = [c for c in re.split(r"(?<!\\)\|", row.strip("|"))]
                    rows.append(cells)
                i += 1
            if take_break():
                body.append(para([], page_break_before=True))
            body.append(table_xml(rows, open_items))
            continue

        if stripped.startswith(">"):
            end_list()
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].strip())
                i += 1
            paras, cur = [], []
            for b in block:
                if not b:
                    if cur:
                        paras.append(cur); cur = []
                else:
                    cur.append(b)
            if cur:
                paras.append(cur)
            brk = take_break()
            for k, p in enumerate(paras):
                body.append(para(inline_with_breaks(p, open_items), style="Summary", shade=True,
                                 page_break_before=brk and k == 0))
            continue

        if stripped.startswith("§"):
            end_list()
            in_section = True
            text = [stripped[1:].strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i])                     and not LIST_RE.match(lines[i]):
                text.append(lines[i]); i += 1
            body.append(para(inline_with_breaks(text, open_items), style="Section",
                             num=(SECTION_NUM, 0), page_break_before=take_break()))
            continue

        m = LIST_RE.match(line)
        if m:
            indent = len(m.group(1).expandtabs(4))
            while indent_stack and indent < indent_stack[-1]:
                indent_stack.pop()
            if not indent_stack or indent > indent_stack[-1]:
                indent_stack.append(indent)
            level = min(len(indent_stack) - 1, 2)
            marker = m.group(2)
            text = [m.group(3)]
            i += 1
            # continuation lines: indented, non-blank, not a new item
            while i < len(lines) and lines[i].strip() and not LIST_RE.match(lines[i]) \
                    and not _is_block_start(lines[i]) and lines[i].startswith(" "):
                text.append(lines[i]); i += 1
            segs = inline_with_breaks(text, open_items)
            if marker in "-*+•":
                num = (BULLET_NUM, level)
            elif in_section:
                num = (SECTION_NUM, min(level + 1, 2))
            else:
                if current_list_num is None:
                    current_list_num = next_num[0]
                    decimal_nums.append(current_list_num)
                    next_num[0] += 1
                num = (current_list_num, level)
            body.append(para(segs, style="ListParagraph", num=num, page_break_before=take_break()))
            continue

        # ordinary paragraph: gather until blank line or block start
        end_list()
        text = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]) \
                and not LIST_RE.match(lines[i]):
            text.append(lines[i]); i += 1
        body.append(para(inline_with_breaks(text, open_items), page_break_before=take_break()))

    return "".join(body), decimal_nums


def _is_block_start(line):
    s = line.strip()
    return (s.startswith("#") or s.startswith("|") or s.startswith(">") or s.startswith("§")
            or re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s) is not None)


# ---------------------------------------------------------------- package parts

def lvl(ilvl, fmt, text, left, hanging, bold=False, suff=None, font=None):
    rpr = ""
    parts = []
    if bold:
        parts.append("<w:b/>")
    if font:
        parts.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:hint="default"/>')
    if parts:
        rpr = f"<w:rPr>{''.join(parts)}</w:rPr>"
    suff_xml = f'<w:suff w:val="{suff}"/>' if suff else ""
    return (f'<w:lvl w:ilvl="{ilvl}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>{suff_xml}'
            f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="left"/>'
            f'<w:pPr><w:ind w:left="{left}" w:hanging="{hanging}"/></w:pPr>{rpr}</w:lvl>')


def numbering_xml(decimal_nums):
    bullets = "".join([
        lvl(0, "bullet", "•", 720, 360),
        lvl(1, "bullet", "◦", 1440, 360),
        lvl(2, "bullet", "▪", 2160, 360),
    ])
    decimal = "".join([
        lvl(0, "decimal", "%1.", 720, 360),
        lvl(1, "lowerLetter", "(%2)", 1440, 360),
        lvl(2, "lowerRoman", "(%3)", 2160, 360),
    ])
    sections = "".join([
        lvl(0, "decimal", "SECTION %1.", 0, 0, bold=True, suff="space"),
        lvl(1, "lowerLetter", "(%2)", 1080, 360),
        lvl(2, "decimal", "(%3)", 1800, 360),
    ])
    abstracts = (
        f'<w:abstractNum w:abstractNumId="{BULLET_ABS}"><w:multiLevelType w:val="hybridMultilevel"/>{bullets}</w:abstractNum>'
        f'<w:abstractNum w:abstractNumId="{DECIMAL_ABS}"><w:multiLevelType w:val="multilevel"/>{decimal}</w:abstractNum>'
        f'<w:abstractNum w:abstractNumId="{SECTION_ABS}"><w:multiLevelType w:val="multilevel"/>{sections}</w:abstractNum>'
    )
    nums = (f'<w:num w:numId="{BULLET_NUM}"><w:abstractNumId w:val="{BULLET_ABS}"/></w:num>'
            f'<w:num w:numId="{SECTION_NUM}"><w:abstractNumId w:val="{SECTION_ABS}"/></w:num>')
    for nid in decimal_nums:  # each separate list restarts at 1
        overrides = "".join(f'<w:lvlOverride w:ilvl="{k}"><w:startOverride w:val="1"/></w:lvlOverride>'
                            for k in range(3))
        nums += f'<w:num w:numId="{nid}"><w:abstractNumId w:val="{DECIMAL_ABS}"/>{overrides}</w:num>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering xmlns:w="{W_NS}">{abstracts}{nums}</w:numbering>'


def styles_xml(font, size):
    hs = size * 2
    def style(sid, name, ppr="", rpr="", based="Normal", typ="paragraph"):
        b = f'<w:basedOn w:val="{based}"/>' if based else ""
        default = ' w:default="1"' if sid == "Normal" else ""
        return (f'<w:style w:type="{typ}"{default} w:styleId="{sid}"><w:name w:val="{name}"/>{b}'
                f'<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')
    return (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="{W_NS}">'
        f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" '
        f'w:eastAsia="{font}" w:cs="{font}"/><w:sz w:val="{hs}"/><w:szCs w:val="{hs}"/>'
        f'<w:lang w:val="en-US"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>'
        f'<w:spacing w:after="200" w:line="240" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault></w:docDefaults>'
        + style("Normal", "Normal", based=None)
        + style("Title", "Title", '<w:jc w:val="center"/><w:spacing w:after="240"/>', f'<w:b/><w:sz w:val="{hs + 4}"/>')
        + style("Heading1", "heading 1", '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:jc w:val="left"/><w:outlineLvl w:val="0"/>', f'<w:b/><w:sz w:val="{hs + 2}"/>')
        + style("Heading2", "heading 2", '<w:keepNext/><w:spacing w:before="200" w:after="100"/><w:jc w:val="left"/><w:outlineLvl w:val="1"/>', "<w:b/>")
        + style("Heading3", "heading 3", '<w:keepNext/><w:spacing w:before="160" w:after="80"/><w:jc w:val="left"/><w:outlineLvl w:val="2"/>', "<w:b/><w:i/>")
        + style("Section", "Ordinance Section", "")
        + style("ListParagraph", "List Paragraph", '<w:spacing w:after="120"/><w:contextualSpacing/>')
        + style("Summary", "Plain-Language Summary", '<w:spacing w:after="120"/><w:jc w:val="left"/>')
        + style("TableText", "Table Text", '<w:spacing w:after="0"/><w:jc w:val="left"/>', f'<w:sz w:val="{hs - 2}"/>')
        + '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr>'
          '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="auto"/><w:left w:val="single" w:sz="4" w:color="auto"/>'
          '<w:bottom w:val="single" w:sz="4" w:color="auto"/><w:right w:val="single" w:sz="4" w:color="auto"/>'
          '<w:insideH w:val="single" w:sz="4" w:color="auto"/><w:insideV w:val="single" w:sz="4" w:color="auto"/>'
          '</w:tblBorders><w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>'
          '</w:tblPr></w:style>'
        + "</w:styles>"
    )


def key_xml():
    segs = [
        ["Draft for review. ", True, False, None],
        ["Yellow", False, False, "yellow"], [" marks a fact still to be filled in. ", False, False, None],
        ["Turquoise", False, False, "cyan"], [" marks a legal judgment for counsel. ", False, False, None],
        ["Green", False, False, "green"], [" marks a fact filled in from a source that should be confirmed. "
                                           "Delete this note, the highlighting and the drafting notes before use.",
                                           False, False, None],
    ]
    return para(segs, style="Summary", shade=True)


def build(md, out_path, font, size, key, title):
    open_items = {"yellow": [], "cyan": [], "confirm": []}
    body, decimal_nums = convert(md, open_items)
    if key:
        body = key_xml() + body
    sect = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" '
            'w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W_NS}" '
                f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<w:body>{body}{sect}</w:body></w:document>')
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = {
        "[Content_Types].xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            '</Types>',
        "_rels/.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>',
        "word/_rels/document.xml.rels":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
            '</Relationships>',
        "word/document.xml": document,
        "word/styles.xml": styles_xml(font, size),
        "word/numbering.xml": numbering_xml(decimal_nums),
        "word/settings.xml":
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="{W_NS}">'
            '<w:defaultTabStop w:val="720"/><w:compat><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>',
        "docProps/core.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{escape(title)}</dc:title><dc:creator>Draft</dc:creator>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
            '</cp:coreProperties>',
        "docProps/app.xml":
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
            '<Application>make_docx.py</Application></Properties>',
    }
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return open_items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("output")
    ap.add_argument("--font", default="Times New Roman")
    ap.add_argument("--size", type=int, default=12)
    ap.add_argument("--no-key", action="store_true", help="omit the highlight key at the top")
    ap.add_argument("--title", help="document title property (default: output file name)")
    a = ap.parse_args()
    try:  # Windows consoles default to a code page that can't print every character
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    with open(a.markdown, encoding="utf-8") as f:
        md = f.read()
    title = a.title or re.sub(r"\.docx$", "", a.output.replace("\\", "/").split("/")[-1])
    items = build(md, a.output, a.font, a.size, not a.no_key, title)
    print(f"Wrote {a.output}")
    print(f"  facts still to fill (yellow): {len(items['yellow'])}")
    print(f"  counsel determinations (turquoise): {len(items['cyan'])}")
    print(f"  filled, to confirm (green): {len(items['confirm'])}")
    seen = set()
    for item in items["yellow"]:
        if item not in seen:
            seen.add(item)
            print(f"    - [{item or ' '}]" if not item.startswith("{") else f"    - {item}")


if __name__ == "__main__":
    sys.exit(main())
