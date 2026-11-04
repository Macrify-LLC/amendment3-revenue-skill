#!/usr/bin/env python3
"""Build the Largo example pages for the site from a demo session folder.

    python build_largo.py <demo-folder> <site-folder>

Reads <demo-folder>/largo-session.jsonl and <demo-folder>/Largo-Amendment3-Drafts/*.docx.
Writes:
    <site>/largo/session.html    readable transcript (messages + summarized steps)
    <site>/largo/docs/*.docx     the drafts, each stamped as an independent demonstration
    <site>/largo/largo-drafts.zip
Requires python-docx (only for stamping the drafts).
"""
import datetime as dt
import glob
import html
import json
import os
import re
import sys
import zipfile
from urllib.parse import urlparse

DEMO, SITE = sys.argv[1], sys.argv[2]
OUT = os.path.join(SITE, "largo")
os.makedirs(os.path.join(OUT, "docs"), exist_ok=True)

STAMP = ("INDEPENDENT DEMONSTRATION. Drafted by an AI skill in a simulated conversation, using only public records, "
         "to show how the Florida Amendment 3 revenue skill works (amendment3.macrify.me). Not prepared by, for, or "
         "with the City of Largo, and not reviewed or endorsed by it. Not legal advice. The \"resident\" in these "
         "drafts is the role played in the demonstration.")


# ------------------------------------------------------------------ transcript

def T(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="nofollow">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def md(text):
    """Small Markdown renderer for the assistant's replies: headings, lists, tables, paragraphs."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            lvl = min(len(m.group(1)) + 2, 5)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if not re.match(r"^\|?\s*:?-{2,}", r):
                    rows.append([c.strip() for c in r.strip("|").split("|")])
                i += 1
            t = ['<div class="tbl"><table>']
            for k, r in enumerate(rows):
                tag = "th" if k == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
            t.append("</table></div>")
            out.append("".join(t)); continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", ln)
        if m:
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items, base = [], len(m.group(1))
            while i < len(lines):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", lines[i])
                if mm and len(mm.group(1)) <= base:
                    items.append([mm.group(3), []]); i += 1
                elif mm or (lines[i].startswith("  ") and lines[i].strip() and items):
                    items[-1][1].append(lines[i]); i += 1
                else:
                    break
            h = [f"<{tag}>"]
            for head, sub in items:
                h.append("<li>" + inline(head) + (md("\n".join(x[3:] if x.startswith("   ") else x.strip() for x in sub)) if sub else "") + "</li>")
            h.append(f"</{tag}>")
            out.append("".join(h)); continue
        para = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*([-*]|\d+\.)\s)", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def describe(name, inp):
    """One plain line per tool call. Tool output is never republished."""
    cmd = inp.get("command", "") if isinstance(inp, dict) else ""
    if name == "WebSearch":
        return "Searched the web", inp.get("query", "")
    if name == "WebFetch":
        u = inp.get("url", "")
        p = urlparse(u)
        return "Read a public web page", f'<a href="{html.escape(u)}" rel="nofollow">{html.escape(p.netloc + p.path)[:90]}</a>'
    if name in ("Write", "Edit"):
        base = os.path.basename(inp.get("file_path", ""))
        return ("Wrote" if name == "Write" else "Revised"), html.escape(base)
    if name == "Read":
        return "Checked its work", "looked at a rendered page" if inp.get("file_path", "").endswith(".jpg") else "read its notes"
    if name == "Skill":
        return "Loaded a skill", "Word document tools"
    if name == "TaskCreate":
        return "Planned a step", html.escape(inp.get("subject", ""))
    if name == "mcp__remote-devices__device_bash":
        if "curl" in cmd:
            return "Downloaded public records", "budget documents into the folder"
        return "Looked in the folder", "listed the files provided"
    if name == "mcp__remote-devices__device_stage_files":
        return "Opened the tax roll", "Pinellas County 2026 final roll (Florida DOR)"
    if name == "mcp__remote-devices__device_commit_files":
        return "Saved to the folder", f'{len(inp.get("files", []))} file(s)'
    if name == "Bash":
        if "exemption_impact.py" in cmd:
            return "Ran the exemption calculator", "parcel by parcel on the state tax roll"
        if "incidence.py" in cmd:
            return "Ran the who-pays calculator", "typical homes and businesses under each package"
        if "unzip" in cmd:
            return "Unpacked the tax roll", ""
        if "conv.js" in cmd or "docx" in cmd:
            return "Built the Word files", ""
        if "/mnt/user-data/outputs" in cmd:
            return "Saved results", ""
        if "references" in cmd or "SKILL" in cmd or "cat " in cmd:
            return "Read the skill's references", ""
        if ".claude/projects" in cmd:
            return None
        return "Ran a calculation", ""
    return None


rows = [json.loads(l) for l in open(os.path.join(DEMO, "largo-session.jsonl"), encoding="utf-8") if l.strip()]
start = T(next(r["timestamp"] for r in rows if r.get("timestamp")))
events = []  # (kind, time, payload)
for r in rows:
    t = r.get("type")
    if t == "user" and r.get("message"):
        c = r["message"]["content"]
        texts = [c] if isinstance(c, str) else [b.get("text", "") for b in c if b.get("type") == "text"]
        for s in texts:
            if not s.strip() or s.startswith("<system-reminder>"):
                continue
            m = re.search(r"<command-args>(.*?)</command-args>", s, re.S)
            if m:
                events.append(("note", r["timestamp"], "Started the skill: Florida Amendment 3 Revenue Replacement"))
                events.append(("user", r["timestamp"], m.group(1).strip()))
            elif s.startswith("Base directory for this skill"):
                continue
            elif "transcript file" in s:
                continue  # the request to save this log
            else:
                events.append(("user", r["timestamp"], s.strip()))
    elif t == "assistant":
        for b in r["message"]["content"]:
            if b.get("type") == "text" and b["text"].strip():
                events.append(("assistant", r["timestamp"], b["text"]))
            elif b.get("type") == "tool_use":
                d = describe(b["name"], b["input"])
                if d:
                    events.append(("step", r["timestamp"], d))

# group steps
blocks, steps = [], []
for kind, ts, p in events:
    if kind == "step":
        steps.append((ts, p)); continue
    if steps:
        blocks.append(("steps", steps)); steps = []
    blocks.append((kind, (ts, p)))
if steps:
    blocks.append(("steps", steps))



def stamp(ts):
    m = int((T(ts) - start).total_seconds() // 60)
    return f"{m} min"


body = []
for kind, data in blocks:
    if kind == "steps":
        n = len(data)
        lis = "".join(
            f'<li><span class="t">{stamp(ts)}</span> <strong>{html.escape(a)}</strong>'
            f'{": " + b if b else ""}</li>' for ts, (a, b) in data)
        label = f"{n} step{'s' if n != 1 else ''}: " + ", ".join(sorted({a.lower() for _, (a, _b) in data}))[:140]
        body.append(f'<details class="steps"><summary>{html.escape(label)}</summary><ul>{lis}</ul></details>')
    elif kind == "note":
        body.append(f'<p class="note">{html.escape(data[1])}</p>')
    elif kind == "user":
        body.append(f'<div class="msg user"><div class="who">Person using the skill <span class="t">{stamp(data[0])}</span></div>'
                    f'<p>{inline(data[1])}</p></div>')
    else:
        body.append(f'<div class="msg ai"><div class="who">Claude, using the skill <span class="t">{stamp(data[0])}</span></div>'
                    f'{md(data[1])}</div>')

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Largo Session Transcript</title>
<meta name="description" content="The full conversation in which the Florida Amendment 3 revenue skill analyzed the City of Largo using public records.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=Public+Sans:ital,wght@0,400;0,600;0,800;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="session.css">
</head><body>
<div class="strip"><div class="wrap"><a href="/">Amendment 3 Revenue Skill</a><span>Independent demonstration. Not legal advice.</span></div></div>
<header class="wrap head">
<h1>The Largo session</h1>
<p class="lede">The complete conversation, as it happened on November 4, 2026. Messages are shown word for word. The steps Claude took in between (searches, pages read, calculations, files written) are listed under each "steps" line; open one to see them. Times count from the start of the session.</p>
<p class="fine">The person using the skill played an interested citizen, not a City employee. The session used only public records: the state tax roll, the City's website and budget documents, news coverage, and state law. It was not commissioned, reviewed or endorsed by the City of Largo, and nothing in it is advice to the City. The drafts it produced are <a href="/#documents">on the main page</a>.</p>
</header>
<main class="wrap convo">
{chr(10).join(body)}
<p class="note">End of session. The person then asked Claude to save this transcript.</p>
</main>
<footer><div class="wrap"><p>Published by <a href="https://macrify.me">Macrify LLC</a>. Not affiliated with any Florida government. Not legal advice.</p></div></footer>
</body></html>"""
open(os.path.join(OUT, "session.html"), "w", encoding="utf-8").write(page)
print("session.html:", sum(1 for b in blocks if b[0] in ("user", "assistant")), "messages,",
      sum(len(b[1]) for b in blocks if b[0] == "steps"), "steps")

# ------------------------------------------------------------------ drafts
try:
    import docx
except ImportError:
    sys.exit("python-docx is needed to stamp the drafts")
from docx.enum.text import WD_COLOR_INDEX

names = []
for f in sorted(glob.glob(os.path.join(DEMO, "Largo-Amendment3-Drafts", "*.docx"))):
    d = docx.Document(f)
    p = d.paragraphs[0].insert_paragraph_before()
    run = p.add_run(STAMP)
    run.bold = True
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    slug = re.sub(r"[^A-Za-z0-9]+", "-", os.path.basename(f)[:-5]).strip("-")
    out = os.path.join(OUT, "docs", slug + ".docx")
    d.save(out)
    names.append((slug, out))
with zipfile.ZipFile(os.path.join(OUT, "largo-drafts.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for slug, out in names:
        z.write(out, f"Largo-Amendment3-Drafts/{slug}.docx")
print("drafts:", ", ".join(s for s, _ in names))
