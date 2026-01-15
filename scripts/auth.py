 #!/usr/bin/env python3
"""
Trakt Device Authentication Module

Handles OAuth2 device flow authentication for Trakt API access.
Generates device codes and polls for access tokens.
"""
import json
import time
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import requests

# Configuration - use pathlib for paths
BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_FILE: Path = BASE_DIR / "secrets.json"
TOKEN_FILE: Path = BASE_DIR / "token.json"
BASE_URL: str = "https://api.trakt.tv"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_secrets() -> Dict[str, str]:
    """
    Load API credentials from secrets.json.
    
    Returns:
        Dictionary containing client_id and client_secret.
        
    Raises:
        FileNotFoundError: If secrets.json doesn't exist.
        ValueError: If credentials are placeholder values.
    """
    if not SECRETS_FILE.exists():
        logger.error(f"Secrets file not found: {SECRETS_FILE}")
        raise FileNotFoundError(f"Missing {SECRETS_FILE}. Create it with your client_id and client_secret.")
    
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        
    if "YOUR_CLIENT_ID_HERE" in secrets.values():
        logger.error("Placeholder credentials detected in secrets.json")
        raise ValueError(f"Please fill in your credentials in {SECRETS_FILE}")
        
    return secrets


def authenticate() -> Optional[Dict[str, Any]]:
    """
    Perform OAuth2 device flow authentication with Trakt.
    
    Displays a user code and verification URL, then polls for
    the access token until authorized or timeout.
    
    Returns:
        Token data dictionary if successful, None if failed/timeout.
    """
    secrets = load_secrets()
    client_id = secrets["client_id"]
    client_secret = secrets["client_secret"]
    
    # 1. Request Device Code
    logger.info("Initiating Device Authentication...")
    try:
        response = requests.post(f"{BASE_URL}/oauth/device/code", json={
            "client_id": client_id
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get device code: {e}")
        return None
        
    data = response.json()
    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_url = data["verification_url"]
    interval = data["interval"]
    expires_in = data["expires_in"]
    
    print("\n" + "="*50)
    print(f"PLEASE GO TO: {verification_url}")
    print(f"ENTER CODE:   {user_code}")
    print("="*50 + "\n")
    
    # 2. Poll for Access Token
    start_time = time.time()
    while (time.time() - start_time) < expires_in:
        print("Waiting for authorization...", end="\r")
        time.sleep(interval)
        
        try:
            token_response = requests.post(f"{BASE_URL}/oauth/device/token", json={
                "code": device_code,
                "client_id": client_id,
                "client_secret": client_secret
            })
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during polling: {e}")
            continue
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=2)
            logger.info(f"Authentication successful! Token saved to {TOKEN_FILE}")
            return token_data
        
        if token_response.status_code == 400:
            # Pending authorization - continue polling
            continue
        else:
            logger.error(f"Unexpected response: {token_response.status_code} - {token_response.text}")
            break
             
    logger.warning("Authentication timed out.")
    return None


if __name__ == "__main__":
    if TOKEN_FILE.exists():
        print(f"Already authenticated! ({TOKEN_FILE} exists)")
        choice = input("Re-authenticate? [y/N]: ")
        if choice.lower() != 'y':
            sys.exit(0)
            
    result = authenticate()
    sys.exit(0 if result else 1)

