#!/usr/bin/env python3
"""
Mark Watched Module (Simkl)
Searches for items and marks them as watched on Simkl.
"""
import requests
import json
import urllib.parse
from typing import List, Dict, Any, Optional

from config import (
    SIMKL_BASE_URL,
    logger
)
from core.fetch_data_simkl import get_headers

def search_item(title: str) -> Optional[Dict[str, Any]]:
    """
    Search for a movie or show by title on Simkl.
    Returns the best match (first result) with an ID.
    """
    headers = get_headers()
    encoded_title = urllib.parse.quote(title)
    
    # Try Movie Search
    url_movie = f"{SIMKL_BASE_URL}/search/movie?q={encoded_title}&limit=1"
    try:
        resp = requests.get(url_movie, headers=headers)
        if resp.status_code == 200 and resp.json():
            item = resp.json()[0]
            return {"type": "movie", "title": item["title"], "year": item["year"], "ids": item["ids"]}
    except Exception as e:
        logger.warning(f"Search error (movie): {e}")

    # Try TV Search
    url_tv = f"{SIMKL_BASE_URL}/search/tv?q={encoded_title}&limit=1"
    try:
        resp = requests.get(url_tv, headers=headers)
        if resp.status_code == 200 and resp.json():
            item = resp.json()[0]
            return {"type": "show", "title": item["title"], "year": item["year"], "ids": item["ids"]}
    except Exception as e:
        logger.warning(f"Search error (tv): {e}")
        
    return None

def mark_as_watched(item: Dict[str, Any]) -> bool:
    """
    Marks the given item as watched on Simkl.
    """
    headers = get_headers()
    if "Authorization" not in headers:
        logger.error("Authentication required to mark items as watched.")
        return False
        
    url = f"{SIMKL_BASE_URL}/sync/history"
    
    payload = {}
    
    if item["type"] == "movie":
        payload["movies"] = [{"ids": item["ids"]}]
    elif item["type"] == "show":
        # For shows, we might want to mark all episodes or specific ones. 
        # Simkl /sync/history allows marking a show as watched (completed).
        payload["shows"] = [{"ids": item["ids"]}]
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        res_data = resp.json()
        # Simkl returns added count
        if (res_data.get("added", {}).get("movies", 0) > 0 or 
            res_data.get("added", {}).get("shows", 0) > 0 or
            res_data.get("added", {}).get("episodes", 0) > 0):
            return True
        logger.info(f"Response: {res_data}")
        return False # Nothing added (maybe already watched)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to mark as watched: {e}")
        return False

def process_titles(titles: List[str]) -> None:
    """
    Process a list of titles: search and mark as watched.
    """
    logger.info(f"Processing {len(titles)} items for Simkl...")
    
    for title in titles:
        # Check if it has a year
        # Basic logic, can be improved
        logger.info(f"Searching for: {title}")
        match = search_item(title)
        
        if match:
            logger.info(f"Found: {match['title']} ({match['year']}) [{match['type']}]")
            success = mark_as_watched(match)
            if success:
                logger.info(f"Successfully marked '{match['title']}' as watched.")
            else:
                logger.warning(f"Could not mark '{match['title']}' as watched (might be already watched).")
        else:
            logger.error(f"Could not find match for: {title}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_titles(sys.argv[1:])
    else:
        print("Usage: python mark_watched_simkl.py 'Movie Title' ...")
