"""Add problems directory to path for direct imports in tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
