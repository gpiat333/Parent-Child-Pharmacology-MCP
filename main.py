import sys
from pathlib import Path

# Databricks stages source without installing the project wheel. Resolve only the
# src directory beside this trusted entry point; never use a request-supplied path.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from parent_child_pharmacology.app import main

if __name__ == "__main__":
    main()
