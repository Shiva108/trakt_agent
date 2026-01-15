#!/usr/bin/env -S venv/bin/python
"""
DEPRECATED: This module is superseded by core/mark_watched.py
Use `cli.py mark "Title"` instead.

This file is kept for backward compatibility but will be removed in a future version.
"""
import warnings
warnings.warn(
    "search_and_mark.py is deprecated. Use 'cli.py mark' instead.",
    DeprecationWarning,
    stacklevel=2
)

import requests
import json
import os
import sys
import time

# Configuration
TOKEN_FILE = "token.json"
SECRETS_FILE = "secrets.json"
BASE_URL = "https://api.trakt.tv"

def get_headers():
    if not os.path.exists(TOKEN_FILE):
        print("Error: Not authenticated.")
        sys.exit(1)
    
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

def search_id(title, type_hint=None):
    print(f"Searching for '{title}'...", end=" ")
    # Search both if type not certain
    types = [type_hint] if type_hint else ["movie", "show"]
    
    for t in types:
        url = f"{BASE_URL}/search/{t}?query={requests.utils.quote(title)}"
        resp = requests.get(url, headers=get_headers())
        if resp.status_code == 200:
            results = resp.json()
            if results:
                # Top match
                match = results[0][t]
                print(f"Found: {match['title']} ({match['year']}) ID: {match['ids']['trakt']}")
                return match['ids']['trakt'], t
                
    print("Not found.")
    return None, None

def mark_watched_ids(movies, shows):
    url = f"{BASE_URL}/sync/history"
    payload = {
        "movies": [{"ids": {"trakt": mid}} for mid in movies],
        "shows": [{"ids": {"trakt": sid}} for sid in shows]
    }
    
    if not movies and not shows:
        return
        
    print(f"Marking {len(movies)} movies and {len(shows)} shows as watched...")
    response = requests.post(url, headers=get_headers(), json=payload)
    
    if response.status_code in [200, 201]:
        data = response.json()
        added = data.get("added", {})
        print(f"Success! Added: {added.get('movies', 0)} movies, {added.get('episodes', 0)} episodes.")
        print(f"⏳ Waiting 5 seconds for Trakt API to sync...")
        time.sleep(5)
        print(f"✅ Sync complete! You can now fetch fresh data.")
    else:
        print(f"Error: {response.text}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_and_mark.py 'Title 1' 'Title 2' ...")
        sys.exit(1)
        
    titles = sys.argv[1:]
    
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
    try:
        main()
    except FileNotFoundError as e:
        print(f"\n❌ Error: Required file not found: {e}")
        print("Ensure token.json and secrets.json exist. Run 'exchange_pin.py' first.")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error connecting to Trakt API: {e}")
        print("Check your internet connection and Trakt API status.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error marking items as watched: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Verify authentication: token.json and secrets.json")
        print(f"2. Check internet connection")
        print(f"3. Verify item titles are correct")
        exit(1)
