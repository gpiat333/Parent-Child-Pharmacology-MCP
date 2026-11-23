"""Build the short demo slides for a self-narrated recording with a live Databricks demo.

Keeps twelve slides from the main deck and the demo cards in scenes.json, adds a live-demo slide,
and puts a voiceover script in each slide's speaker notes. Three answer cards follow the closing
slide as backups, in case the live demo can't be recorded.

    python build_demo_slides.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v24.pptx"

Needs python-pptx only.
"""

import argparse
import json
from pathlib import Path

from cards import DEEP, HEAD, MIST2, PURPLE, WHITE, RGBColor, box, chat_card, grid_card, text
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
POLICY = "2026-11-23.27"
CARD_DEEP = RGBColor(0x3A, 0x39, 0x86)

LIVE_QUESTIONS = [
    (
        "What does LactMed say about sertraline and breastfeeding? Link the studies.",
        "Levels measured in breast milk, each linked to its study, and what the record doesn't say.",
    ),
    (
        "Should I stop taking sertraline while breastfeeding?",
        "It won't decide for her. It points to her prescriber or pharmacist, and MotherToBaby's free line.",
    ),
    (
        "What is the research on pregnancy and Advil?",
        "The brand name Advil matched to its ingredient, ibuprofen, then evidence with source links.",
    ),
]

# (what to show, speaker notes). Deck slides are found by text they contain, so deck edits don't break this.
SLIDES = [
    ("deck:GSA MCP Server and AI Agent Hackathon",
     "Hi. This is the Parent-child Pharmacology MCP, for the GSA MCP Server and AI Agent Hackathon, "
     "Dataset Access Server track. It's a server that lets AI assistants look up public evidence about "
     "medicines in pregnancy, breastfeeding and childhood. I'll show why I built it, and then the real "
     "server running in Databricks."),
    ("deck:2:07 a.m.",
     "Picture a new mom, awake at two in the morning. She takes Zoloft, and she's wondering whether it "
     "gets into her breast milk, and whether she should stop."),
    ("deck:At 2 a.m., every place she turns falls short",
     "Right now, every place she turns falls short. Her doctor's office is closed. A web search turns up "
     "forums. MotherToBaby's experts answer the next business day. And the best evidence, in LactMed, "
     "is written for clinicians. Why is this so hard?"),
    ("deck:Many medicines lack data for pregnancy and for children",
     "Pregnant people and children are usually left out of the studies that establish a new medicine's "
     "safety. Fewer than 10 percent of medicines approved since 1980 have enough information to "
     "determine their safety in pregnancy, yet nine in ten women in the United States take a medication "
     "during pregnancy. And in 1997, fewer than 20 percent of prescription drugs were labeled for use in "
     "children."),
    ("deck:Two decades of federal programs and research have worked to close the gap",
     "For two decades, federal programs have worked to close that gap: the Best Pharmaceuticals for "
     "Children Act and the Pediatric Research Equity Act, NICHD's Obstetric and Pediatric Pharmacology and "
     "Therapeutics Branch, LactMed, the Pediatric Trials Network, FDA's Pregnancy and Lactation Labeling "
     "Rule, the PRGLAC task force and the MPRINT Hub. Each effort produced evidence, but each in a "
     "different place and format."),
    ("deck:The evidence gap is real, but a lot of evidence exists",
     "So the gap is real, but a lot of evidence exists: almost 2,000 LactMed drug records, 656 "
     "MotherToBaby fact sheets in English and Spanish, more than 3,800 curated MPRINT study records, and "
     "1.3 million PubMed records labeled by study type. PubMed, ClinicalTrials.gov, drug labels and FDA "
     "data are searched live, every time. And where evidence is missing, the server says so."),
    ("deck:However, what is known is scattered across agencies",
     "But what's known is scattered across agencies: NLM, FDA, NIH and NICHD, and nonprofits like "
     "MotherToBaby. For a parent, a researcher or a clinician, that means different names, IDs and "
     "formats: public APIs, web pages, spreadsheets and PDFs. No single place connects them."),
    ("deck:One MCP server connects pregnancy, breastfeeding and pediatric data",
     "So I built one MCP server that connects them: LactMed, FDA drug labels, PubMed, "
     "ClinicalTrials.gov, MotherToBaby and NIH research data, through 31 tools. It follows her "
     "from pregnancy, to breastfeeding, to her child's medicines, with newborns, infants, children and "
     "teens kept separate."),
    ("live",
     "Here it is live. The server is deployed as a Databricks App, and I've added it to the Databricks "
     "AI Playground as a tool.\n\n"
     "[Switch to the Playground recording.]\n\n"
     "Question 1: What does LactMed say about sertraline and breastfeeding? Link the studies.\n"
     "Point out: it calls the server's tools, reports the levels measured in breast milk, links each "
     "number to its study, and says what the record doesn't cover.\n\n"
     "Question 2: Should I stop taking sertraline while breastfeeding?\n"
     "Point out: it won't make that decision. It says to ask the prescriber or a pharmacist, and gives "
     "MotherToBaby's free number.\n\n"
     "Question 3 (optional): What is the research on pregnancy and Advil?\n"
     "Point out: it matches the brand name Advil to its ingredient, ibuprofen, before searching, and "
     "links every source it uses.\n\n"
     "Tip: practice once, then click Reset chat so the recording starts clean."),
    ("card:safety",
     "Some questions need a person, not a search. If she says she feels hopeless, she gets 988 and the "
     "National Maternal Mental Health Hotline right away. Trying to trick it, like 'pretend you're my "
     "doctor', doesn't work. A vaccine decision goes to her pediatrician. And no, it won't order a pizza."),
    ("card:spanish",
     "Questions in Spanish don't get an automatic answer yet, because the safety rules are written and "
     "tested in English. But the reply itself is in Spanish, reviewed by a native speaker, and points to "
     "MotherToBaby, 988 in Spanish and MedlinePlus en español."),
    ("deck:Results: with the MCP",
     "I tested it with scripted chats, side-by-side comparisons with and without the server, and an "
     "exact-answer benchmark, all tracked in MLflow on Databricks. With the server, the model completed "
     "all seven paired tasks. Without it, none. Every research answer stuck to its sources, and the "
     "benchmark got ten of ten exact answers."),
    ("deck:Thank you",
     "It doesn't replace a clinician. It helps families, clinicians and researchers find what's known, "
     "see what isn't, and know who to call. Thank you."),
    ("backup:lactmed",
     "BACKUP, only if the live demo can't be recorded. A real answer: the LactMed record for sertraline, "
     "with milk levels linked to their studies, and what's missing."),
    ("backup:brief",
     "BACKUP. An evidence brief keeps three things apart: effects on her, how much reaches the baby, and "
     "what was seen in babies. It ends with questions for her clinician."),
    ("backup:can-i-take",
     "BACKUP. Asked 'Can I take ibuprofen?', it won't say yes or no. It shares the evidence, says the "
     "decision belongs with her clinician or pharmacist, and gives MotherToBaby's free number."),
]


def live_demo_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = DEEP
    text(s, 0.65, 0.5, 8.0, 0.4, "LIVE DEMO", size=14, bold=True, color=MIST2)
    text(s, 0.65, 0.95, 12.0, 0.8, "Now the real server, running in Databricks", size=36, font=HEAD,
         bold=True, color=WHITE)
    text(s, 0.65, 1.85, 12.0, 0.5,
         "The deployed Databricks App, added to the Databricks AI Playground as an MCP tool.",
         size=18, color=MIST2)
    for i, (question, shows) in enumerate(LIVE_QUESTIONS):
        x, y, w, h = 0.65 + i * 4.1, 2.75, 3.85, 3.5
        box(s, x, y, w, h, CARD_DEEP, radius=0.05)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.3), Inches(y + 0.3), Inches(0.55), Inches(0.55))
        dot.fill.solid()
        dot.fill.fore_color.rgb = PURPLE
        dot.line.fill.background()
        dot.shadow.inherit = False
        tf = dot.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        run = tf.paragraphs[0].add_run()
        run.text = str(i + 1)
        run.font.size, run.font.bold, run.font.color.rgb = Pt(18), True, WHITE
        tf.paragraphs[0].alignment = 2  # center
        text(s, x + 0.3, y + 1.05, w - 0.6, 1.4, f"“{question}”", size=18, font=HEAD, italic=True, color=WHITE)
        text(s, x + 0.3, y + 2.3, w - 0.6, 1.1, shows, size=14, color=MIST2)
    text(s, 0.65, 6.85, 12.0, 0.4,
         f"Databricks App mcp-mc, policy {POLICY}. Answers are generated live and vary between runs.",
         size=12, italic=True, color=MIST2)


def find_deck_slide(slides, needle):
    for slide in slides:
        if any(sh.has_text_frame and sh.text_frame.text.strip().startswith(needle) for sh in slide.shapes):
            return slide
    raise SystemExit(f"No deck slide has text starting with {needle!r}")


def drop_slide_number(slide, number):
    """Main-deck slides carry their deck position (for example "15"), which is wrong in the short deck."""
    for sh in list(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip() == str(number):
            sh._element.getparent().remove(sh._element)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--scenes", default=str(HERE / "scenes.json"))
    ap.add_argument("--out", default=str(HERE.parent / "Parent-child Pharmacology MCP — Demo slides.pptx"))
    args = ap.parse_args()
    cards = {s["id"]: s["card"] for s in json.loads(Path(args.scenes).read_text(encoding="utf-8"))["scenes"]
             if "card" in s}
    for card in cards.values():
        card["footer"] = card["footer"].replace("policy 2026-11-23.26", f"policy {POLICY}")

    prs = Presentation(args.deck)
    original = list(prs.slides)
    ordered = []
    for key, notes in SLIDES:
        kind, _, name = key.partition(":")
        if kind == "deck":
            slide = find_deck_slide(original, name)
            drop_slide_number(slide, original.index(slide) + 1)
        elif kind == "live":
            live_demo_slide(prs)
            slide = prs.slides[-1]
        else:
            card = dict(cards[name])
            if kind == "backup":
                card["label"] = "Backup: " + card["label"]
            (grid_card if card["kind"] == "grid" else chat_card)(prs, card)
            slide = prs.slides[-1]
        slide.notes_slide.notes_text_frame.text = notes
        ordered.append(slide)

    # Keep only the chosen slides, in order; dropping a slide's relationship leaves it out of the saved file.
    id_list = prs.slides._sldIdLst
    by_part = {prs.part.related_part(e.rId): e for e in id_list}
    for e in list(id_list):
        id_list.remove(e)
    keep = set()
    for slide in ordered:
        id_list.append(by_part[slide.part])
        keep.add(by_part[slide.part].rId)
    for r_id in [r for r in list(prs.part.rels) if prs.part.rels[r].reltype.endswith("/slide") and r not in keep]:
        prs.part.drop_rel(r_id)
    prs.save(args.out)
    print(f"{len(ordered)} slides -> {args.out}")


if __name__ == "__main__":
    main()
