# Core functionality modules
import sys
from pathlib import Path

# Add parent directory to path for config imports
_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

from . import fetch_data
from . import profile_taste
from . import recommend
from . import mark_watched
from . import search_and_mark
