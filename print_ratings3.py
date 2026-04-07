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
if Path("preferences.json").exists():
    with open("preferences.json", "r") as f:
        prefs = json.load(f)
        exclusions = prefs.get("genre_exclusions", [])

valid_candidates = recommend.filter_candidates(candidates_data, watched_ids, exclusions, [], 2005)
ratings_map = recommend.build_ratings_map(candidates_data)

already_picked = [
    "Avatar (2009)", "Mercy (2026)", "Greenland 2: Migration (2026)", "Ballerina (2025)", "Trap House (2025)",
    "Nobody 2 (2025)", "Sisu: Road to Revenge (2025)", "The Secret Agent (2025)", "Dead of Winter (2025)", "The Life of Chuck (2025)",
    "The Pitt (2025)", "Landman (2024)", "Zootopia (2016)", "F1 (2025)", "The Housemaid (2025)", "Chicago P.D. (2014)",
    "Chicago Fire (2012)", "The Traitors (2022)", "9-1-1 (2018)", "Sentimental Value (2025)", "Rental Family (2025)", 
    "Abbott Elementary (2021)", "The Big Bang Theory (2007)", "Grey's Anatomy (2005)", "Zootopia 2 (2025)"
]

out = []
for title in valid_candidates:
    if title not in already_picked:
        rating = ratings_map.get(title, 0.0)
        # find item genres
        genres = []
        for c in candidates_data:
            if recommend.get_title_year(c) == title:
                genres = recommend.get_genres(c)
                break
        out.append(f"{title} - Score: {rating} - Genres: {genres}")

print("\n".join(out[:50]))
