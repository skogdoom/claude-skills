"""Tests import the built package, not the sources under src/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "build"))
