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
import time
from pathlib import Path

import imageio_ffmpeg
import pypdfium2
from cards import chat_card, grid_card
from pptx import Presentation
from pptx.util import Inches

HERE = Path(__file__).resolve().parent
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


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
            for attempt in range(4):  # the speech service occasionally drops a request
                done = subprocess.run([edge, "--voice", voice, f"--rate={spec.get('rate', '+0%')}",
                                       "--text", scene["narration"], "--write-media", str(audio)],
                                      capture_output=True)
                if done.returncode == 0:
                    break
                time.sleep(3 * (attempt + 1))
            else:
                raise RuntimeError(done.stderr.decode(errors="replace")[-500:])
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
