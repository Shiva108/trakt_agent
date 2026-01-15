#!/usr/bin/env -S venv/bin/python
"""
Fetch Data Module
Retrieves watch history and candidate data from Trakt API.
"""
import requests
import json
import time
from typing import Dict, List, Any, Optional

from config import (
    TRAKT_BASE_URL,
    TRAKT_API_DELAY,
    TOKEN_FILE,
    SECRETS_FILE,
    HISTORY_FILE,
    CANDIDATES_FILE,
    HISTORY_LIMIT,
    logger
)

def get_headers() -> Dict[str, str]:
    """
    Constructs Trakt API headers using stored credentials.
    Raises FileNotFoundError if sensitive files are missing.
    """
    if not TOKEN_FILE.exists():
        logger.error(f"Token file not found at {TOKEN_FILE}")
        raise FileNotFoundError(f"Missing {TOKEN_FILE}. Run 'exchange_pin.py' first.")
    
    if not SECRETS_FILE.exists():
        logger.error(f"Secrets file not found at {SECRETS_FILE}")
        raise FileNotFoundError(f"Missing {SECRETS_FILE}.")

    with open(TOKEN_FILE, "r") as f:
        token = json.load(f)
        
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token['access_token']}",
        "trakt-api-version": "2",
        "trakt-api-key": secrets["client_id"]
    }

def fetch_history(limit: int = HISTORY_LIMIT) -> List[Dict[str, Any]]:
    """
    Fetches the user's watch history from Trakt.
    
    Args:
        limit: Maximum number of history items to fetch.
        
    Returns:
        List of history item dictionaries.
    """
    logger.info(f"Fetching last {limit} watched items...")
    
    all_items: List[Dict[str, Any]] = []
    page = 1
    per_page = 100 
    headers = get_headers()
    
    while len(all_items) < limit:
        url = f"{TRAKT_BASE_URL}/sync/history?limit={per_page}&page={page}"
        logger.debug(f"Fetching history page {page}...")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error on page {page}: {e}")
            break
            
        if not data:
            break
            
        all_items.extend(data)
        page += 1
        time.sleep(TRAKT_API_DELAY)
        
    logger.info(f"Fetched {len(all_items)} total items.")
    return all_items[:limit]

def fetch_category(category: str, category_type: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Generic fetcher for trending/popular lists.
    
    Args:
        category: 'trending' or 'popular'
        category_type: 'movies' or 'shows'
        limit: items to fetch
    """
    url = f"{TRAKT_BASE_URL}/{category_type}/{category}?limit={limit}"
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {category} {category_type}: {e}")
        return []

def main() -> None:
    try:
        # 1. Fetch Deep History
        history = fetch_history(limit=HISTORY_LIMIT)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"Saved {len(history)} history items to {HISTORY_FILE.name}")
        
        # 2. Fetch Candidates
        logger.info("Fetching candidate pools...")
        trending_mv = fetch_category("trending", "movies", 100)
        trending_tv = fetch_category("trending", "shows", 100)
        popular_mv = fetch_category("popular", "movies", 100)
        popular_tv = fetch_category("popular", "shows", 100)
        
        # Merge and deduplicate
        candidates: Dict[int, Dict[str, Any]] = {}
        pool = trending_mv + trending_tv + popular_mv + popular_tv
        
        for item in pool:
            if "movie" in item:
                tid = item["movie"]["ids"]["trakt"]
                candidates[tid] = item
            elif "show" in item:
                tid = item["show"]["ids"]["trakt"]
                candidates[tid] = item
                
        final_candidates = list(candidates.values())
        
        with open(CANDIDATES_FILE, "w") as f:
            json.dump(final_candidates, f, indent=2)
        logger.info(f"Saved {len(final_candidates)} unique candidates to {CANDIDATES_FILE.name}")

    except Exception as e:
        logger.error(f"Detailed Error: {e}")
        # Re-raise to let the caller (CLI) handle exit code
        raise e

if __name__ == "__main__":
    main()
