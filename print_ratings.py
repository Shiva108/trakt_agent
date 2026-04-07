import json
from core import recommend
from config import CANDIDATES_FILE, HISTORY_FILE, PROFILE_FILE
from pathlib import Path

history = recommend.load_json(HISTORY_FILE)
candidates_data = recommend.load_json(CANDIDATES_FILE)

watched_ids = set()
for item in history:
    tid = recommend.get_item_id(item)
    if tid:
        watched_ids.add(tid)

exclusions = []
title_blocklist = []
preferred_min_year = 0
if Path("preferences.json").exists():
    with open("preferences.json", "r") as f:
        prefs = json.load(f)
        exclusions = prefs.get("genre_exclusions", [])
        title_blocklist = prefs.get("title_blocklist", [])
        preferred_min_year = prefs.get("preferred_min_year", 0)

valid_candidates = recommend.filter_candidates(candidates_data, watched_ids, exclusions, title_blocklist, preferred_min_year)
ratings_map = recommend.build_ratings_map(candidates_data)

already_picked = ["Avatar (2009)", "Mercy (2026)", "Greenland 2: Migration (2026)", "Ballerina (2025)", "Trap House (2025)", "Nobody 2 (2025)", "Sisu: Road to Revenge (2025)", "The Secret Agent (2025)", "Dead of Winter (2025)", "The Life of Chuck (2025)"]

out = []
for title in valid_candidates:
    if title not in already_picked:
        rating = ratings_map.get(title, 0.0)
        # Just show rating if it exists
        out.append(f"{title} - Score: {rating}")

print("\n".join(out[:30]))
