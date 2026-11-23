"""Build the narrated demo video from scenes.json.

Edit scenes.json (narration, card text, which deck slide to show) and re-run:

    python build_demo.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v20.pptx" --out demo.mp4

Needs: python-pptx, pypdfium2, Pillow, imageio-ffmpeg, LibreOffice, and macOS `say`.
Narration uses the engine and voice in scenes.json: "edge" (Microsoft neural voices via the edge-tts
package; the narration text is sent to Microsoft's speech service) or "say" (a macOS voice; if it is
not installed, the fallback voice is used and the manifest says so).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
import pypdfium2
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

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


def render_pdf(pptx, workdir):
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(workdir), str(pptx)],
                   check=True, capture_output=True)
    return workdir / (pptx.stem + ".pdf")


def pdf_pages(pdf, prefix, workdir):
    doc = pypdfium2.PdfDocument(str(pdf))
    paths = []
    for i in range(len(doc)):
        path = workdir / f"{prefix}{i + 1:02d}.png"
        doc[i].render(scale=2.0).to_pil().convert("RGB").resize((1920, 1080)).save(path)
        paths.append(path)
    return paths


def deck_titles(deck):
    titles = []
    for slide in Presentation(str(deck)).slides:
        lines = [sh.text_frame.text.strip() for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
        titles.append(lines[0] if lines else "")
    return titles


def available_voice(name):
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    return any(line.startswith(name + " ") or line.startswith(name + "  ") or line.split("  ")[0].strip() == name
               for line in out.splitlines())


def seconds(path):
    out = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def vtt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default=str(HERE / "scenes.json"))
    ap.add_argument("--deck", required=True)
    ap.add_argument("--out", default=str(HERE / "demo.mp4"))
    ap.add_argument("--voice", default=None, help="Override the voice in scenes.json")
    args = ap.parse_args()
    spec = json.loads(Path(args.scenes).read_text(encoding="utf-8"))
    deck = Path(args.deck)
    if not deck.is_absolute():
        deck = (Path(args.scenes).parent / deck).resolve()
    engine = spec.get("engine", "say")
    voice = args.voice or spec["voice"]
    if engine == "say" and not available_voice(voice):
        print(f"Voice {voice!r} is not installed; using {spec['fallback_voice']!r}.", file=sys.stderr)
        voice = spec["fallback_voice"]
    edge = shutil.which("edge-tts") or str(Path(sys.executable).with_name("edge-tts"))
    work = Path(tempfile.mkdtemp(prefix="demo-build-"))

    # Frames: rendered deck slides plus demo cards.
    titles = deck_titles(deck)
    deck_png = pdf_pages(render_pdf(deck, work), "deck", work)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    card_index = {}
    for scene in spec["scenes"]:
        if "card" in scene:
            card_index[scene["id"]] = len(prs.slides)
            (grid_card if scene["card"]["kind"] == "grid" else chat_card)(prs, scene["card"])
    cards_pptx = work / "cards.pptx"
    prs.save(cards_pptx)
    card_png = pdf_pages(render_pdf(cards_pptx, work), "card", work) if card_index else []

    segments, cues, manifest, t = [], [], [], 0.0
    for n, scene in enumerate(spec["scenes"]):
        if "card" in scene:
            frame = card_png[card_index[scene["id"]]]
        elif "deck_index" in scene:
            frame = deck_png[scene["deck_index"] - 1]
        else:
            match = [i for i, title in enumerate(titles) if title.startswith(scene["deck_title"])]
            if not match:
                raise SystemExit(f"No deck slide starts with {scene['deck_title']!r}")
            frame = deck_png[match[0]]
        if engine == "edge":
            # Microsoft neural voice via edge-tts: only the narration text is sent to the speech service.
            audio = work / f"a{n:02d}.mp3"
            subprocess.run([edge, "--voice", voice, f"--rate={spec.get('rate', '+0%')}",
                            "--text", scene["narration"], "--write-media", str(audio)], check=True,
                           capture_output=True)
        else:
            audio = work / f"a{n:02d}.aiff"
            subprocess.run(["say", "-v", voice, "-r", str(spec.get("rate_wpm", 170)), "-o", str(audio),
                            scene["narration"]], check=True)
        speech = seconds(audio)
        duration = speech + 1.2
        frames = int(duration * 30)
        seg = work / f"s{n:02d}.mp4"
        vf = (f"scale=2112:1188,zoompan=z='1+0.035*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s=1920x1080:fps=30,fade=t=in:st=0:d=0.35,fade=t=out:st={duration - 0.35:.2f}:d=0.35,format=yuv420p")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(frame), "-i", str(audio), "-vf", vf,
                        "-af", "adelay=400|400,apad", "-t", f"{duration:.2f}", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(seg)], check=True)
        segments.append(seg)
        cues.append((t + 0.4, t + 0.4 + speech, scene["narration"]))
        manifest.append({"id": scene["id"], "start": round(t, 2), "seconds": round(duration, 2)})
        t += duration

    listing = work / "list.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in segments), encoding="utf-8")
    out = Path(args.out).resolve()
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    vtt = ["WEBVTT", ""] + [f"{vtt_time(a)} --> {vtt_time(b)}\n{txt}\n" for a, b, txt in cues]
    out.with_suffix(".vtt").write_text("\n".join(vtt), encoding="utf-8")
    out.with_suffix(".manifest.json").write_text(json.dumps(
        {"engine": engine, "voice": voice, "deck": deck.name, "seconds": round(t, 1), "scenes": manifest}, indent=2), encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"video": str(out), "seconds": round(t, 1), "voice": voice}))


if __name__ == "__main__":
    main()
