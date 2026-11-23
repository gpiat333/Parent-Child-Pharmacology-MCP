# Narrated demo video

`scenes.json` holds everything that changes: the narration for each scene, the text on each demo card, and which deck slide to show (by title, so reordering the deck doesn't break it). Card text comes from real outputs: model answers from the final evaluation chats (`evaluation/policy24-final/chats/`) and fixed server replies.

To rebuild after editing `scenes.json`:

```
python build_demo.py --deck "../Parent-child Pharmacology MCP — Hackathon deck v19.pptx" --out "demo.mp4"
```

Needs LibreOffice, macOS `say`, and the Python packages python-pptx, pypdfium2, Pillow and imageio-ffmpeg. The narration engine and voice are set in `scenes.json`: "edge" uses a Microsoft neural voice (en-US-AvaNeural) through the edge-tts package and sends only the narration text to Microsoft's speech service; "say" uses a macOS voice. Each build also writes captions and a manifest. Each build also writes captions (`.vtt`) and a manifest with scene timings.
