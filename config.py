"""
Trakt Agent Configuration
Centralized configuration for all scripts
"""
import logging
import sys
from pathlib import Path
from typing import Final, Dict, List, Union

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("trakt_agent")

import os

# ==============================================================================
# LOCAL LLM CONFIGURATION
# ==============================================================================
API_BASE_URL: Final[str] = "http://127.0.0.1:1234/v1"  # Your local LLM server endpoint
MODEL_NAME: Final[str] = "qwen/qwen3-4b-2507"  # Model identifier
API_KEY: Final[str] = os.getenv("LOCAL_LLM_API_KEY", "not-needed")  # Local servers typically don't require authentication
TEMPERATURE: Final[float] = 0.7  # Creativity level (0.1=focused, 0.9=creative)

# ==============================================================================
# TRAKT API CONFIGURATION
# ==============================================================================
TRAKT_BASE_URL: Final[str] = "https://api.trakt.tv"

# ==============================================================================
# SERVICE CONFIGURATION
# ==============================================================================
# Options: "trakt", "simkl"
SERVICE_PROVIDER: Final[str] = "trakt"

# ==============================================================================
# FILE PATHS (using pathlib)
# ==============================================================================
BASE_DIR: Final[Path] = Path(__file__).resolve().parent

DATA_DIR: Final[Path] = BASE_DIR / "data"

if SERVICE_PROVIDER == "simkl":
    HISTORY_FILE: Final[Path] = DATA_DIR / "watch_history_simkl.json"
    CANDIDATES_FILE: Final[Path] = DATA_DIR / "candidates_simkl.json"
else:
    HISTORY_FILE: Final[Path] = DATA_DIR / "watch_history.json"
    CANDIDATES_FILE: Final[Path] = DATA_DIR / "candidates.json"

OUTPUT_DIR: Final[Path] = BASE_DIR / "output"
PROFILE_FILE: Final[Path] = OUTPUT_DIR / "Trakt Taste Profile.md"
RECOMMENDATIONS_FILE: Final[Path] = OUTPUT_DIR / "Trakt Recommendations.md"

PREFERENCES_FILE: Final[Path] = BASE_DIR / "preferences.json"
TOKEN_FILE: Final[Path] = BASE_DIR / "token.json"
SECRETS_FILE: Final[Path] = BASE_DIR / "secrets.json"

# Ensure data and output directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# PROCESSING LIMITS
# ==============================================================================
HISTORY_LIMIT: Final[int] = 500  # Number of watch history items to fetch
PROFILE_ANALYSIS_LIMIT: Final[int] = 75  # Reduced from 100 for 4k context overlap optimization
CANDIDATE_LIMIT: Final[int] = 60  # Reduced from 100 for 4k context safety
NUM_RECOMMENDATIONS: Final[int] = 10  # Number of recommendations to generate

# ==============================================================================
# RATE LIMITING
# ==============================================================================
TRAKT_API_DELAY: Final[float] = 0.1  # Seconds between API calls

# ==============================================================================
# SIMKL API CONFIGURATION
# ==============================================================================
SIMKL_BASE_URL: Final[str] = "https://api.simkl.com"
SIMKL_TOKEN_FILE: Final[Path] = BASE_DIR / "simkl_token.json"

# ==============================================================================
# SERVICE CONFIGURATION
# ==============================================================================
# Options: "trakt", "simkl"
SERVICE_PROVIDER: Final[str] = "trakt"
