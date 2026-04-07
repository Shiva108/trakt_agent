import json

with open("data/candidates.json", "r") as f:
    candidates = json.load(f)

with open("preferences.json", "r") as f:
    prefs = json.load(f)

exclusions = [e.lower() for e in prefs.get("genre_exclusions", [])]

already_recommended = [
    "Avatar", "Mercy", "Greenland 2: Migration", "Nobody 2", "Ballerina",
    "Sisu: Road to Revenge", "The Secret Agent", "Trap House", "Dead of Winter",
    "The Life of Chuck", "Chicago P.D.", "Chicago Fire", "The Traitors", "9-1-1",
    "Sentimental Value", "Rental Family", "Abbott Elementary", "The Big Bang Theory",
    "Grey's Anatomy", "Zootopia 2", "Severance", "Breaking Bad", "Dexter",
    "Better Call Saul", "Slow Horses", "Tehran", "Mayor of Kingstown",
    "Sentenced to Be a Hero", "Fire Force", "Tell Me Lies", "Landman", "Zootopia",
    "F1", "The Housemaid"
]
already_rec_lower = [a.lower() for a in already_recommended]

fresh = []
for c in candidates:
    if "movie" in c:
        title = c["movie"]["title"]
        year = c["movie"].get("year", 0)
        genres = c["movie"].get("genres", [])
        rating = c["movie"].get("rating", 0)
        votes = c["movie"].get("votes", 0)
    elif "show" in c:
        title = c["show"]["title"]
        year = c["show"].get("year", 0)
        genres = c["show"].get("genres", [])
        rating = c["show"].get("rating", 0)
        votes = c["show"].get("votes", 0)
    else:
        continue
        
    if year and year < 2005:
        continue
        
    if any(ex.lower() in [g.lower() for g in genres] for ex in exclusions):
        continue
        
    if any(ar in title.lower() for ar in already_rec_lower):
        continue
        
    fresh.append((title, year, rating, votes, genres))

# Sort by rating (descending), but prioritize things with enough votes to be good but maybe not too mainstream
fresh.sort(key=lambda x: (x[2]), reverse=True)

for i, (t, y, r, v, g) in enumerate(fresh[:20]):
    print(f"{t} ({y}) - Rating: {round(r,1)}, Votes: {v}, Genres: {g}")
