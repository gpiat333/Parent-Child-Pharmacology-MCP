# Narrated demo video

`scenes.json` holds everything that changes: the narration for each scene, the text on each demo card, and which deck slide to show (by title, so reordering the deck doesn't break it). Card text comes from real outputs: model answers from the final evaluation chats (`evaluation/policy24-final/chats/ and policy25-final`) and fixed server replies.

To rebuild after editing `scenes.json`:

```
python build_demo.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v24.pptx" --out "demo.mp4"
```

Needs LibreOffice, macOS `say`, and the Python packages python-pptx, pypdfium2, Pillow, imageio-ffmpeg and edge-tts. The narration engine and voice are set in `scenes.json`: "edge" uses a Microsoft neural voice (en-US-AvaNeural) through the edge-tts package and sends only the narration text to Microsoft's speech service; "say" uses a macOS voice. Each build also writes captions (`.vtt`) and a manifest with scene timings.

## Demo slides for a self-narrated recording

`../Parent-child Pharmacology MCP — Demo slides.pptx` is a short deck for recording the demo in your own voice: sixteen slides from the main deck (background, architecture and all 31 tools) and the demo cards, a testing slide (GPT and Claude, safety probes, languages, automated tests, deployment), and a live-demo slide where the recording switches to the deployed Databricks App in the Databricks AI Playground. Each slide's speaker notes hold a voiceover script. Three answer cards after the closing slide are backups in case the live demo can't be recorded. To rebuild:

```
python build_demo_slides.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v24.pptx"
```

Needs python-pptx only. `cards.py` holds the card drawing shared with `build_demo.py`.
