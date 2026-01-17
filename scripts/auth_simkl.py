#!/usr/bin/env python3
"""
Simkl Authentication Module

Handles OAuth2 authentication for Simkl API access.
Directs user to authorization URL and exchanges code for access token.
"""
import json
import sys
import logging
import webbrowser
from typing import Dict, Any, Optional
import requests

from config import (
    SIMKL_BASE_URL,
    SIMKL_TOKEN_FILE,
    SECRETS_FILE,
    logger
)

def load_simkl_secrets() -> Dict[str, str]:
    """
    Load Simkl API credentials from secrets.json.
    
    Returns:
        Dictionary containing simkl_client_id and simkl_client_secret.
    """
    if not SECRETS_FILE.exists():
        logger.error(f"Secrets file not found: {SECRETS_FILE}")
        raise FileNotFoundError(f"Missing {SECRETS_FILE}.")
    
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        
    if "simkl_client_id" not in secrets or "simkl_client_secret" not in secrets:
        logger.error("Simkl credentials missing in secrets.json")
        raise ValueError("Please add 'simkl_client_id' and 'simkl_client_secret' to secrets.json")
        
    return secrets

def authenticate() -> Optional[Dict[str, Any]]:
    """
    Perform OAuth2 authentication with Simkl.
    """
    try:
        secrets = load_simkl_secrets()
    except Exception as e:
        print(f"Error: {e}")
        return None

    client_id = secrets["simkl_client_id"]
    client_secret = secrets["simkl_client_secret"]
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    
    auth_url = (
        f"https://simkl.com/oauth/authorize?"
        f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )
    
    print("\n" + "="*60)
    print("SIMKL AUTHENTICATION REQUIRED")
    print("="*60)
    print(f"1. Visit this URL: {auth_url}")
    print("2. Authorize the application.")
    print("3. Copy the code provided.")
    print("="*60 + "\n")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
    except:
        pass
        
    code = input("Enter the code here: ").strip()
    
    if not code:
        logger.warning("No code entered.")
        return None
        
    logger.info("Exchanging code for access token...")
    
    try:
        response = requests.post(f"{SIMKL_BASE_URL}/oauth/token", json={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        })
        response.raise_for_status()
        
        token_data = response.json()
        
        with open(SIMKL_TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
            
        logger.info(f"Authentication successful! Token saved to {SIMKL_TOKEN_FILE}")
        return token_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Authentication failed: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    authenticate()
