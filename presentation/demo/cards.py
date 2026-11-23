"""Slide-card drawing shared by the narrated video (build_demo.py) and the demo slides (build_demo_slides.py)."""

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

DEEP = RGBColor(0x2A, 0x29, 0x6B)
TEAL = RGBColor(0x46, 0x50, 0xC4)
PURPLE = RGBColor(0x7B, 0x5C, 0xD6)
MIST = RGBColor(0xEE, 0xF0, 0xFB)
MIST2 = RGBColor(0xCF, 0xD4, 0xF4)
CORAL = RGBColor(0xC8, 0x55, 0x3D)
CORAL_T = RGBColor(0xFB, 0xEA, 0xE5)
INK = RGBColor(0x2B, 0x2B, 0x3A)
MUTED = RGBColor(0x6B, 0x6E, 0x86)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEAD, BODY = "Cambria", "Calibri"


def text(slide, x, y, w, h, paras, size=18, color=INK, font=BODY, bold=False, italic=False,
         anchor=MSO_ANCHOR.TOP, space_after=6):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate([paras] if isinstance(paras, str) else paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = para
        r.font.name, r.font.size, r.font.bold, r.font.italic = font, Pt(size), bold, italic
        r.font.color.rgb = color
    return tb


def box(slide, x, y, w, h, fill, radius=0.06):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = radius
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def chat_card(prs, card):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    text(s, 0.65, 0.4, 8.0, 0.4, card["label"].upper(), size=13, bold=True, color=TEAL)
    # The user's question, as a chat bubble.
    box(s, 0.65, 0.95, 12.0, 1.15, MIST, radius=0.25)
    text(s, 0.95, 0.95, 11.4, 1.15, card["question"], size=24, font=HEAD, italic=True, color=DEEP,
         anchor=MSO_ANCHOR.MIDDLE)
    # The reply.
    box(s, 0.65, 2.35, 12.0, 4.45, DEEP, radius=0.04)
    text(s, 1.0, 2.55, 11.3, 0.6, card["answer_title"], size=26, font=HEAD, bold=True, color=WHITE)
    text(s, 1.0, 3.35, 11.3, 3.4, ["•  " + line for line in card["lines"]], size=21,
         color=MIST2, space_after=12)
    text(s, 0.65, 6.95, 12.0, 0.4, card["footer"], size=12, italic=True, color=MUTED)


def grid_card(prs, card):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    text(s, 0.65, 0.4, 8.0, 0.4, card["label"].upper(), size=13, bold=True, color=TEAL)
    text(s, 0.65, 0.8, 12.0, 0.7, card["title"], size=30, font=HEAD, bold=True, color=DEEP)
    for i, item in enumerate(card["items"]):
        x, y = 0.65 + (i % 2) * 6.1, 1.75 + (i // 2) * 2.55
        box(s, x, y, 5.9, 2.35, CORAL_T if i == 0 else MIST, radius=0.06)
        text(s, x + 0.3, y + 0.18, 5.3, 0.4, item["tag"], size=15, bold=True, color=CORAL if i == 0 else TEAL)
        text(s, x + 0.3, y + 0.6, 5.3, 0.8, item["question"], size=17, italic=True, color=DEEP)
        text(s, x + 0.3, y + 1.4, 5.3, 0.9, item["reply"], size=16, color=INK)
    text(s, 0.65, 6.95, 12.0, 0.4, card["footer"], size=12, italic=True, color=MUTED)
