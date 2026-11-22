"""Rebuild current reports from saved evidence; no model or test execution."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / 'evidence-revision' / 'report.py'), run_name='__main__')
