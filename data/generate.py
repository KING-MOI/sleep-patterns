"""Regenerate the synthetic CSVs in this folder.

    python data/generate.py --seed 7
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sleep_patterns.synthetic import main  # noqa: E402

if __name__ == "__main__":
    main(["--out", str(Path(__file__).resolve().parent), *sys.argv[1:]])
