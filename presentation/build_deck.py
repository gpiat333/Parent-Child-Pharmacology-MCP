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

# Palette: deep teal-green ink, a soft mist tint, one warm coral accent.
DEEP = RGBColor(0x12, 0x3B, 0x3A)
TEAL = RGBColor(0x0E, 0x5E, 0x5C)
MIST = RGBColor(0xEC, 0xF3, 0xF2)
MIST2 = RGBColor(0xD8, 0xE8, 0xE6)
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
text(s, 0.9, 1.6, 9.5, 0.5, "GSA MCP Server and AI Agent Hackathon  ·  Dataset Access Server track",
     size=14, color=MIST2)
text(s, 0.9, 2.2, 11.0, 1.9, ["Parent-child", "Pharmacology MCP"], size=54, font=HEAD, bold=True,
     color=WHITE, space_after=0, line=0.95)
text(s, 0.9, 4.25, 10.0, 1.0,
     "Public evidence on medicines in pregnancy, breastfeeding and childhood, ready for AI assistants",
     size=20, color=MIST2)
text(s, 0.9, 5.55, 9.0, 1.0, [
    [("Gabriela Piatkowski, MS", {"bold": True, "color": WHITE})],
    "Program Analyst, Obstetric and Pediatric Pharmacology and Therapeutics Branch, NICHD",
], size=14, color=MIST2, space_after=2)
text(s, 0.9, 6.75, 11.5, 0.4,
     "Built as a hackathon prototype. Not an official NIH product or medical advice.", size=11,
     color=MIST2, italic=True)

# 2 ─ The questions
s = new("People ask the same kinds of questions", notes=(
    "These are the kinds of questions I hear in this field. Parents want to prepare for a conversation with "
    "their doctor. Clinicians and researchers want the primary evidence, with its population and dates. "
    "The answers exist in public federal resources, but they are spread out."))
cols = [
    ("Parents and caregivers", [
        "I take Zoloft and just found out I'm pregnant. What research can help me talk with my doctor?",
        "I'm breastfeeding and have a headache. What do we know about Advil getting into breast milk?",
        "My child's bottle says Keppra. What is that, and has it been studied in kids?"]),
    ("Clinicians and researchers", [
        "What does LactMed report about sertraline in breast milk and observed infant effects?",
        "What published studies examine metformin during pregnancy?",
        "What did NICHD fund in neonatal pharmacology in FY 2024 and FY 2025?"]),
]
for ci, (head, qs) in enumerate(cols):
    x = 0.65 + ci * 6.15
    text(s, x, 1.6, 5.8, 0.4, head, size=18, bold=True, color=TEAL)
    for qi, q in enumerate(qs):
        y = 2.2 + qi * 1.55
        box(s, x, y, 5.85, 1.35, fill=MIST if ci == 0 else CORAL_T)
        text(s, x + 0.3, y + 0.2, 5.25, 1.0, f"“{q}”", size=16, color=INK, italic=True,
             anchor=MSO_ANCHOR.MIDDLE)

# 2b ─ The evidence is thin
s = new("The evidence itself is thin", notes=(
    "CDC puts the problem in one number. Fewer than ten percent of medicines approved since 1980 have "
    "enough information to determine their safety during pregnancy, yet nine in ten women take a medication "
    "while pregnant. Pregnant people are usually left out of the trials that establish a new drug's safety. "
    "So for most questions, the honest answer includes what is not known, and the tool has to show that. "
    "Congress created PRGLAC, the Task Force on Research Specific to Pregnant Women and Lactating Women, in "
    "the 21st Century Cures Act. Its 2018 report made 15 recommendations, and NICHD's Council tracks "
    "implementation. Pregnancy and lactation briefs now include that context, so an empty evidence row is "
    "read as a known research gap, not as safety."))
box(s, 0.65, 1.7, 5.85, 3.9, fill=DEEP)
text(s, 1.0, 1.95, 5.2, 1.4, "<10%", size=72, font=HEAD, bold=True, color=WHITE)
text(s, 1.0, 3.45, 5.2, 2.0,
     "of medicines approved since 1980 have enough information to determine their safety during pregnancy",
     size=18, color=MIST2)
box(s, 6.85, 1.7, 5.8, 3.9, fill=MIST)
text(s, 7.2, 1.95, 5.2, 1.4, "9 in 10", size=72, font=HEAD, bold=True, color=TEAL)
text(s, 7.2, 3.45, 5.1, 2.0, "women in the United States take a medication during pregnancy", size=18, color=INK)
text(s, 0.65, 5.85, 12.0, 1.0, [
    [("Why: ", {"bold": True, "color": DEEP}),
     ("pregnant people are usually left out of the studies that establish a new medicine's safety. NICHD's "
      "PRGLAC task force made 15 recommendations in 2018 to close this gap; pregnancy and lactation briefs "
      "now link to them.", {})]], size=15, color=INK)
text(s, 0.65, 6.95, 9.5, 0.35,
     "Source: CDC, Medicine and Pregnancy: An Overview, and Treating for Two (cdc.gov/medicine-and-pregnancy).",
     size=11, color=MUTED, italic=True)

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

# 4 ─ Interpretation traps
s = new("Finding the record is the easy part", notes=(
    "The harder problem is reading what you find. These three mistakes are easy for a person or an AI to "
    "make, and each one can push someone toward stopping a medicine they need. The server is designed so "
    "these distinctions travel with the data."))
traps = [
    ("1", "An empty search looks like good news",
     "Usually it means nobody studied it in this population. The server returns an explicit "
     "“no evidence retrieved; not evidence of safety” flag."),
    ("2", "A level in breast milk gets read as harm",
     "Exposure and infant outcomes are different findings. The server keeps them in separate rows, with "
     "maternal effects in a third."),
    ("3", "Report counts get read as risk",
     "FDA adverse-event reports have no denominator and do not show cause. The counts carry those "
     "caveats in the payload."),
]
for i, (n, head, body) in enumerate(traps):
    x = 0.65 + i * 4.1
    box(s, x, 1.75, 3.8, 4.4, fill=MIST)
    circle_num(s, x + 0.35, 2.1, n, d=0.6, fill=CORAL, size=20)
    text(s, x + 0.35, 2.95, 3.15, 1.1, head, size=20, font=HEAD, bold=True, color=DEEP)
    text(s, x + 0.35, 4.1, 3.15, 1.9, body, size=16, color=INK)
text(s, 0.65, 6.45, 12.0, 0.4,
     "Each of these can push someone toward stopping a medicine they need.", size=16, color=CORAL,
     bold=True)

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
      "people to MotherToBaby (866-626-6847) and links their fact sheets.", {})]], size=15, color=INK)

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
text(s, 4.75, 6.4, 3.4, 0.7, "MPRINT snapshot, dated and checked", size=14, bold=True, color=WHITE,
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
    "snapshot resource checks MPRINT's GitHub for newer data, and a weekly GitHub job fails if there is."))
decs = [
    ("Tools for goals, not endpoints", "medication_evidence_brief and check_evidence_coverage each combine "
     "several sources, so an agent makes one meaningful call instead of eight thin ones."),
    ("Confirm the medicine first", "RxNorm resolves brand names to ingredients. An uncertain match returns "
     "requires_confirmation; a description of a pill stops the request."),
    ("Missing stays missing", "Empty searches, absent label sections and truncated records are explicit "
     "fields. A failed source is reported as unavailable, not as zero."),
    ("Dated, checkable snapshots", "MPRINT tables ship as read-only SQLite. Every result shows the copy's date, "
     "and a weekly check flags newer upstream data."),
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
    "I tested in layers. 768 automated tests pass both on my machine and in a Databricks serverless notebook. "
    "MCP Inspector checked the protocol and schemas. Then 28 scripted chats: 21 research questions and 7 that "
    "should stop. Seven questions were run twice, once with the MCP and once with the same model and no tools. "
    "Finally, a 10-question exact-answer benchmark against the MPRINT snapshot, scored in Arize Phoenix. "
    "Model-graded results are tracked in MLflow."))
tests = [
    ("768", "automated tests", "All pass locally and in a Databricks serverless notebook"),
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
    "sheets and who funds this research. The fact sheet tool links sheets but doesn't read them yet, because "
    "NLM's site shows automated readers a browser check, and I won't work around it."))
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
         "Read MotherToBaby fact sheet text once NLM allows automated access; today the server links them",
         "Spanish-speaker review before enabling Spanish safety messages",
         "Add referral, fact sheet and \u201cwho funds this research?\u201d questions to the evaluation set",
         "Deploy the current version to the Databricks App"]
for i, t in enumerate(nexts):
    y = 2.15 + i * 0.98
    circle_num(s, 6.85, y - 0.04, str(i + 1), d=0.5, fill=CORAL, size=15)
    text(s, 7.6, y, 5.05, 0.9, t, size=15, color=INK, anchor=MSO_ANCHOR.TOP)

# 17 ─ Close
s = new(dark=True, notes="Thank you. The repository has the code, the full evaluation records and a quickstart.")
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
                               "Six ways an answer can mislead  ·  Benchmark history  ·  Prompts and resources"],
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
    ["LactMed (NLM)", "Breastfeeding evidence. Lactation only; missing or truncated sections are reported."],
    ["DailyMed (NLM)", "Label sections 8.1 to 8.4. In-use labeling may differ from the latest FDA-approved version."],
    ["PubMed and PMC", "Studies and abstracts. Study type and population need separate checks."],
    ["ClinicalTrials.gov", "Registrations and recruiting status. No eligibility decisions."],
    ["openFDA", "FAERS reports, recalls, alerts, shortages. Report counts are not rates and don't show cause."],
    ["RxNorm and MedlinePlus", "Medicine identity and patient education, including Spanish pages by drug code."],
    ["MPRINT", "Published pharmacology tables (MIT license), as a dated read-only snapshot."],
    ["NIH RePORTER", "Funded projects and portfolios. An award is not a finding."],
    ["NICHD BPCA and DASH", "Pediatric study summaries and study discovery. Controlled data are not retrieved."],
    ["MotherToBaby (OTIS, via NLM)", "English and Spanish consumer fact sheets. Nonprofit content; links only."],
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
     "Evaluated on policy .14. Policies .15 to .17 add safety fixes, referrals and fact sheets; all 768 tests pass on Databricks.",
     size=12, color=MUTED, italic=True)

s = new("Six ways an answer can mislead", appendix=True, notes=(
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
