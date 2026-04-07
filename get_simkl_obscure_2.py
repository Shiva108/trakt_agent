import json

try:
    with open("data/candidates_simkl.json", "r") as f:
        candidates = json.load(f)
except:
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
    "F1", "The Housemaid", "Jujutsu Kaisen", "Game of Thrones", "Frieren",
    "Interstellar", "Fallout", "Demon Slayer", "Avengers", "Top Gun",
    "Marty Supreme", "Breaking Bad", "Stranger Things", "Pluribus", "A Knight of the Seven Kingdoms",
    "The Night Manager", "How to Train Your Dragon", "All Her Fault", "Steal", "Run Away", "HIS & HERS",
    "Agatha Christie's Seven Dials", "No Other Choice", "Project Hail Mary", "Dune", "Inception",
    "Deadpool", "Guardians of the Galaxy", "Spider-Man", "Sinners", "Crime 101", "Iron Man", "War Machine",
    "The Super Mario Bros. Movie", "Wuthering Heights"
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

# Use Trakt data for better genre/rating accuracy
with open("data/candidates.json", "r") as f:
    trakt_cand = json.load(f)

for c in trakt_cand:
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

# Sort by rating to get best quality hidden gems.
obscure = [x for x in fresh if x[3] < 20000 and x[2] >= 7.0]
obscure.sort(key=lambda x: (x[2], -x[3]), reverse=True)

final_list = []
seen_titles = set()
for t, y, r, v, g in obscure:
    if t not in seen_titles:
        final_list.append((t, y, r, v, g))
        seen_titles.add(t)

for i, (t, y, r, v, g) in enumerate(final_list[:20]):
    print(f"{t} ({y}) - Rating: {round(r,1)}, Votes: {v}, Genres: {g}")
