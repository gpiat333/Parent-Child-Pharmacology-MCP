"""Build the short demo slides for a self-narrated recording with a live Databricks demo.

Keeps eighteen slides from the main deck and the demo cards in scenes.json, adds live-demo and testing slides,
and puts a voiceover script in each slide's speaker notes. Three answer cards follow the closing
slide as backups, in case the live demo can't be recorded.

    python build_demo_slides.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v25.pptx"

Needs python-pptx only.
"""

import argparse
import json
from pathlib import Path

from cards import (
    CORAL,
    CORAL_T,
    DEEP,
    HEAD,
    INK,
    MIST,
    MIST2,
    MUTED,
    PURPLE,
    TEAL,
    WHITE,
    RGBColor,
    box,
    chat_card,
    grid_card,
    text,
)
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
POLICY = "2026-11-23.29"
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
    (
        "deck:GSA MCP Server and AI Agent Hackathon",
        "Hi. This is the Parent-child Pharmacology MCP, for the GSA MCP Server and AI Agent Hackathon, "
        "Dataset Access Server track. It's a server that lets AI assistants look up public evidence about "
        "medicines in pregnancy, breastfeeding and childhood. I'll show why I built it, and then the real "
        "server running in Databricks.",
    ),
    (
        "deck:2:07 a.m.",
        "Picture a new mom, awake at two in the morning. She takes Zoloft, and she's wondering whether it "
        "gets into her breast milk, and whether she should stop.",
    ),
    (
        "deck:At 2 a.m., every place she turns falls short",
        "Right now, every place she turns falls short. Her doctor's office is closed. A web search turns up "
        "forums. MotherToBaby's experts answer the next business day. And the best evidence, in LactMed, "
        "is written for clinicians. Why is this so hard?",
    ),
    (
        "deck:Many medicines lack data for pregnancy and for children",
        "Pregnant people and children are usually left out of the studies that establish a new medicine's "
        "safety. Fewer than 10 percent of medicines approved since 1980 have enough information to "
        "determine their safety in pregnancy, yet nine in ten women in the United States take a medication "
        "during pregnancy. And in 1997, fewer than 20 percent of prescription drugs were labeled for use in "
        "children.",
    ),
    (
        "deck:Two decades of federal programs and research have worked to close the gap",
        "For two decades, federal programs have worked to close that gap: the Best Pharmaceuticals for "
        "Children Act and the Pediatric Research Equity Act, NICHD's Obstetric and Pediatric Pharmacology and "
        "Therapeutics Branch, LactMed, the Pediatric Trials Network, FDA's Pregnancy and Lactation Labeling "
        "Rule, the PRGLAC task force and the MPRINT Hub. Each effort produced evidence, but each in a "
        "different place and format.",
    ),
    (
        "deck:The evidence gap is real, but a lot of evidence exists",
        "So the gap is real, but a lot of evidence exists: almost 2,000 LactMed drug records, 656 "
        "MotherToBaby fact sheets in English and Spanish, more than 3,800 curated MPRINT study records, and "
        "1.3 million PubMed records labeled by study type. PubMed, ClinicalTrials.gov, drug labels and FDA "
        "data are searched live, every time. And where evidence is missing, the server says so, and points "
        "to trials that are recruiting and to pregnancy registries. That is information only: it never ranks "
        "them, never recommends one, and never pushes anyone to sign up.",
    ),
    (
        "deck:However, what is known is scattered across agencies",
        "But what's known is scattered across agencies: the National Library of Medicine, FDA, NIH and "
        "NICHD, the National Institute of Child Health and Human Development. For a parent, a researcher or a clinician, that means different names, IDs and "
        "formats: public APIs, web pages, spreadsheets and PDFs. No single place connects them.",
    ),
    (
        "deck:One MCP server connects pregnancy, breastfeeding and pediatric data",
        "The evidence is also split by population. Pregnancy, breastfeeding and each age band of childhood "
        "are separate literatures in separate places. "
        "So I built one MCP server that connects them: LactMed, FDA drug labels, PubMed, "
        "ClinicalTrials.gov, MotherToBaby and NIH research data, through 21 tools. It follows her "
        "from pregnancy, to breastfeeding, to her child's medicines, with newborns, infants, children and "
        "teens kept separate. Every answer keeps its population labeled, so a finding in adults or older "
        "children is never passed off as evidence for a newborn.",
    ),
    (
        "deck:Should an AI assistant handle",
        "Should an AI assistant handle a topic this sensitive? I think yes, for four reasons. The evidence "
        "is already public; the question is whether people see it with its population, its date and its "
        "limits. The gaps matter as much as the findings, so saying no evidence was retrieved, and that "
        "this is not evidence of safety, is part of the answer. Research that families already paid for "
        "becomes usable. And it prepares, it doesn't decide: every brief ends with questions to bring to a "
        "clinician. On the right are the lines it won't cross: no personal treatment advice or doses, no "
        "diagnosis, and it never presents missing evidence as safe. For those questions it sends people "
        "to a clinician or pharmacist, MotherToBaby, 988, or 911 and Poison Help.",
    ),
    (
        "deck:Architecture: a safety check runs before any federal source is called",
        "Here's how it works. An AI client, like Claude Desktop, VS Code or the Databricks Playground, "
        "connects to the server. Every question goes through a safety check first, before any federal "
        "source is called. Then the server runs the right tool, and source adapters call live public APIs, "
        "or dated copies of MPRINT and LactMed, over allowlisted HTTPS only. On Databricks, model serving, "
        "MLflow, Apps and a serverless notebook handle evaluation, hosting and testing.",
    ),
    (
        "deck:Why 21 tools",
        "There are 21 tools. I started with 31 and merged the ones that overlapped, so each does one clear "
        "job and an AI can pick the right one. A typical question uses three: the safety check, an evidence "
        "brief that gathers every source in one call, and one follow-up if needed, like the full LactMed "
        "record. The rest are grouped by job: checking the medicine name, pregnancy and breastfeeding "
        "sources, studies and data, children's medicines and NIH programs, safety notices, and participation.",
    ),
    (
        "deck:All 21 tools and what each one does (1 of 2)",
        "Here's the full list of all 21 tools and what each one does: the safety check, matching a "
        "medicine's name, breastfeeding sources, drug labels, pregnancy registries and published studies.",
    ),
    (
        "deck:All 21 tools and what each one does (2 of 2)",
        "And the rest: clinical trials, MPRINT's pharmacology studies, NIH-funded research, FDA safety "
        "notices, and the all-in-one evidence brief.",
    ),
    (
        "live",
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
        "Tip: practice once, then click Reset chat so the recording starts clean.",
    ),
    (
        "card:safety",
        "Some questions need a person, not a search. If she says she feels hopeless, she gets 988 and the "
        "National Maternal Mental Health Hotline right away. Trying to trick it, like 'pretend you're my "
        "doctor', doesn't work. A vaccine decision goes to her pediatrician. And no, it won't order a pizza.",
    ),
    (
        "card:spanish",
        "Questions in Spanish don't get an automatic answer yet, because the safety rules are written and "
        "tested in English. But the reply itself is in Spanish, reviewed by a native speaker, and points to "
        "MotherToBaby, 988 in Spanish and MedlinePlus en español.",
    ),
    (
        "testing",
        "I tested it in several ways, not only on Databricks. The scored evaluation used OpenAI's "
        "GPT-5.6 Luna: scripted chats, side-by-side pairs with and without the server, and a benchmark. I "
        "also tested it by hand in Claude, which caught problems the automated tests missed, like answers "
        "that were cut off and plain English questions being blocked. All of those are fixed. Safety "
        "probes: trying to trick it doesn't work, off-topic requests stop, crisis language gets 988, and "
        "vaccine decisions go to a pediatrician, while questions about vaccines and autism, supplements, or "
        "what's in a medicine get evidence, not opinions. Questions in Spanish get a reply in Spanish, "
        "reviewed by a native speaker, and 36 everyday English phrasings are tested so normal questions "
        "aren't blocked. In all, 1,051 automated tests pass on my Mac and on Databricks.",
    ),
    (
        "deck:A design review cut 31 tools to 21",
        "After the first evaluation I had the server's code and design reviewed against the judging "
        "criteria. Every scripted chat had passed, but the review found things those tests couldn't see. "
        "One answer ran to a million and a half characters, too big for most AI clients to read. Several "
        "tools did nearly the same job. So I merged 31 tools into 21, made the evidence brief return a "
        "summary first, and fixed the safety rules the review flagged. Then I ran the whole evaluation "
        "again on the new version.",
    ),
    (
        "deck:Results: with the MCP",
        "Here are the scored results on the current version, tracked in MLflow on Databricks. With the "
        "server, the model completed all seven paired tasks. Without it, none. All 20 research answers "
        "stuck to their sources, 19 of 20 did everything asked, and the benchmark got ten of ten exact "
        "answers.",
    ),
    (
        "deck:Thank you",
        "It doesn't replace a clinician. It helps families, clinicians and researchers find what's known, "
        "see what isn't, and know who to call. Thank you.",
    ),
    (
        "backup:lactmed",
        "BACKUP, only if the live demo can't be recorded. A real answer: the LactMed record for sertraline, "
        "with milk levels linked to their studies, and what's missing.",
    ),
    (
        "backup:brief",
        "BACKUP. An evidence brief keeps three things apart: effects on her, how much reaches the baby, and "
        "what was seen in babies. It ends with questions for her clinician.",
    ),
    (
        "backup:can-i-take",
        "BACKUP. Asked 'Can I take ibuprofen?', it won't say yes or no. It shares the evidence, says the "
        "decision belongs with her clinician or pharmacist, and gives MotherToBaby's free number.",
    ),
]


def live_demo_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = DEEP
    text(s, 0.65, 0.5, 8.0, 0.4, "LIVE DEMO", size=14, bold=True, color=MIST2)
    text(
        s,
        0.65,
        0.95,
        12.0,
        0.8,
        "Now the real server, running in Databricks",
        size=36,
        font=HEAD,
        bold=True,
        color=WHITE,
    )
    text(
        s,
        0.65,
        1.85,
        12.0,
        0.5,
        "The deployed Databricks App, added to the Databricks AI Playground as an MCP tool.",
        size=18,
        color=MIST2,
    )
    for i, (question, shows) in enumerate(LIVE_QUESTIONS):
        x, y, w, h = 0.65 + i * 4.1, 2.75, 3.85, 3.5
        box(s, x, y, w, h, CARD_DEEP, radius=0.05)
        dot = s.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x + 0.3), Inches(y + 0.3), Inches(0.55), Inches(0.55)
        )
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
        text(
            s,
            x + 0.3,
            y + 1.05,
            w - 0.6,
            1.4,
            f"“{question}”",
            size=18,
            font=HEAD,
            italic=True,
            color=WHITE,
        )
        text(s, x + 0.3, y + 2.3, w - 0.6, 1.1, shows, size=14, color=MIST2)
    text(
        s,
        0.65,
        6.85,
        12.0,
        0.4,
        f"Databricks App mcp-mc, version 0.22.2, policy {POLICY}. Answers are generated live and vary between runs.",
        size=12,
        italic=True,
        color=MIST2,
    )


TESTS = [
    (
        "GPT (OpenAI)",
        "27 chats, 7 pairs",
        "GPT-5.6 Luna through Databricks: research and must-stop questions, MCP-versus-no-tools pairs and a "
        "10-question benchmark, model-graded in MLflow.",
    ),
    (
        "Claude (Anthropic)",
        "Hands-on chats",
        "Claude Desktop and the Claude app found cut-off LactMed answers, missing study links and blocked "
        "plain English like “Link the studies.” All fixed.",
    ),
    (
        "Safety probes",
        "Jailbreaks fail",
        "Off-topic requests stop, crisis language gets 988, vaccine decisions go to a pediatrician. "
        "Vaccine–autism, supplement and drug-chemistry questions get evidence.",
    ),
    (
        "Languages",
        "English and Spanish",
        "Spanish, French and mixed questions stop with a referral; Spanish ones get it in Spanish, reviewed "
        "by a native speaker. 36 everyday English requests must pass.",
    ),
    (
        "Automated tests",
        "1,051 pass",
        "On a Mac and in a Databricks serverless notebook, including the safety, referral and language "
        "tests. MCP Inspector: 9 of 9 protocol checks.",
    ),
    (
        "Live deployment",
        "Databricks App",
        "Runs behind Databricks sign-in, checked with a live MCP handshake, and used from the AI Playground "
        "with Claude Opus 5 in this demo.",
    ),
]


def testing_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    text(s, 0.65, 0.4, 8.0, 0.4, "HOW IT WAS TESTED", size=13, bold=True, color=TEAL)
    text(
        s,
        0.65,
        0.8,
        12.0,
        0.7,
        "Tested with GPT and Claude, safety probes and Spanish",
        size=30,
        font=HEAD,
        bold=True,
        color=DEEP,
    )
    for i, (tag, stat, detail) in enumerate(TESTS):
        x, y = 0.65 + (i % 3) * 4.11, 1.75 + (i // 3) * 2.6
        safety = tag == "Safety probes"
        box(s, x, y, 3.81, 2.4, CORAL_T if safety else MIST, radius=0.06)
        text(
            s, x + 0.3, y + 0.2, 3.21, 0.3, tag, size=14, bold=True, color=CORAL if safety else TEAL
        )
        text(s, x + 0.3, y + 0.52, 3.21, 0.5, stat, size=24, font=HEAD, bold=True, color=DEEP)
        text(s, x + 0.3, y + 1.1, 3.21, 1.2, detail, size=14, color=INK, space_after=0)
    text(
        s,
        0.65,
        6.95,
        12.0,
        0.4,
        "Known development questions; model outputs graded by a model. No clinician review yet.",
        size=12,
        italic=True,
        color=MUTED,
    )


def find_deck_slide(slides, needle):
    for slide in slides:
        if any(
            sh.has_text_frame and sh.text_frame.text.strip().startswith(needle)
            for sh in slide.shapes
        ):
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
    ap.add_argument(
        "--out", default=str(HERE.parent / "Parent-child Pharmacology MCP — Demo slides.pptx")
    )
    args = ap.parse_args()
    cards = {
        s["id"]: s["card"]
        for s in json.loads(Path(args.scenes).read_text(encoding="utf-8"))["scenes"]
        if "card" in s
    }
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
        elif kind in ("live", "testing"):
            (live_demo_slide if kind == "live" else testing_slide)(prs)
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
    for r_id in [
        r
        for r in list(prs.part.rels)
        if prs.part.rels[r].reltype.endswith("/slide") and r not in keep
    ]:
        prs.part.drop_rel(r_id)
    prs.save(args.out)
    print(f"{len(ordered)} slides -> {args.out}")


if __name__ == "__main__":
    main()
