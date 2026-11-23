"""Build the hackathon deck with python-pptx. Usage: python build_deck.py <repo_root> <out.pptx>"""

import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

REPO = Path(sys.argv[1])
OUT = sys.argv[2]
DEMO = REPO / "presentation/current-demo"

# Palette: deep indigo ink, blue-violet, lavender tints, one warm coral accent.
DEEP = RGBColor(0x2A, 0x29, 0x6B)
TEAL = RGBColor(0x46, 0x50, 0xC4)
PURPLE = RGBColor(0x7B, 0x5C, 0xD6)
MIST = RGBColor(0xEE, 0xF0, 0xFB)
MIST2 = RGBColor(0xCF, 0xD4, 0xF4)
CORAL = RGBColor(0xC8, 0x55, 0x3D)
CORAL_T = RGBColor(0xFB, 0xEC, 0xE8)
INK = RGBColor(0x1E, 0x2A, 0x32)
MUTED = RGBColor(0x5E, 0x6B, 0x73)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEAD = "Cambria"
BODY = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W = 13.333
_n = [0]


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, space_after=6, line=None):
    """runs: str, or list of paragraphs; a paragraph is str or list of (text, opts) tuples."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        if line:
            p.line_spacing = line
        parts = [(para, {})] if isinstance(para, str) else para
        for t, o in parts:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = o.get("color", color)
    return tb


def box(slide, x, y, w, h, fill=MIST, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.text_frame.text = ""
    return s


def circle_num(slide, x, y, label, d=0.5, fill=TEAL, color=WHITE, size=16):
    s = box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    tf = s.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = BODY, Pt(size), True, color
    return s


def connector(slide, x1, y1, x2, y2, color=MIST2, width=1.75):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    return c


def waves(slide, top, height, colors, n=6):
    """Flowing sine lines across the slide (title and closing slides)."""
    import math

    for k in range(n):
        pts = []
        for i in range(121):
            x = -0.2 + 13.8 * i / 120
            y = top + height * (0.5 + 0.38 * math.sin(i / 120 * 2 * math.pi * 1.1 + k * 0.55)
                                + 0.08 * math.sin(i / 120 * 2 * math.pi * 3 + k))
            pts.append((Inches(x), Inches(y + k * 0.09)))
        ff = slide.shapes.build_freeform(pts[0][0], pts[0][1], scale=1.0)
        ff.add_line_segments(pts[1:], close=False)
        shp = ff.convert_to_shape()
        shp.fill.background()
        shp.shadow.inherit = False
        shp.line.color.rgb = colors[k % len(colors)]
        shp.line.width = Pt(1.5 + (k % 3))


def picture(slide, path, x, y, max_w, max_h, border=True):
    iw, ih = Image.open(path).size
    scale = min(max_w / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    if border:
        frame = box(slide, x - 0.12, y - 0.12, w + 0.24, h + 0.24, fill=WHITE, line=MIST2, radius=0.03)
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    return w, h


def new(title=None, dark=False, notes=None, appendix=False):
    s = prs.slides.add_slide(BLANK)
    bg(s, DEEP if dark else WHITE)
    _n[0] += 1
    if title:
        text(s, 0.65, 0.5, 12.0, 0.9, title, size=32, font=HEAD, bold=True, color=WHITE if dark else DEEP,
             anchor=MSO_ANCHOR.TOP)
    if not dark:
        label = f"Appendix  ·  {_n[0]}" if appendix else str(_n[0])
        text(s, W - 2.65, 7.0, 2.0, 0.3, label, size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


# 1 ─ Title
s = new(dark=True, notes=(
    "I'm Gabriela Piatkowski, a program analyst in NICHD's Obstetric and Pediatric Pharmacology and "
    "Therapeutics Branch. I built this MCP server for the Dataset Access Server track. It gives AI assistants "
    "structured access to public evidence about medicines in pregnancy, breastfeeding and childhood. "
    "This is my own hackathon prototype, not an NIH product."))
waves(s, 6.15, 0.95, [TEAL, PURPLE, RGBColor(0x9A, 0xA4, 0xF0), RGBColor(0xB9, 0xA6, 0xF2)])
text(s, 0.9, 1.0, 9.5, 0.5, "GSA MCP Server and AI Agent Hackathon  ·  Dataset Access Server track",
     size=14, color=MIST2)
text(s, 0.9, 1.55, 11.0, 1.9, ["Parent-child", "Pharmacology MCP"], size=54, font=HEAD, bold=True,
     color=WHITE, space_after=0, line=0.95)
text(s, 0.9, 3.55, 10.0, 1.0,
     "Public evidence on medicines in pregnancy, breastfeeding and childhood, ready for AI assistants",
     size=20, color=MIST2)
text(s, 0.9, 4.6, 9.0, 1.0, [
    [("Gabriela Piatkowski, MS", {"bold": True, "color": WHITE})],
    "Program Analyst, Obstetric and Pediatric Pharmacology and Therapeutics Branch, NICHD",
], size=14, color=MIST2, space_after=2)
text(s, 0.9, 5.5, 11.5, 0.4,
     "Built as a hackathon prototype. Not an official NIH product or medical advice.", size=11,
     color=MIST2, italic=True)

# 2 ─ Hook
s = new(dark=True, notes=(
    "It's 2:07 in the morning. She just found out she's pregnant, and she has taken sertraline for three "
    "years. Her question is simple, and it is one of the most common questions in this field. Finding a "
    "trustworthy answer at that hour is not simple. This is an illustrative question, not a real patient."))
text(s, 0.9, 1.0, 11.5, 1.6, "2:07 a.m.", size=88, font=HEAD, bold=True, color=CORAL_T)
text(s, 0.9, 2.95, 11.0, 2.2,
     "“I just found out I’m pregnant. I’ve taken sertraline for three years. "
     "Is my baby okay? Should I stop?”", size=30, font=HEAD, italic=True, color=WHITE, line=1.1)
text(s, 0.9, 5.45, 11.0, 0.9,
     "Nine in ten women take a medication during pregnancy. Most will ask some version of this question.",
     size=18, color=MIST2)
text(s, 0.9, 6.75, 11.5, 0.4, "Illustrative question, not a real patient. Statistic: CDC, Medicine and Pregnancy.",
     size=11, color=MIST2, italic=True)

# 2b ─ Her night, step by step
s = new("Her night, step by step", notes=(
    "Follow her through the night. At 2:07 she can't sleep. Her doctor's office is closed until morning, and "
    "the after-hours line is for emergencies. A web search gives forums and lists of 'safe' medicines, which "
    "CDC cautions often lack evidence. MotherToBaby is the right service, but after hours it replies the next "
    "business day. LactMed is excellent, but it covers breastfeeding, not pregnancy. The label and PubMed are "
    "written for clinicians. With this MCP, one question to any AI assistant returns the label's pregnancy "
    "section, studies with links, the MotherToBaby fact sheet, registries and studies she could join, and "
    "questions for her doctor, plus MotherToBaby's number for the morning and crisis lines if she needs them "
    "now. It doesn't tell her what to do; it gets her ready for that conversation."))
import math
cx, amp, top, bottom = 4.55, 0.42, 1.75, 6.2
pts = []
for k in range(161):
    y = top + (bottom - top) * k / 160
    pts.append((cx + amp * math.sin(k / 160 * 2 * math.pi * 2.5), y))
ff = s.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
ff.add_line_segments([(Inches(x), Inches(y)) for x, y in pts[1:]], close=False)
path = ff.convert_to_shape()
path.fill.background()
path.shadow.inherit = False
path.line.color.rgb = MIST2
path.line.width = Pt(6)
stops = [
    ("2:07 a.m.", "Can't sleep. Is my baby okay?", CORAL),
    ("Doctor's office", "Closed until 8 a.m.; the after-hours line is for emergencies", TEAL),
    ("Web search", "Forums and “safe” lists that CDC says often lack evidence", TEAL),
    ("MotherToBaby", "The right experts, but after hours they reply the next business day", TEAL),
    ("LactMed", "Excellent, but it covers breastfeeding, not pregnancy", TEAL),
    ("Label and PubMed", "Written for clinicians; studies spread across sites", TEAL),
]
for i, (head, body, color) in enumerate(stops):
    k = int(160 * (0.03 + 0.89 * i / (len(stops) - 1)))
    x, y = pts[k]
    circle_num(s, x - 0.19, y - 0.19, "", d=0.38, fill=color)
    if i % 2 == 0:
        text(s, 0.55, y - 0.32, x - 0.95, 0.35, head, size=14, bold=True, color=DEEP, align=PP_ALIGN.RIGHT)
        text(s, 0.55, y - 0.02, x - 0.95, 0.6, body, size=12, color=INK, align=PP_ALIGN.RIGHT)
    else:
        text(s, x + 0.4, y - 0.32, 8.75 - x - 0.4, 0.35, head, size=14, bold=True, color=DEEP)
        text(s, x + 0.4, y - 0.02, 8.75 - x - 0.4, 0.6, body, size=12, color=INK)
box(s, 0.55, 6.25, 8.3, 0.95, fill=DEEP)
text(s, 0.8, 6.25, 7.85, 0.95, [
    [("With this MCP: ", {"bold": True, "color": WHITE}),
     ("one question returns the label, studies with links, the MotherToBaby fact sheet, registries and "
      "studies she could join, and questions for her doctor, plus who to call.", {"color": MIST2})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE)
picture(s, REPO / "presentation/assets/mother-newborn.png", 9.15, 1.35, 3.6, 5.85, border=False)
text(s, 9.15, 6.75, 3.6, 0.3, "Illustration", size=10, color=MUTED, italic=True, align=PP_ALIGN.RIGHT)

# 3 ─ Evidence gap
s = new("Most medicines lack data for pregnancy and for children", notes=(
    "CDC puts the pregnancy problem in one number: fewer than ten percent of medicines approved since 1980 have "
    "enough information to determine their safety during pregnancy, yet nine in ten women take a medication "
    "while pregnant. Children had the same problem: a 1997 Senate report found fewer than twenty percent of "
    "prescription drugs were labeled for use in children. That finding helped drive BPCA and PREA. Pregnant "
    "people and children are usually left out of the studies that establish a new drug's safety, so an honest "
    "answer has to include what isn't known."))
stats3 = [
    ("<10%", "of medicines approved since 1980 have enough information to determine their safety during pregnancy", DEEP),
    ("9 in 10", "women in the United States take a medication during pregnancy", MIST),
    ("<20%", "of prescription drugs were labeled for use in children in 1997, before BPCA and PREA", DEEP),
]
for i, (num, label, fill) in enumerate(stats3):
    x = 0.65 + i * 4.1
    box(s, x, 1.7, 3.8, 3.7, fill=fill)
    dark = fill == DEEP
    text(s, x + 0.35, 1.95, 3.2, 1.3, num, size=60, font=HEAD, bold=True, color=WHITE if dark else TEAL)
    text(s, x + 0.35, 3.3, 3.15, 2.0, label, size=17, color=MIST2 if dark else INK)
text(s, 0.65, 5.75, 12.0, 0.8, [
    [("Why: ", {"bold": True, "color": DEEP}),
     ("pregnant people and children are usually left out of the studies that establish a new medicine's "
      "safety, so most answers have to include what isn't known.", {})]], size=16, color=INK)
text(s, 0.65, 6.75, 12.0, 0.5,
     "Sources: CDC, Medicine and Pregnancy and Treating for Two; National Academies, Safe and Effective Medicines "
     "for Children (2012), citing a 1997 Senate report.", size=11, color=MUTED, italic=True)

# 4 ─ Federal efforts timeline
s = new("Two decades of federal work to close the gap", notes=(
    "This gap is well known, and federal programs have worked on it for over twenty years. The Best "
    "Pharmaceuticals for Children Act in 2002 and the Pediatric Research Equity Act in 2003 drove pediatric "
    "studies; NICHD leads the NIH side of BPCA, and created my branch, OPPTB, in 2004. NLM launched LactMed "
    "in 2006. NICHD's Pediatric Trials Network began in 2010. FDA's Pregnancy and Lactation Labeling Rule "
    "replaced the old letter categories in 2015. Congress created the PRGLAC task force in 2016, and its 2018 "
    "report made 15 recommendations. In 2020 NICHD announced funding for the MPRINT Hub. Each effort produced "
    "evidence, but in a different place and format, which is the next problem."))
events = [
    ("2002", "BPCA", "Pediatric studies of on- and off-patent drugs; NICHD leads NIH's role"),
    ("2003", "PREA", "Requires pediatric studies for many new drug approvals"),
    ("2004", "NICHD OPPTB", "Obstetric and Pediatric Pharmacology and Therapeutics Branch created"),
    ("2006", "LactMed", "NLM database on medicines and breastfeeding"),
    ("2010", "Pediatric Trials Network", "NICHD trials network under BPCA"),
    ("2015", "PLLR", "FDA labels replace A/B/C/D/X letters with pregnancy and lactation summaries"),
    ("2016–18", "PRGLAC", "Task force from the 21st Century Cures Act; 15 recommendations in 2018"),
    ("2020", "MPRINT Hub", "NICHD announces funding for maternal and pediatric therapeutics research"),
]
line_y = 4.05
connector(s, 0.75, line_y, 12.6, line_y, color=TEAL, width=3)
step = (12.6 - 0.75) / len(events)
for i, (year, name, what) in enumerate(events):
    cx = 0.75 + step * (i + 0.5)
    circle_num(s, cx - 0.14, line_y - 0.14, "", d=0.28, fill=CORAL if name in ("NICHD OPPTB", "PRGLAC", "MPRINT Hub") else TEAL)
    up = i % 2 == 0
    yy = 1.55 if up else 4.45
    connector(s, cx, line_y - 0.14 if up else line_y + 0.14, cx, (yy + 2.25) if up else yy, color=MIST2, width=1.5)
    text(s, cx - 0.72, yy, 1.44, 0.4, year, size=16, font=HEAD, bold=True, color=CORAL if not up else TEAL, align=PP_ALIGN.CENTER)
    text(s, cx - 0.72, yy + 0.38, 1.44, 0.6, name, size=14, bold=True, color=DEEP, align=PP_ALIGN.CENTER)
    text(s, cx - 0.74, yy + 0.98, 1.48, 1.3, what, size=12, color=INK, align=PP_ALIGN.CENTER)
text(s, 0.65, 6.85, 12.0, 0.4,
     "Each effort produced evidence, in a different place and format.", size=15, bold=True, color=DEEP)

# 5 ─ Scattered across agencies
s = new("What we do know is scattered across agencies", notes=(
    "Here is where that evidence lives today. NLM hosts LactMed, DailyMed labels, PubMed, ClinicalTrials.gov, "
    "RxNorm and MedlinePlus. FDA has adverse-event reports, pediatric labeling changes and pregnancy registry "
    "listings. NIH and NICHD have funded projects in RePORTER, BPCA and Pediatric Trials Network summaries, "
    "MPRINT data and DASH. MotherToBaby, a nonprofit, publishes fact sheets. Each uses different names, IDs "
    "and formats: APIs, web pages, spreadsheets and PDFs."))
agencies = [
    ("NLM", MIST, TEAL, ["LactMed", "DailyMed labels", "PubMed", "ClinicalTrials.gov", "RxNorm", "MedlinePlus"]),
    ("FDA", MIST, TEAL, ["Adverse-event reports (FAERS)", "Pediatric labeling changes", "Pregnancy registries",
                         "Recalls, alerts, shortages"]),
    ("NIH and NICHD", MIST, TEAL, ["RePORTER funded projects", "BPCA and PTN summaries", "MPRINT data", "DASH studies"]),
    ("Nonprofit", CORAL_T, CORAL, ["MotherToBaby fact sheets (OTIS), English and Spanish"]),
]
for i, (head, fill, hc, items) in enumerate(agencies):
    x = 0.65 + i * 3.1
    box(s, x, 1.6, 2.85, 4.4, fill=fill)
    text(s, x + 0.25, 1.8, 2.4, 0.5, head, size=20, font=HEAD, bold=True, color=hc)
    text(s, x + 0.25, 2.45, 2.4, 3.4, items, size=15, color=INK, space_after=8)
text(s, 0.65, 6.25, 12.0, 0.8, [
    [("Different names, IDs and formats: ", {"bold": True, "color": DEEP}),
     ("public APIs, web pages, spreadsheets and PDFs. No single place connects them.", {})]], size=16, color=INK)

# 3 ─ One question, many sources
s = new("Answering one question means visiting many sources", notes=(
    "Take the Zoloft question. First you have to know Zoloft is sertraline. The label's pregnancy section is "
    "in DailyMed, studies are in PubMed, trials in ClinicalTrials.gov, pregnancy registries at FDA, published "
    "pharmacokinetic data in MPRINT, and LactMed once the baby is born. Each uses different names, IDs and "
    "formats, and some are web pages or spreadsheets rather than APIs."))
cx, cy, cw, ch = 4.4, 3.35, 4.55, 1.45
srcs = [
    (0.65, 1.65, "RxNorm", "Zoloft is sertraline"),
    (4.85, 1.65, "DailyMed", "Pregnancy section of the label"),
    (9.05, 1.65, "PubMed", "Published studies"),
    (0.65, 3.45, "ClinicalTrials.gov", "Studies now recruiting"),
    (9.05, 3.45, "FDA registries", "Pregnancy exposure registries"),
    (0.65, 5.25, "MPRINT", "Published PK data tables"),
    (4.85, 5.25, "LactMed", "If she breastfeeds later"),
    (9.05, 5.25, "openFDA", "Reported adverse events"),
]
for x, y, name, what in srcs:
    connector(s, x + 1.8, y + 0.55, cx + cw / 2, cy + ch / 2)
for x, y, name, what in srcs:
    box(s, x, y, 3.6, 1.1, fill=MIST)
    text(s, x + 0.25, y + 0.15, 3.2, 0.4, name, size=16, bold=True, color=TEAL)
    text(s, x + 0.25, y + 0.55, 3.2, 0.4, what, size=14, color=INK)
q = box(s, cx, cy, cw, ch, fill=DEEP)
text(s, cx + 0.3, cy + 0.15, cw - 0.6, ch - 0.3,
     "“I take Zoloft and just found out I'm pregnant.”", size=18, font=HEAD, color=WHITE,
     italic=True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)

# 8 ─ Three things she has to get right
s = new("Three things she has to get right", notes=(
    "Even with the right sources, three things go wrong easily. The medicine: Zoloft is sertraline, a "
    "combination product has several ingredients, and 'my little white pill' can't be identified at all. "
    "The population: breastfeeding evidence isn't pregnancy evidence, and animal data isn't human data. "
    "And reading the source: an empty search is not good news, and adverse-event report counts are not rates. "
    "The server handles each one in code rather than leaving it to the AI's judgment."))
things = [
    ("1", "The right medicine", "Zoloft is sertraline. A combination pill has several ingredients. “My little "
     "white pill” can't be identified.", "Confirms the name with RxNorm; stops if unclear"),
    ("2", "The right population", "Breastfeeding evidence isn't pregnancy evidence. A study in adults or older "
     "children doesn't tell you about a newborn.", "Tags every finding with its population and age band"),
    ("3", "The right reading", "An empty search isn't good news. Adverse-event report counts aren't rates.",
     "Says “no evidence retrieved; not evidence of safety”"),
]
for i, (n, head, body, fix) in enumerate(things):
    x = 0.65 + i * 4.1
    box(s, x, 1.65, 3.8, 3.85, fill=MIST)
    circle_num(s, x + 0.35, 1.95, n, d=0.6, fill=CORAL, size=20)
    text(s, x + 0.35, 2.75, 3.15, 0.5, head, size=20, font=HEAD, bold=True, color=DEEP)
    text(s, x + 0.35, 3.35, 3.15, 2.0, body, size=16, color=INK)
    box(s, x, 5.65, 3.8, 0.95, fill=DEEP)
    text(s, x + 0.3, 5.65, 3.25, 0.95, fix, size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 6.85, 12.0, 0.4, "Dark boxes: what the server does about each, in code.", size=12, color=MUTED, italic=True)

# 5 ─ What I built
s = new("What I built", notes=(
    "The server has 31 tools, 4 reusable prompts and 4 resources. The tools are grouped around the jobs "
    "people actually do: confirm the medicine, look at breastfeeding or pregnancy evidence, search the "
    "literature and trials, look at NICHD research, and check safety notices. The most important tool is "
    "medication_evidence_brief, which does the whole workflow in one call."))
stats = [("31", "tools"), ("4", "prompts"), ("4", "resources"), ("15", "public sources")]
for i, (num, lab) in enumerate(stats):
    x = 0.65 + i * 1.75
    text(s, x, 1.55, 1.6, 0.8, num, size=40, font=HEAD, bold=True, color=TEAL)
    text(s, x, 2.35, 1.6, 0.4, lab, size=14, color=MUTED)
box(s, 7.95, 1.55, 4.75, 1.3, fill=DEEP)
text(s, 8.25, 1.7, 4.2, 1.0, [
    [("medication_evidence_brief", {"bold": True, "color": WHITE, "font": "Courier New", "size": 15})],
    "One call: confirm the medicine, gather every source, sort the evidence and list the gaps.",
], size=14, color=MIST2, space_after=4)
groups = [
    ("Identify the medicine", "RxNorm names, ingredients and products; parent-friendly MedlinePlus pages"),
    ("Breastfeeding", "LactMed search and full records, with exposure and infant outcomes kept apart"),
    ("Pregnancy and labels", "DailyMed pregnancy and lactation sections, pediatric labeling changes, MotherToBaby fact sheets"),
    ("Research", "PubMed with pregnancy and lactation filters, abstracts, ClinicalTrials.gov, MPRINT data"),
    ("NICHD programs", "RePORTER funding portfolios, BPCA study summaries, DASH study discovery"),
    ("Safety and participation", "Recalls, safety alerts, shortages, FAERS signals, registries, recruiting studies"),
]
for i, (head, body) in enumerate(groups):
    x = 0.65 + (i % 3) * 4.1
    y = 3.25 + (i // 3) * 1.85
    box(s, x, y, 3.8, 1.6, fill=MIST)
    text(s, x + 0.3, y + 0.2, 3.3, 0.4, head, size=17, bold=True, color=TEAL)
    text(s, x + 0.3, y + 0.65, 3.3, 0.9, body, size=14, color=INK)

# 5b ─ Where it fits
s = new("Where it fits next to LactMed and MotherToBaby", notes=(
    "A judge who knows this field will ask: why not just use LactMed, or call MotherToBaby? Neither is a "
    "competitor. LactMed is a source this server reads. LactRx is MotherToBaby's app with the same LactMed "
    "content. MotherToBaby is a nonprofit service whose specialists weigh the evidence for one person, which "
    "this server deliberately does not do. What the server adds is breadth across pregnancy, breastfeeding and "
    "children's medicines, machine-readable answers with sources, visible gaps, and availability at any hour. "
    "After hours, MotherToBaby replies the next business day; this server can help someone prepare for that "
    "conversation."))
cols = [
    ("LactMed and LactRx", MIST, TEAL, [
        ("Covers", "Breastfeeding only"),
        ("Who runs it", "NLM database; LactRx is MotherToBaby's app with the same content"),
        ("How you use it", "Search the website or app yourself"),
    ]),
    ("MotherToBaby", CORAL_T, CORAL, [
        ("Covers", "Pregnancy and breastfeeding exposures"),
        ("Who runs it", "OTIS, a nonprofit of teratology specialists"),
        ("How you use it", "Talk to a specialist, weekdays 8 am to 7 pm ET; next business day after hours"),
    ]),
    ("This MCP server", DEEP, WHITE, [
        ("Covers", "Pregnancy, breastfeeding and children's medicines"),
        ("Who runs it", "Reads 15 public sources, including LactMed, labels, studies, trials and NICHD data"),
        ("How you use it", "Any AI assistant, any hour; cited, structured answers with gaps shown"),
    ]),
]
for i, (head, fill, hc, rows) in enumerate(cols):
    x = 0.65 + i * 4.1
    box(s, x, 1.6, 3.8, 4.25, fill=fill)
    text(s, x + 0.3, 1.8, 3.2, 0.45, head, size=19, font=HEAD, bold=True, color=hc)
    body = []
    for label, val in rows:
        body.append([(label, {"bold": True, "size": 12, "color": MIST2 if fill == DEEP else MUTED})])
        body.append(val)
    text(s, x + 0.3, 2.4, 3.2, 3.4, body, size=15, color=WHITE if fill == DEEP else INK, space_after=3)
text(s, 0.65, 6.1, 12.0, 0.9, [
    [("What it does not do: ", {"bold": True, "color": CORAL}),
     ("weigh the evidence for one person. For an individual pregnancy or breastfeeding question, it refers "
      "people to MotherToBaby (866-626-6847) and shares their English and Spanish fact sheets.", {})]], size=15, color=INK)

# 5c ─ Beyond parents
s = new("Beyond parents: clinicians, researchers and program staff", notes=(
    "The same server answers professional questions. Clinicians want the primary evidence with its population "
    "and dates. Researchers and NICHD program staff want studies, trials, data and funding, with exact query "
    "criteria they can reproduce."))
cols = [
    ("Clinicians", [
        "What does LactMed report about sertraline in breast milk and observed infant effects?",
        "What published studies examine metformin during pregnancy?",
        "What does the lamotrigine label say in its pregnancy section?"]),
    ("Researchers and NIH program staff", [
        "What did NICHD fund in neonatal pharmacology in FY 2024 and FY 2025?",
        "Find BPCA and PTN study summaries and FDA pediatric labeling changes for levetiracetam.",
        "Which MPRINT studies report pharmacokinetics for sertraline?"]),
]
for ci, (head, qs) in enumerate(cols):
    x = 0.65 + ci * 6.15
    text(s, x, 1.6, 5.8, 0.4, head, size=18, bold=True, color=TEAL)
    for qi, q in enumerate(qs):
        y = 2.2 + qi * 1.55
        box(s, x, y, 5.85, 1.35, fill=MIST if ci == 0 else CORAL_T)
        text(s, x + 0.3, y + 0.2, 5.25, 1.0, f"“{q}”", size=16, color=INK, italic=True,
             anchor=MSO_ANCHOR.MIDDLE)


# 5d ─ Beyond pregnancy
s = new("Beyond pregnancy: children, studies and Spanish", notes=(
    "The opening follows a pregnant mother, but much of the server is about children and research. For "
    "children's medicines it covers FDA pediatric labeling changes, BPCA and Pediatric Trials Network study "
    "summaries, MPRINT pediatric data and recruiting trials, keeping neonates, infants, children and adolescents "
    "separate. For studies, it searches PubMed with pregnancy and lactation filters, returns abstracts, trials, "
    "MPRINT tables and NIH funding, and the AI explains dense studies and labels in plain language with every "
    "claim linked. For Spanish speakers, it returns MotherToBaby fact sheets in Spanish and MedlinePlus Spanish "
    "drug pages. Spanish safety messages are held until a Spanish speaker reviews them."))
caps = [
    ("Children's medicines", [
        "FDA pediatric labeling changes",
        "BPCA and Pediatric Trials Network study summaries",
        "MPRINT pediatric studies and data tables",
        "Recruiting trials with confirmed pediatric ages",
        "Neonate, infant, child and adolescent kept separate",
    ]),
    ("Studies, in plain language", [
        "PubMed with pregnancy and lactation filters",
        "Abstracts, trials and MPRINT data in one place",
        "NIH funding portfolios with exact query criteria",
        "Dense studies and labels explained plainly by the AI, every claim linked",
    ]),
    ("Spanish", [
        "323 MotherToBaby fact sheets in Spanish, verbatim",
        "MedlinePlus Spanish drug pages by drug code",
        "Spanish safety messages held until a Spanish speaker reviews them",
    ]),
]
for i, (head, items) in enumerate(caps):
    x = 0.65 + i * 4.1
    box(s, x, 1.6, 3.8, 5.1, fill=MIST if i != 2 else CORAL_T)
    text(s, x + 0.3, 1.8, 3.2, 0.5, head, size=19, font=HEAD, bold=True, color=TEAL if i != 2 else CORAL)
    text(s, x + 0.3, 2.45, 3.25, 4.1, items, size=15, color=INK, space_after=10)

# 6 ─ The brief workflow
s = new("One call turns a question into an evidence brief", notes=(
    "Here is what medication_evidence_brief does. It confirms the medicine through RxNorm first, and stops "
    "if the name is ambiguous. For combination products, every ingredient gets its own search. The results "
    "are sorted into three evidence axes, so effects on the mother, exposure of the baby, and outcomes in "
    "the baby are never blended together. Empty rows stay visible. It ends with questions to take to a "
    "clinician."))
steps = [("1", "Confirm the medicine", "RxNorm match; stop if unclear"),
         ("2", "Search each source", "Every ingredient separately"),
         ("3", "Sort the evidence", "Three axes, never merged"),
         ("4", "Show the gaps", "Empty rows stay visible"),
         ("5", "Prepare questions", "For the clinician visit")]
for i, (n, head, body) in enumerate(steps):
    x = 0.65 + i * 2.5
    if i < 4:
        connector(s, x + 0.75, 2.05, x + 2.5 + 0.25, 2.05, color=MIST2, width=2.5)
    circle_num(s, x + 0.25, 1.75, n, d=0.6)
    text(s, x, 2.55, 2.3, 0.4, head, size=16, bold=True, color=DEEP)
    text(s, x, 2.95, 2.3, 0.7, body, size=14, color=MUTED)
text(s, 0.65, 4.0, 12.0, 0.4, "The three evidence axes", size=18, bold=True, color=TEAL)
axes = [("The person taking it", "Effects on the pregnant or breastfeeding parent, and their pharmacokinetics when found"),
        ("Transfer or exposure", "Measured levels in the fetus, breast milk or infant, kept apart from animal or modeled data"),
        ("Fetal or infant outcomes", "What was observed in the baby, kept apart from exposure measurements")]
for i, (head, body) in enumerate(axes):
    x = 0.65 + i * 4.1
    box(s, x, 4.55, 3.8, 1.85, fill=MIST if i != 2 else CORAL_T)
    text(s, x + 0.3, 4.75, 3.2, 0.4, head, size=17, bold=True, color=DEEP)
    text(s, x + 0.3, 5.2, 3.2, 1.1, body, size=14, color=INK)


def demo(title, img, question, caption, notes, max_h=3.95):
    s = new(title, notes=notes)
    box(s, 0.65, 1.55, 12.0, 0.75, fill=DEEP)
    text(s, 0.95, 1.6, 11.4, 0.65, f"“{question}”", size=16, color=WHITE, italic=True,
         anchor=MSO_ANCHOR.MIDDLE)
    iw, ih = Image.open(img).size
    w = min(10.6, iw / ih * max_h)
    picture(s, img, (W - w) / 2, 2.65, 10.6, max_h)
    text(s, 0.65, 6.95, 9.5, 0.35, caption, size=11, color=MUTED, italic=True)
    return s


# 7 ─ Demo: exposure vs outcomes
demo("Demo: exposure and infant outcomes stay separate", DEMO / "cross-source.png",
     "Compare LactMed sertraline evidence with a PubMed study. Separate measured exposure from infant outcomes.",
     "Recorded answer from an earlier version of the same workflow. Source links (S1, S10) point to the retrieved records.",
     "The model answered from LactMed and the study abstract. You can see measured serum levels under exposure, "
     "the single case report under outcomes, and the selected product label with its date. The note at the "
     "bottom says the exact product match was not confirmed, which is the kind of honesty I want in answers.")

# 8 ─ Demo: gaps
s = new("Demo: gaps are shown, not hidden", notes=(
    "Daridorexant is a newer sleep medicine with very little pregnancy data. The brief shows how much each "
    "source has, the label's limited human data, empty evidence rows, and the pregnancy registry, which is "
    "listed but never recommended. On the right, a search that finds nothing says so explicitly, so an AI "
    "client can't turn silence into reassurance."))
box(s, 0.65, 1.55, 12.0, 0.75, fill=DEEP)
text(s, 0.95, 1.6, 11.4, 0.65, "“Give me an evidence brief on daridorexant in pregnancy.”", size=16,
     color=WHITE, italic=True, anchor=MSO_ANCHOR.MIDDLE)
picture(s, DEMO / "gap.png", 0.75, 2.7, 6.9, 3.95)
picture(s, DEMO / "empty.png", 7.95, 2.7, 4.7, 2.6)
text(s, 7.95, 4.6, 4.7, 1.5, [
    [("When nothing is found", {"bold": True, "color": TEAL})],
    "The payload says so in plain fields. Missing data never reads as safe.",
], size=14, color=INK)
text(s, 0.65, 6.95, 9.5, 0.35, "Recorded output from an earlier version of the same tools.", size=11,
     color=MUTED, italic=True)

# 8b ─ Should AI answer this?
s = new(None, notes=(
    "This is the question I asked myself first. Medicines in pregnancy, breastfeeding and childhood are "
    "high-stakes, and a wrong answer can do real harm. My answer is yes, with firm limits. The evidence is "
    "already public; what's missing is context, so people see a finding with its population, its date and "
    "its gaps. Showing what isn't known matters as much as showing what is. It also makes two decades of "
    "federal work, BPCA, PRGLAC, MPRINT and LactMed, visible and usable. And it is built to prepare someone for "
    "a conversation with a clinician, never to replace it. On the right are the lines it won't cross. Every "
    "one is enforced in code and covered by tests."))
reasons = [
    ("The evidence is already public", "The question isn't whether people find it; it's whether they see it with its population, date and limits."),
    ("The gaps matter as much as the findings", "Saying “no evidence retrieved; not evidence of safety” is part of the answer."),
    ("Federal work becomes visible", "BPCA, PRGLAC, MPRINT and LactMed produced evidence most families never see."),
    ("It prepares, it doesn't decide", "Every brief ends with questions to bring to a clinician."),
]
text(s, 0.65, 0.45, 12.0, 0.45, "Maternal and pediatric pharmacology is a highly sensitive topic.", size=18, color=MUTED)
text(s, 0.65, 0.85, 12.0, 0.8, "Should an AI assistant handle questions about it?", size=32, font=HEAD, bold=True, color=DEEP)
text(s, 0.65, 1.85, 6.6, 0.45, "Why I think yes", size=20, font=HEAD, bold=True, color=TEAL)
for i, (head, body) in enumerate(reasons):
    y = 2.45 + i * 1.1
    circle_num(s, 0.65, y + 0.05, str(i + 1), d=0.48, size=15)
    text(s, 1.35, y, 5.9, 0.4, head, size=17, bold=True, color=DEEP)
    text(s, 1.35, y + 0.42, 5.9, 0.75, body, size=14, color=INK)
box(s, 7.65, 1.85, 5.0, 4.85, fill=DEEP)
text(s, 7.95, 2.05, 4.5, 0.45, "Lines it won't cross", size=20, font=HEAD, bold=True, color=WHITE)
text(s, 7.95, 2.6, 4.45, 2.6, [
    "No individualized treatment advice",
    "No doses, schedules or start/stop decisions",
    "No diagnosis or triage",
    "Missing evidence is never presented as safe",
    "Never guesses a medicine from a description",
    "No names, birth dates or record numbers",
], size=14, color=MIST2, space_after=6)
text(s, 7.95, 4.95, 4.45, 1.7, [
    [("Instead, as appropriate, it directs people to ", {"bold": True, "color": WHITE}),
     ("a clinician or pharmacist, MotherToBaby (866-626-6847), 988, the Maternal Mental Health Hotline "
      "(1-833-TLC-MAMA), Poison Help (1-800-222-1222) or 911.", {})]], size=13, color=CORAL_T)
text(s, 0.65, 6.95, 7.0, 0.35, "Each line is enforced in code and covered by tests.", size=12, color=MUTED, italic=True)

# 9 ─ Safety routing
s = new("Some questions shouldn't get a research answer", notes=(
    "Before any search or AI answer, the question goes through route_parent_question. These are the actual "
    "current replies. Emergencies get 911 and Poison Help. A crisis gets 988; if the person is pregnant or "
    "postpartum, it also gets HRSA's National Maternal Mental Health Hotline, 1-833-TLC-MAMA, which answers "
    "calls and texts around the clock in English and Spanish. A vague pill description is stopped, because guessing the drug is dangerous. Dosing "
    "and personal medication decisions go to a clinician or pharmacist; if the person is pregnant or "
    "breastfeeding, the reply also gives MotherToBaby's free specialist line. In testing, all seven stop cases made zero downstream calls."))
rows = [
    ("Emergency", "“My baby is having a seizure.”", "Call 911 now; Poison Help 1-800-222-1222"),
    ("Crisis", "“I feel hopeless since giving birth…”", "Call or text 988 or 1-833-TLC-MAMA"),
    ("Unclear medicine", "“My little white pill…”", "Check the package with a pharmacist first"),
    ("Personal decision", "“Can I take ibuprofen while breastfeeding?”", "Clinician or pharmacist, plus MotherToBaby"),
    ("Private details", "Names, birth dates, record numbers", "Remove them; nothing is looked up"),
    ("Not English", "Questions the rules can't check", "Stop; Spanish MedlinePlus pages by drug code"),
]
text(s, 0.65, 1.55, 2.6, 0.4, "Route", size=14, bold=True, color=MUTED)
text(s, 3.35, 1.55, 4.6, 0.4, "Example", size=14, bold=True, color=MUTED)
text(s, 8.15, 1.55, 4.5, 0.4, "What the person sees", size=14, bold=True, color=MUTED)
for i, (r, ex, out) in enumerate(rows):
    y = 2.0 + i * 0.78
    box(s, 0.65, y, 12.0, 0.66, fill=CORAL_T if i < 2 else MIST, radius=0.15)
    text(s, 0.9, y, 2.4, 0.66, r, size=16, bold=True, color=CORAL if i < 2 else TEAL, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 3.35, y, 4.6, 0.66, ex, size=14, color=INK, italic=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.15, y, 4.4, 0.66, out, size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 6.8, 12.0, 0.4,
     "Checked before any search or model answer. In testing, 7 of 7 stop cases made zero downstream calls.",
     size=14, color=DEEP, bold=True)

# 10 ─ Getting the safety check right
s = new("A safety rule has to work in both directions", notes=(
    "During final review I found the safety check was too eager. Any mention of seizures or postpartum "
    "depression triggered the emergency or crisis message, even in a research question. That would have "
    "blocked core NICHD topics like epilepsy drugs in pregnancy. The fix separates describing an event from "
    "naming a condition, and 29 new tests pin both directions. The same review found that \u201csince giving "
    "birth\u201d was not recognized as postpartum; it now adds the maternal mental health hotline."))
pairs = [
    ("“What does research say about lamotrigine for seizures in pregnancy?”",
     "Before: emergency message", "Now: research answer", False),
    ("“What is known about postpartum depression treatment with zuranolone?”",
     "Before: crisis message", "Now: research answer", False),
    ("“My baby is having a seizure.”", "Before: call 911", "Now: call 911", True),
    ("“I feel hopeless since giving birth.”", "Before: 988 only", "Now: adds TLC-MAMA", True),
]
for i, (qtext, before, after, same) in enumerate(pairs):
    y = 1.65 + i * 1.2
    box(s, 0.65, y, 7.3, 1.0, fill=MIST)
    text(s, 0.95, y, 6.8, 1.0, qtext, size=15, italic=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.2, y, 2.2, 1.0, before, size=14, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)
    pill = box(s, 10.45, y + 0.2, 2.2, 0.6, fill=TEAL if not same else DEEP, radius=0.5)
    text(s, 10.45, y + 0.2, 2.2, 0.6, after, size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE,
         align=PP_ALIGN.CENTER)
text(s, 0.65, 6.6, 12.0, 0.6, [
    [("The fix: ", {"bold": True, "color": DEEP}),
     ("naming a condition is a research topic; describing it happening, or yourself, still stops the request. "
      "29 new tests cover both directions.", {})]], size=15, color=INK)

# 10b ─ Six ways an accurate answer can still mislead
s = new("Six ways an accurate answer can still mislead", notes=(
    "I wrote down the six ways an accurate-looking answer could still mislead, and what the server does about "
    "each. Two of them, false reassurance and prompting someone to stop a medicine, need a clinician's eye."))
mis = [
    ("Partial looks complete", "Missing sections, truncation and label choice are reported."),
    ("No reports reads as safe", "Study types and unknown counts travel with no-effects text."),
    ("Populations get merged", "Every item keeps its source population and age bands."),
    ("Counts read as rates", "FAERS counts carry no-denominator and no-causation caveats."),
    ("Old looks current", "Label versions, dates and snapshot revisions are returned."),
    ("Facts prompt stopping", "Source context and a medication-change caution stay attached."),
]
for i, (head, body) in enumerate(mis):
    x = 0.65 + (i % 3) * 4.1
    y = 1.65 + (i // 3) * 2.45
    needs = i in (1, 5)
    box(s, x, y, 3.8, 2.2, fill=CORAL_T if needs else MIST)
    text(s, x + 0.3, y + 0.25, 3.2, 0.7, head, size=17, bold=True, color=CORAL if needs else TEAL)
    text(s, x + 0.3, y + 0.95, 3.2, 1.1, body, size=15, color=INK)
text(s, 0.65, 6.7, 12.0, 0.4, "Coral cards still need clinician review of real answers.", size=13,
     color=MUTED, italic=True)


# 11 ─ Architecture
s = new("How it fits together", notes=(
    "Any MCP client can connect: Claude Desktop, VS Code, MCP Inspector, or my PowerShell chat client. The "
    "safety check runs first. The FastMCP server validates every input with Pydantic models, and every tool "
    "goes through one shared wrapper for safety checks, errors and provenance. Source adapters call only an "
    "allowlist of federal HTTPS hosts. MPRINT data ship as a read-only local snapshot. On Databricks I used "
    "model serving for the chat model and judge, MLflow for evaluation tracking, and Apps for hosting."))
layers = [
    ("AI client", "Claude Desktop, VS Code, MCP Inspector or the companion chat client", MIST),
    ("Safety check first", "route_parent_question screens the actual question", CORAL_T),
    ("FastMCP server", "Pydantic input models  ·  one audited wrapper for every tool  ·  common response envelope", MIST),
    ("Source adapters", "HTTPS to an allowlist of federal hosts  ·  retries, caching, size limits", MIST),
]
for i, (head, body, fill) in enumerate(layers):
    y = 1.6 + i * 1.2
    box(s, 0.65, y, 7.6, 0.95, fill=fill)
    text(s, 0.95, y, 2.6, 0.95, head, size=16, bold=True, color=CORAL if fill == CORAL_T else TEAL,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 3.55, y, 4.5, 0.95, body, size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    if i < 3:
        connector(s, 4.45, y + 0.95, 4.45, y + 1.2, color=TEAL, width=2)
box(s, 0.65, 6.4, 3.7, 0.7, fill=DEEP)
text(s, 0.85, 6.4, 3.4, 0.7, "Live public APIs and pages", size=14, bold=True, color=WHITE,
     anchor=MSO_ANCHOR.MIDDLE)
box(s, 4.55, 6.4, 3.7, 0.7, fill=DEEP)
text(s, 4.75, 6.4, 3.4, 0.7, "MPRINT and LactMed, dated copies", size=14, bold=True, color=WHITE,
     anchor=MSO_ANCHOR.MIDDLE)
connector(s, 2.5, 6.15, 2.5, 6.4, color=TEAL, width=2)
connector(s, 6.4, 6.15, 6.4, 6.4, color=TEAL, width=2)
box(s, 8.75, 1.6, 3.9, 5.5, fill=MIST)
text(s, 9.05, 1.85, 3.4, 0.4, "On Databricks", size=18, bold=True, color=TEAL)
text(s, 9.05, 2.45, 3.35, 4.5, [
    [("Model serving", {"bold": True})], "Chat model and evaluation judge",
    [("MLflow", {"bold": True})], "Every evaluation run, trace and grade",
    [("Apps", {"bold": True})], "Hosted MCP endpoint with OAuth",
    [("Serverless notebook", {"bold": True})], "Full test suite run in the cloud",
], size=14, color=INK, space_after=3)

# 12 ─ Key decisions
s = new("Four design decisions", notes=(
    "First, I built tools around what people are trying to do, not around each API. The evidence brief and "
    "the coverage check each combine several sources. Second, the medicine must be confirmed before any "
    "evidence lookup. Third, missing data is a first-class result. Fourth, MPRINT tables ship as a local "
    "read-only snapshot, so answers are reproducible. Every MPRINT result says how old the copy is, the "
    "snapshot resource checks MPRINT's GitHub for newer data, and a weekly GitHub job fails if there is. "
    "LactMed's web pages started showing automated readers a browser check, so LactMed text now comes from "
    "NCBI's official download package. That also gave me LactMed's citations: every finding links to its "
    "PubMed study."))
decs = [
    ("Tools for goals, not endpoints", "medication_evidence_brief and check_evidence_coverage each combine "
     "several sources, so an agent makes one meaningful call instead of eight thin ones."),
    ("Confirm the medicine first", "RxNorm resolves brand names to ingredients. An uncertain match returns "
     "requires_confirmation; a description of a pill stops the request."),
    ("Missing stays missing", "Empty searches, absent label sections and truncated records are explicit "
     "fields. A failed source is reported as unavailable, not as zero."),
    ("Dated copies with study links", "MPRINT and LactMed ship as read-only copies of official releases. Every "
     "result shows its date; LactMed findings link to their PubMed studies."),
]
for i, (head, body) in enumerate(decs):
    x = 0.65 + (i % 2) * 6.15
    y = 1.65 + (i // 2) * 2.65
    box(s, x, y, 5.85, 2.4, fill=MIST)
    circle_num(s, x + 0.3, y + 0.3, str(i + 1), d=0.55)
    text(s, x + 1.05, y + 0.32, 4.5, 0.5, head, size=19, font=HEAD, bold=True, color=DEEP)
    text(s, x + 1.05, y + 0.95, 4.5, 1.35, body, size=15, color=INK)

# 13 ─ How I tested
s = new("How I tested it", notes=(
    "I tested in layers. All 861 automated tests pass in a Databricks serverless notebook; on my Mac, the "
    "PowerShell client checks are skipped because PowerShell isn't installed. "
    "MCP Inspector checked the protocol and schemas. Then 28 scripted chats: 21 research questions and 7 that "
    "should stop. Seven questions were run twice, once with the MCP and once with the same model and no tools. "
    "Finally, a 10-question exact-answer benchmark against the MPRINT snapshot, scored in Arize Phoenix. "
    "Model-graded results are tracked in MLflow."))
tests = [
    ("861", "automated tests", "All pass in a Databricks serverless notebook"),
    ("9", "Inspector checks", "Protocol, tool schemas and sample contracts"),
    ("28", "scripted chats", "21 research questions and 7 that should stop"),
    ("7", "paired questions", "Same model with the MCP versus with no tools"),
    ("10", "benchmark questions", "Exact answers against the MPRINT snapshot, scored in Phoenix"),
]
for i, (num, lab, body) in enumerate(tests):
    y = 1.6 + i * 1.02
    text(s, 0.65, y, 1.6, 0.9, num, size=34, font=HEAD, bold=True, color=TEAL, anchor=MSO_ANCHOR.MIDDLE,
         align=PP_ALIGN.RIGHT)
    text(s, 2.55, y + 0.08, 3.3, 0.4, lab, size=17, bold=True, color=DEEP)
    text(s, 2.55, y + 0.45, 6.0, 0.4, body, size=14, color=MUTED)
box(s, 8.9, 1.65, 3.75, 4.95, fill=MIST)
text(s, 9.2, 1.9, 3.2, 4.6, [
    [("How answers were graded", {"bold": True, "color": TEAL, "size": 17})],
    "A model judge scored two things separately: did the answer stick to the retrieved sources, and did it "
    "do everything the question asked.",
    "Code checked the rest: routes, tool choice, required notices and whether every link came from a tool.",
    "Every run, trace and grade is stored in MLflow. No scores were overridden.",
], size=14, color=INK, space_after=10)

# 14 ─ Results
s = new("Results", notes=(
    "The clearest result: with the MCP, the model fulfilled all seven paired tasks. Without tools, the same "
    "model fulfilled none, mostly because it couldn't verify current records. All 28 chats took the expected "
    "route with the expected tools, and all seven stop cases made zero downstream calls. The benchmark scored "
    "9 of 10; the one miss copied the wrong DOI. These are known development questions with a model judge, "
    "and there has been no clinician review yet."))
box(s, 0.65, 1.6, 5.9, 3.0, fill=DEEP)
text(s, 0.95, 1.8, 5.3, 0.4, "Paired tasks fulfilled", size=16, color=MIST2)
text(s, 0.95, 2.3, 2.6, 1.2, "7/7", size=60, font=HEAD, bold=True, color=WHITE)
text(s, 0.95, 3.5, 2.6, 0.4, "with the MCP", size=15, color=MIST2)
text(s, 3.6, 2.3, 2.6, 1.2, "0/7", size=60, font=HEAD, bold=True, color=CORAL_T)
text(s, 3.6, 3.5, 2.6, 0.4, "same model, no tools", size=15, color=MIST2)
res = [("28/28", "chats took the expected route and tools"),
       ("7/7", "stop cases made zero downstream calls"),
       ("21/21", "research tasks fulfilled"),
       ("9/10", "exact benchmark answers")]
for i, (num, lab) in enumerate(res):
    x = 6.85 + (i % 2) * 2.95
    y = 1.6 + (i // 2) * 1.55
    box(s, x, y, 2.75, 1.4, fill=MIST)
    text(s, x + 0.25, y + 0.12, 2.3, 0.65, num, size=30, font=HEAD, bold=True, color=TEAL)
    text(s, x + 0.25, y + 0.78, 2.35, 0.6, lab, size=13, color=INK)
text(s, 0.65, 4.95, 12.0, 1.6, [
    [("What the misses taught me. ", {"bold": True, "color": DEEP}),
     ("Source fidelity was 17 of 21: four answers drifted beyond what the sources said, so I tightened the "
      "answer instructions. The benchmark miss copied a DOI from the wrong candidate. Earlier versions "
      "scored 3/10 on the same benchmark; most of those failures were safety-check false positives.", {})],
], size=15, color=INK)
text(s, 0.65, 6.6, 12.0, 0.5,
     "Known development questions, one answer each, graded by a model judge. No clinician review yet.",
     size=13, color=MUTED, italic=True)

# 14b ─ Hands-on testing
s = new("Using it myself found three more problems", notes=(
    "Scripted tests measure known questions. So I also connected the server to Claude Desktop and used it the "
    "way a parent or researcher would. A sertraline answer said it was cut off, because the record extract was "
    "capped at 6,000 characters. Findings like a French pharmacovigilance study had no link, because the "
    "reference list was being discarded. And the MotherToBaby fact sheet couldn't be read: the tool only "
    "returned links, and NCBI's pages now show automated readers a browser check, which the server never "
    "bypasses. I fixed all three that night by reading NCBI's official LactMed and MotherToBaby packages, and "
    "each fix has tests."))
found = [
    ("A LactMed answer said it was cut off", "Extracts now default to 16,000 characters; anything cut is still flagged"),
    ("No link to the studies behind findings", "Each finding keeps LactMed's citation, such as [54], with its PubMed link"),
    ("A MotherToBaby fact sheet couldn't be read", "Answers come verbatim from NCBI's official package, attributed to OTIS"),
]
text(s, 0.65, 1.55, 5.6, 0.4, "What I saw in the chat", size=14, bold=True, color=MUTED)
text(s, 6.85, 1.55, 5.8, 0.4, "What changed", size=14, bold=True, color=MUTED)
for i, (saw, fix) in enumerate(found):
    y = 2.05 + i * 1.3
    box(s, 0.65, y, 5.85, 1.1, fill=CORAL_T)
    text(s, 0.95, y, 5.3, 1.1, saw, size=16, bold=True, color=DEEP, anchor=MSO_ANCHOR.MIDDLE)
    box(s, 6.85, y, 5.8, 1.1, fill=MIST)
    text(s, 7.15, y, 5.3, 1.1, fix, size=15, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    connector(s, 6.5, y + 0.55, 6.85, y + 0.55, color=TEAL, width=2.5)
text(s, 0.65, 6.05, 12.0, 0.8, [
    [("Example: ", {"bold": True, "color": DEEP}),
     ("[54] Trenque et al., Drug Saf 2011, the French pharmacovigilance study, now links to "
      "pubmed.ncbi.nlm.nih.gov/22077504.", {})]], size=15, color=INK)
text(s, 0.65, 6.85, 11.0, 0.35, "Hand-run Claude Desktop chats by the developer; qualitative, not scored. Details: documentation/HANDS_ON_TESTING.md.",
     size=11, color=MUTED, italic=True)

# 15 ─ Security
s = new("Security", notes=(
    "The data are public, but I still treated the server as something that could be misused. Outbound "
    "requests can only reach an allowlist of federal hosts over HTTPS, with no redirects and a 5 MB cap, "
    "and DNS answers must be public addresses. Remote hosting refuses to start without token verification, "
    "and each tool needs its own scope. Database queries are parameterized, questions are never written to "
    "logs, and identifying details are blocked before any lookup."))
sec = [
    ("Outbound traffic", "Allowlisted federal HTTPS hosts, plus read-only GitHub for the data check. No redirects, 5 MB cap."),
    ("Remote access", "Signed RS256 tokens with a separate scope for each tool. Won't start without them."),
    ("Inputs", "Pydantic models reject bad values. SQL is parameterized. No user-supplied URLs."),
    ("Privacy", "Names, birth dates and record numbers are blocked. Questions are never logged."),
    ("Data", "Public, read-only sources. No patient data, no write actions, no form submissions."),
    ("Known gaps", "No penetration test. Prompt-injection resistance in retrieved text is not established."),
]
for i, (head, body) in enumerate(sec):
    x = 0.65 + (i % 3) * 4.1
    y = 1.65 + (i // 3) * 2.6
    gap = i == 5
    box(s, x, y, 3.8, 2.35, fill=CORAL_T if gap else MIST)
    text(s, x + 0.3, y + 0.25, 3.2, 0.4, head, size=18, bold=True, color=CORAL if gap else TEAL)
    text(s, x + 0.3, y + 0.8, 3.2, 1.45, body, size=15, color=INK)

# 16 ─ Lessons and next steps
s = new("What I learned and what comes next", notes=(
    "Three lessons. Interpretation was harder than retrieval. Safety rules need tests in both directions; "
    "my own filter was blocking legitimate research. And automated graders make mistakes too, so I read "
    "the failures myself. Next, I need a clinician to review real answers, a Spanish speaker to review the "
    "held Spanish safety messages, and new evaluation questions covering the MotherToBaby referral, fact "
    "sheets and who funds this research, plus weekly freshness checks for the LactMed and MotherToBaby "
    "packages like the one MPRINT already has."))
text(s, 0.65, 1.6, 5.8, 0.4, "Lessons", size=20, font=HEAD, bold=True, color=TEAL)
lessons = [("Interpretation is the real work", "Retrieval was quick to build. Keeping populations, exposure and outcomes apart took most of the effort."),
           ("Test safety rules both ways", "My filter blocked research on seizures and postpartum depression until I tested for over-blocking."),
           ("Check the graders", "The model judge sometimes failed correct answers. I read every failure before changing anything.")]
for i, (head, body) in enumerate(lessons):
    y = 2.15 + i * 1.6
    box(s, 0.65, y, 5.85, 1.42, fill=MIST)
    text(s, 0.95, y + 0.15, 5.3, 0.4, head, size=16, bold=True, color=DEEP)
    text(s, 0.95, y + 0.55, 5.3, 0.85, body, size=14, color=INK)
text(s, 6.85, 1.6, 5.8, 0.4, "Next steps", size=20, font=HEAD, bold=True, color=TEAL)
nexts = ["Clinician review of real answers, especially for false reassurance or alarm",
         "Weekly freshness checks for the LactMed and MotherToBaby packages, as MPRINT already has",
         "Spanish-speaker review before enabling Spanish safety messages",
         "Add referral, fact sheet and \u201cwho funds this research?\u201d questions to the evaluation set",
         "Deploy the current version to the Databricks App"]
for i, t in enumerate(nexts):
    y = 2.15 + i * 0.98
    circle_num(s, 6.85, y - 0.04, str(i + 1), d=0.5, fill=CORAL, size=15)
    text(s, 7.6, y, 5.05, 0.9, t, size=15, color=INK, anchor=MSO_ANCHOR.TOP)

# 17 ─ Close
s = new(dark=True, notes="Thank you. The repository has the code, the full evaluation records and a quickstart.")
waves(s, 6.15, 0.95, [TEAL, PURPLE, RGBColor(0x9A, 0xA4, 0xF0), RGBColor(0xB9, 0xA6, 0xF2)])
text(s, 0.9, 2.2, 11.0, 1.2, "Thank you", size=54, font=HEAD, bold=True, color=WHITE)
text(s, 0.9, 3.5, 11.0, 1.4, [
    "Code, evaluation records and quickstart: GitHub repository Parent-Child-Pharmacology-MCP",
    "Evaluation document: documentation/Parent-child Pharmacology MCP - Evaluation.docx",
], size=18, color=MIST2, space_after=10)
text(s, 0.9, 5.6, 11.5, 0.9, [
    "A prototype for finding evidence and preparing for a clinician visit.",
    "It does not give medical advice, triage symptoms or replace clinical judgment.",
], size=14, color=MIST2, italic=True, space_after=4)

# ─── Appendix ───
s = new(dark=True, notes="Reference slides for judges who want more detail.")
text(s, 0.9, 2.6, 11.0, 1.0, "Appendix", size=48, font=HEAD, bold=True, color=WHITE)
text(s, 0.9, 3.7, 11.0, 1.6, ["All 31 tools  ·  Sources and their limits  ·  Full evaluation numbers",
                               "Benchmark history  ·  Prompts and resources"],
     size=18, color=MIST2, space_after=8)


def table(slide, x, y, w, col_w, rows, header=True, size=13, row_h=0.42):
    shp = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w),
                                 Inches(row_h * len(rows)))
    t = shp.table
    for ci, cw in enumerate(col_w):
        t.columns[ci].width = Inches(cw)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.cell(ri, ci)
            c.margin_left = c.margin_right = Inches(0.12)
            c.margin_top = c.margin_bottom = Inches(0.05)
            c.fill.solid()
            c.fill.fore_color.rgb = DEEP if (header and ri == 0) else (MIST if ri % 2 else WHITE)
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = ""
            r = p.add_run()
            r.text = val
            r.font.name = BODY
            r.font.size = Pt(size)
            r.font.bold = (header and ri == 0) or ci == 0
            r.font.color.rgb = WHITE if (header and ri == 0) else (TEAL if ci == 0 else INK)
    return t


s = new("All 31 tools", appendix=True, notes="The full tool list, grouped by job.")
table(s, 0.65, 1.5, 12.0, [2.6, 9.4], [
    ["Group", "Tools"],
    ["Identity", "normalize_drug, find_products_containing_ingredient, get_patient_education"],
    ["Breastfeeding", "search_lactmed, get_lactmed_record, semantic_search_lactmed, search_mothertobaby_fact_sheets"],
    ["Pregnancy and labels", "get_label_sections, search_pediatric_labeling_changes, find_pregnancy_exposure_registries, search_pregnancy_registries"],
    ["Literature and trials", "search_literature, get_abstracts, search_trials, find_recruiting_studies"],
    ["MPRINT data", "find_mprint_records, get_mprint_details"],
    ["NICHD programs", "search_funded_research, summarize_research_portfolio, search_bpca_evidence, search_nichd_studies"],
    ["Safety", "get_adverse_event_signals, search_medication_recalls, search_drug_safety_alerts, search_drug_shortages"],
    ["Parents", "route_parent_question, get_parent_medication_info, search_parent_input_opportunities, get_reporting_resources"],
    ["Composite", "medication_evidence_brief, check_evidence_coverage"],
], size=13, row_h=0.5)

s = new("Sources and what each one can support", appendix=True,
        notes="Each source answers a different part of the question, and each has limits the server reports.")
table(s, 0.65, 1.5, 12.0, [2.9, 9.1], [
    ["Source", "Used for, and its limit"],
    ["LactMed (NLM)", "Breastfeeding evidence from NCBI's official package, with PubMed links for each cited study."],
    ["DailyMed (NLM)", "Label sections 8.1 to 8.4. In-use labeling may differ from the latest FDA-approved version."],
    ["PubMed and PMC", "Studies and abstracts. Study type and population need separate checks."],
    ["ClinicalTrials.gov", "Registrations and recruiting status. No eligibility decisions."],
    ["openFDA", "FAERS reports, recalls, alerts, shortages. Report counts are not rates and don't show cause."],
    ["RxNorm and MedlinePlus", "Medicine identity and patient education, including Spanish pages by drug code."],
    ["MPRINT", "Published pharmacology tables (MIT license), as a dated read-only snapshot."],
    ["NIH RePORTER", "Funded projects and portfolios. An award is not a finding."],
    ["NICHD BPCA and DASH", "Pediatric study summaries and study discovery. Controlled data are not retrieved."],
    ["MotherToBaby (OTIS, via NLM)", "English and Spanish consumer fact sheets, verbatim and attributed. Nonprofit content."],
], size=13, row_h=0.46)

s = new("Full evaluation numbers", appendix=True,
        notes="All numbers are from the evaluated version and are reported separately because they measure different things.")
table(s, 0.65, 1.5, 12.0, [3.6, 3.4, 5.0], [
    ["Measure", "Result", "What it means"],
    ["Automated tests", "709 local; 709 Databricks", "No failures, errors or skips"],
    ["Grader unit tests", "33 passed", "The grading code itself is tested"],
    ["MCP Inspector", "9/9", "Protocol, schemas and sample contracts"],
    ["Scripted chats", "28/28 completed", "21 research and 7 stop cases"],
    ["Routes and tool checks", "28/28 and 28/28", "Checked from traces"],
    ["Stop cases", "7/7", "No downstream evidence or model calls"],
    ["Research answers", "17/21 fidelity; 21/21 tasks", "Separate model judgments"],
    ["Paired tasks", "MCP 7/7; plain 0/7", "Same model and instructions"],
    ["Paired fidelity (pass/fail/N/A)", "MCP 7/0/0; plain 1/5/1", "N/A is not counted as a pass"],
    ["Benchmark", "9/10 exact", "Fixed MPRINT snapshot, scored in Phoenix"],
], size=13, row_h=0.45)
text(s, 0.65, 6.75, 12.0, 0.4,
     "Evaluated on policy .14. Version 0.19.0 adds safety fixes, referrals, fact sheets, display checks and LactMed study links; all 861 tests pass on Databricks.",
     size=12, color=MUTED, italic=True)

s = new("Benchmark history: 3/10 to 9/10", appendix=True, notes=(
    "The same ten questions and references were used throughout. Most early failures came from the safety "
    "and language checks blocking legitimate research questions."))
hist = [("3/10", "Earlier version", "Three false safety stops, one arithmetic error, three wrong candidate sets"),
        ("10/10", "Intermediate run", "Bounded English task recognition, joined candidates, pagination"),
        ("9/10", "Evaluated version", "One answer copied the DOI of a different candidate")]
for i, (num, head, body) in enumerate(hist):
    x = 0.65 + i * 4.1
    box(s, x, 1.75, 3.8, 3.6, fill=MIST)
    text(s, x + 0.3, 2.0, 3.2, 1.0, num, size=48, font=HEAD, bold=True, color=TEAL)
    text(s, x + 0.3, 3.1, 3.2, 0.4, head, size=17, bold=True, color=DEEP)
    text(s, x + 0.3, 3.6, 3.2, 1.6, body, size=15, color=INK)
    if i < 2:
        connector(s, x + 3.8, 3.55, x + 4.1, 3.55, color=TEAL, width=2.5)
text(s, 0.65, 5.75, 12.0, 0.9,
     "Every run is kept, including the failures. No answer was replaced or corrected by hand.", size=15,
     color=INK)

s = new("Prompts and resources", appendix=True, notes="Reusable prompts and read-only resources any MCP client can use.")
text(s, 0.65, 1.6, 5.8, 0.4, "Prompts", size=20, font=HEAD, bold=True, color=TEAL)
for i, (name, body) in enumerate([
        ("breastfeeding_medication_check", "Guided lactation evidence review"),
        ("pregnancy_medication_check", "Guided pregnancy evidence review"),
        ("clinician_literature_scan", "Literature-first scan for clinicians"),
        ("questions_to_ask_clinician", "Turns evidence into visit questions")]):
    y = 2.15 + i * 1.1
    box(s, 0.65, y, 5.85, 0.95, fill=MIST)
    text(s, 0.95, y + 0.1, 5.4, 0.4, name, size=14, bold=True, color=DEEP, font="Courier New")
    text(s, 0.95, y + 0.5, 5.4, 0.4, body, size=14, color=INK)
text(s, 6.85, 1.6, 5.8, 0.4, "Resources", size=20, font=HEAD, bold=True, color=TEAL)
for i, (name, body) in enumerate([
        ("mother-child://sources", "Every source, its role and limits"),
        ("parent-child://capabilities", "What the server can and can't do"),
        ("parent-child://mprint-snapshot", "Snapshot revision, date and coverage"),
        ("parent-child://disclaimer", "The standard informational notice")]):
    y = 2.15 + i * 1.1
    box(s, 6.85, y, 5.8, 0.95, fill=MIST)
    text(s, 7.15, y + 0.1, 5.4, 0.4, name, size=14, bold=True, color=DEEP, font="Courier New")
    text(s, 7.15, y + 0.5, 5.4, 0.4, body, size=14, color=INK)

prs.core_properties.author = "Gabriela Piatkowski"
prs.core_properties.title = "Parent-child Pharmacology MCP"
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
