"""Compatibility launcher. Prefer uv run parent-child-mcp at repository root."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from parent_child_pharmacology.app import main

if __name__ == "__main__":
    main()
