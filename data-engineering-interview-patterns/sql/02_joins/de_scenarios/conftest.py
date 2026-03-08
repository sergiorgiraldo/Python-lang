import sys
from pathlib import Path

# Add sql/ to path so imports from sql/conftest.py work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
