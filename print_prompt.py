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
preferred_genres = []
title_blocklist = []
preferred_min_year = 0
if Path("preferences.json").exists():
    with open("preferences.json", "r") as f:
        prefs = json.load(f)
        exclusions = prefs.get("genre_exclusions", [])
        preferred_genres = prefs.get("preferred_genres", [])
        title_blocklist = prefs.get("title_blocklist", [])
        preferred_min_year = prefs.get("preferred_min_year", 0)

valid_candidates = recommend.filter_candidates(candidates_data, watched_ids, exclusions, title_blocklist, preferred_min_year)

with open(PROFILE_FILE, "r") as f:
    profile_data = json.load(f)

candidate_list_str = "\n".join([f"- {c}" for c in valid_candidates[:50]])
print("CANDIDATES:\n", candidate_list_str)
