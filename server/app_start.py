"""Compatibility launcher; the current deployment kit uses the repository root."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("server.py")), run_name="__main__")
