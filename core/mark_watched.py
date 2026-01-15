#!/usr/bin/env -S venv/bin/python
import requests
import json
import time
from typing import Dict, List, Optional, Tuple, Any

from config import (
    TRAKT_BASE_URL,
    TOKEN_FILE,
    SECRETS_FILE,
    logger
)

def get_headers() -> Dict[str, str]:
    """Constructs Trakt API headers."""
    if not TOKEN_FILE.exists() or not SECRETS_FILE.exists():
        logger.error("Missing auth files.")
        raise FileNotFoundError("Run exchange_pin.py first.")

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

def search_id(title_input: str, type_hint: Optional[str] = None) -> Tuple[Optional[int], Optional[str]]:
    """
    Search for a movie or show by title.
    Supports 'type:Title' syntax (e.g. 'show:Stranger Things').
    Supports 'Title (Year)' syntax to filter by year.
    Returns (trakt_id, type) or (None, None).
    """
    # Parse prefixes
    if title_input.lower().startswith("movie:"):
        type_hint = "movie"
        title_input = title_input[6:]
    elif title_input.lower().startswith("show:"):
        type_hint = "show"
        title_input = title_input[5:]
        
    # Parse year
    import re
    year_match = re.search(r'\((\d{4})\)$', title_input.strip())
    target_year = None
    clean_title = title_input
    
    if year_match:
        target_year = int(year_match.group(1))
        clean_title = title_input[:year_match.start()].strip()
        
    logger.info(f"Searching for '{clean_title}'" + (f" (Year: {target_year})" if target_year else "") + (f" [Type: {type_hint}]" if type_hint else "") + "...")
    
    types = [type_hint] if type_hint else ["movie", "show"]
    headers = get_headers()
    
    for t in types:
        # Trakt search works best with just the title
        url = f"{TRAKT_BASE_URL}/search/{t}?query={requests.utils.quote(clean_title)}"
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    # If year is specified, look for a match
                    match = None
                    if target_year:
                        for r in results:
                            item = r[t]
                            if item.get('year') == target_year:
                                match = item
                                break
                    
                    # Fallback to first if no year matched or no year specified
                    if not match and results:
                         # If we had a year but didn't find it, we might want to be careful.
                         # But users might have slightly wrong years.
                         # For now, if year specified but not found, let's skip to next type 
                         # UNLESS we are restricted by type_hint.
                         if target_year and not type_hint:
                             continue 
                         match = results[0][t]

                    if match:
                        logger.info(f"Found: {match['title']} ({match.get('year')}) [ID: {match['ids']['trakt']}]")
                        return match['ids']['trakt'], t
        except requests.exceptions.RequestException as e:
            logger.error(f"Search failed for {title_input}: {e}")
            
    logger.warning(f"'{title_input}' not found.")
    return None, None

def mark_watched_ids(movies: List[int], shows: List[int]) -> None:
    """Marks the given lists of Trakt IDs as watched."""
    if not movies and not shows:
        return
        
    url = f"{TRAKT_BASE_URL}/sync/history"
    payload = {
        "movies": [{"ids": {"trakt": mid}} for mid in movies],
        "shows": [{"ids": {"trakt": sid}} for sid in shows]
    }
    
    logger.info(f"Marking {len(movies)} movies and {len(shows)} shows as watched...")
    
    try:
        response = requests.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        
        data = response.json()
        added = data.get("added", {})
        logger.info(f"Success! Added: {added.get('movies', 0)} movies, {added.get('episodes', 0)} episodes.")
        
        # Wait for sync
        logger.info("Waiting 2s for Trakt sync...")
        time.sleep(2)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to mark watched: {e}")

def process_titles(titles: List[str]) -> None:
    """
    Main logic: Resolve titles to IDs and mark them.
    """
    movies_to_mark = []
    shows_to_mark = []
    
    for title in titles:
        tid, type_found = search_id(title)
        if tid:
            if type_found == "movie":
                movies_to_mark.append(tid)
            else:
                shows_to_mark.append(tid)
                
    mark_watched_ids(movies_to_mark, shows_to_mark)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mark_watched.py 'Title 1' 'Title 2'")
        sys.exit(1)
    process_titles(sys.argv[1:])
