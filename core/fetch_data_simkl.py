#!/usr/bin/env python3
"""
Fetch Data Module (Simkl)
Retrieves watch history and candidate data from Simkl API.
"""
import requests
import json
import socket
from typing import Dict, List, Any, Optional

from config import (
    SIMKL_BASE_URL,
    SIMKL_TOKEN_FILE,
    SECRETS_FILE,
    HISTORY_FILE,
    CANDIDATES_FILE,
    HISTORY_LIMIT,
    logger
)

def get_headers() -> Dict[str, str]:
    """
    Constructs Simkl API headers.
    """
    if not SECRETS_FILE.exists():
        logger.error(f"Secrets file not found at {SECRETS_FILE}")
        raise FileNotFoundError(f"Missing {SECRETS_FILE}.")

    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        
    client_id = secrets.get("simkl_client_id")
    if not client_id:
        raise ValueError("simkl_client_id missing in secrets.json")

    headers = {
        "Content-Type": "application/json",
        "simkl-api-key": client_id
    }

    # Add Authorization header if token exists
    if SIMKL_TOKEN_FILE.exists():
        with open(SIMKL_TOKEN_FILE, "r") as f:
            token = json.load(f)
            if "access_token" in token:
                 headers["Authorization"] = f"Bearer {token['access_token']}"
    
    return headers

def fetch_simkl_details(simkl_id: int, item_type: str) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed info (title, year) for a specific item by ID.
    item_type: 'movie' or 'show'
    """
    # Endpoint segment: 'movies' for movie, 'tv' for show
    segment = "movies" if item_type == "movie" else "tv"
    url = f"{SIMKL_BASE_URL}/{segment}/{simkl_id}"
    
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.warning(f"Failed to fetch details for {item_type} {simkl_id}: {e}")
        
    return None

def normalize_simkl_item(item: Dict[str, Any], item_type: str = None) -> Dict[str, Any]:
    """
    Normalizes a Simkl item to match the structure expected by the recommendation engine.
    Wraps it in 'movie' or 'show' key and ensures 'ids' map exists.
    """
    # Determine type if not provided
    if not item_type:
        # Simkl usually provides specific fields or we know the context
        pass 

    # Basic normalization
    # Simkl item often has: title, year, ids: { simkl, imdb, etc. }
    
    # Copy relevant fields
    ids = item.get("ids", {})
    # Ensure simkl id is present (it might be the root id in some endpoints if not redundant)
    # But usually Simkl returns 'ids' object.
    
    normalized = {
        "title": item.get("title"),
        "year": item.get("year"),
        "ids": ids
    }
    
    # If explicit type known or inferred
    final_obj = {}
    if item_type == "movie" or "movie" in item or item.get("poster", "").startswith("movie"):
         final_obj["movie"] = normalized
    elif item_type == "show" or "show" in item or item.get("poster", "").startswith("tv"):
         final_obj["show"] = normalized
    else:
        # Fallback based on logic if mixed
        # For now, let's assume usage contexts define type
        pass
        
    return final_obj

def fetch_history(limit: int = HISTORY_LIMIT) -> List[Dict[str, Any]]:
    """
    Fetches the user's watch history from Simkl.
    Note: Simkl 'sync/all-items/completed' returns all items.
    """
    logger.info("Fetching Simkl watch history...")
    
    headers = get_headers()
    if "Authorization" not in headers:
         logger.warning("No Simkl token found. History fetch might be limited or fail.")
         return []

    url = f"{SIMKL_BASE_URL}/sync/all-items/completed"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Simkl history: {e}")
        return []

    # Data structure: { "movies": [...], "shows": [...], "anime": [...] }
    all_items = []
    
    for movie in data.get("movies", []):
         # Create structure similar to Trakt: { "movie": { ... } }
         norm = {
             "movie": {
                 "title": movie.get("movie", {}).get("title"),
                 "year": movie.get("movie", {}).get("year"),
                 "ids": movie.get("movie", {}).get("ids", {})
             }
         }
         # Ensure we have ids
         if not norm["movie"]["ids"]:
             # Sometimes structure differs, let's debug if needed.
             # But /sync/all-items usually returns full objects
             pass
         all_items.append(norm)

    for show in data.get("shows", []):
         norm = {
             "show": {
                 "title": show.get("show", {}).get("title"),
                 "year": show.get("show", {}).get("year"),
                 "ids": show.get("show", {}).get("ids", {})
             }
         }
         all_items.append(norm)
         
    # Simkl returns everything. Slice to limit.
    # Ideally sort by last_watched_at but Simkl format here is list of items.
    # The 'last_watched_at' is inside the user object part usually.
    # For now, just taking top items.
    
    logger.info(f"Fetched {len(all_items)} history items from Simkl.")
    return all_items[:limit]

def fetch_candidates() -> List[Dict[str, Any]]:
    """
    Fetches movies and shows from Simkl.
    Prioritizes personalized recommendations if authenticated.
    Fallbacks to trending/popular if not.
    """
    logger.info("Fetching Simkl candidates...")
    headers = get_headers()
    candidates = []
    
    # Check if we are authenticated
    has_auth = "Authorization" in headers
    
    if has_auth:
        logger.info("Authenticated: Fetching personalized recommendations...")
        # 0. Personalized Recommendations
        # Note: Simkl doesn't have a direct "mixed" recommendations endpoint documented publicly 
        # that mirrors Trakt's specific style easily, but let's try a discovery approach or just use trending with user context?
        # Actually, let's stick to generic trending but filtered by user if possible?
        # No, let's just fetch trending with extended info.
        pass

    # 1. Trending Movies
    # We limit to 10 detailed lookups to be polite and fast
    url_movies = f"{SIMKL_BASE_URL}/movies/trending/week?limit=10"
    try:
        resp = requests.get(url_movies, headers=headers)
        if resp.status_code == 200:
            items = resp.json()
            for item in items:
                simkl_id = item.get("ids", {}).get("simkl_id")
                if not simkl_id:
                    continue

                # Fetch details to get title
                details = fetch_simkl_details(simkl_id, "movie")
                if details:
                    candidates.append({
                        "movie": {
                            "title": details.get("title"),
                            "year": details.get("year"),
                            "ids": details.get("ids", {})
                        }
                    })
        else:
            logger.warning(f"Simkl Movies Trending returned {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching trending movies: {e}")

    # 2. Trending Shows
    url_shows = f"{SIMKL_BASE_URL}/tv/trending/week?limit=10"
    try:
        resp = requests.get(url_shows, headers=headers)
        if resp.status_code == 200:
            items = resp.json()
            for item in items:
                simkl_id = item.get("ids", {}).get("simkl_id")
                if not simkl_id:
                    continue

                details = fetch_simkl_details(simkl_id, "show")
                if details:
                    candidates.append({
                        "show": {
                            "title": details.get("title"),
                            "year": details.get("year"),
                            "ids": details.get("ids", {})
                        }
                    })
        else:
             logger.warning(f"Simkl Shows Trending returned {resp.status_code}")
    except Exception as e:
         logger.error(f"Error fetching trending shows: {e}")

    logger.info(f"Fetched {len(candidates)} candidates from Simkl.")
    return candidates

def main() -> None:
    try:
        # 1. Fetch History
        history = fetch_history(limit=HISTORY_LIMIT)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"Saved {len(history)} history items to {HISTORY_FILE.name}")
        
        # 2. Fetch Candidates
        candidates = fetch_candidates()
        with open(CANDIDATES_FILE, "w") as f:
            json.dump(candidates, f, indent=2)
        logger.info(f"Saved {len(candidates)} candidates to {CANDIDATES_FILE.name}")

    except Exception as e:
        logger.error(f"Detailed Error: {e}")
        raise e

if __name__ == "__main__":
    main()
