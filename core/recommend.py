#!/usr/bin/env -S venv/bin/python
import json
from typing import List, Set, Dict, Any, Optional

from pathlib import Path

from config import (
    API_BASE_URL, MODEL_NAME, API_KEY, TEMPERATURE,
    HISTORY_FILE, CANDIDATES_FILE, PROFILE_FILE, RECOMMENDATIONS_FILE,
    CANDIDATE_LIMIT, NUM_RECOMMENDATIONS, logger
)

def load_json(path: Path) -> List[Dict[str, Any]]:
    """Safe JSON loader that returns empty list on failure."""
    if not path.exists():
        logger.warning(f"File not found: {path}")
        return []
    with open(path, "r") as f:
        return json.load(f)

def get_item_id(item: Dict[str, Any]) -> Optional[str]:
    """Extracts a unique ID (Trakt, Simkl, or IMDB) from a movie or show object."""
    ids = {}
    if "movie" in item:
        ids = item["movie"]["ids"]
    elif "show" in item:
        ids = item["show"]["ids"]
    else:
        return None
        
    # Priority: Trakt > Simkl > IMDB
    if "trakt" in ids:
        return str(ids["trakt"])
    if "simkl" in ids:
        return str(ids["simkl"])
    if "imdb" in ids:
        return str(ids["imdb"])
    
    # Fallback to any key
    if ids:
        return str(list(ids.values())[0])
        
    return None

def get_title_year(item: Dict[str, Any]) -> str:
    """Extensions title (year) string from item."""
    title = "Unknown"
    year = ""
    
    if "movie" in item:
        title = item["movie"]["title"]
        year = item["movie"].get("year", "")
    elif "show" in item:
        title = item["show"]["title"]
        year = item["show"].get("year", "")
        
    return f"{title} ({year})" if year else title

def get_year(item: Dict[str, Any]) -> int:
    """Extracts year as integer from item."""
    try:
        if "movie" in item:
            return int(item["movie"]["year"])
        if "show" in item:
            return int(item["show"]["year"])
    except (ValueError, TypeError, KeyError):
        return 0
    return 0

def get_genres(item: Dict[str, Any]) -> List[str]:
    """Extracts genres from a movie or show object."""
    if "movie" in item:
        return item["movie"].get("genres", [])
    if "show" in item:
        return item["show"].get("genres", [])
    return []

def filter_candidates(candidates: List[Dict[str, Any]], watched_ids: Set[int], genre_exclusions: List[str] = [], title_blocklist: List[str] = [], min_year: int = 0) -> List[str]:
    """Filters candidates by watched status, excluded genres, blocked titles, and minimum year."""
    valid_candidates = []
    filtered_watched = 0
    filtered_genre = 0
    filtered_title = 0
    filtered_year = 0
    
    # Normalize exclusions to lowercase for matching
    excluded_genres_lower = [g.lower() for g in genre_exclusions]
    blocked_titles_lower = [t.lower() for t in title_blocklist]
    
    for item in candidates:
        tid = get_item_id(item)
        desc = get_title_year(item)
        genres = get_genres(item)
        genres_lower = [g.lower() for g in genres]
        
        # Extract just the title for blocklist matching
        title_only = desc.split(" (")[0].lower() if " (" in desc else desc.lower()
        
        # Skip watched items
        if tid and tid in watched_ids:
            filtered_watched += 1
            continue
        
        # Skip items with excluded genres
        if any(excl in genres_lower for excl in excluded_genres_lower):
            filtered_genre += 1
            if filtered_genre <= 5:
                logger.debug(f"Filtered (genre): {desc} - {genres}")
            continue
        
        # Skip blocked titles
        if title_only in blocked_titles_lower:
            filtered_title += 1
            logger.debug(f"Filtered (blocklist): {desc}")
            continue
        
        # Skip items older than min_year
        if min_year > 0:
            year = get_year(item)
            if year > 0 and year < min_year:
                filtered_year += 1
                logger.debug(f"Filtered (year): {desc} ({year} < {min_year})")
                continue
        
        if tid:
            valid_candidates.append(desc)
    
    logger.info(f"Filtered {len(candidates)} candidates → {len(valid_candidates)} valid items")
    logger.info(f"Removed {filtered_watched} watched, {filtered_genre} by genre, {filtered_title} by blocklist, {filtered_year} by year")
    
    return valid_candidates

def generate_recommendations(profile_text: str, candidates: List[str], exclusions: List[str], preferred_genres: List[str] = [], seed_items: List[str] = []) -> str:
    """Calls LLM to generate recommendations."""
    candidate_list_str = "\n".join([f"- {c}" for c in candidates[:CANDIDATE_LIMIT]])
    
    exclusion_text = ""
    if exclusions:
        exclusion_text = f"\n4. EXCLUSIONS: You must NOT recommend content from these genres: {', '.join(exclusions)}."

    preference_text = ""
    if preferred_genres:
        preference_text = f"\n5. PREFERENCES: Prioritize content in these genres: {', '.join(preferred_genres)}."

    specific_request_text = ""
    if seed_items:
        specific_request_text = f"\n6. SPECIFIC REQUEST: The user is specifically looking for content similar to these titles: {', '.join(seed_items)}. Heavily weight these as positive signals."

    prompt = f"""You are a recommendation engine. Select {NUM_RECOMMENDATIONS} items from the CANDIDATE LIST below that best match the USER PROFILE.

RULES: 
1. Only recommend items explicitly listed below. No hallucinations.
2. DIVERSITY: Select a variety of genres (drama, comedy, sci-fi, thriller, etc.) to avoid repetitiveness.
3. FRESHNESS: EXPLICIT CONSTRAINT: You must ONLY recommend items released in or after 2005. Do NOT include anything earlier.

USER PROFILE:
{profile_text}

CANDIDATE LIST ({len(candidates[:CANDIDATE_LIMIT])} items):
{candidate_list_str}

OUTPUT FORMAT (numbered list):
1. **Dune (2021)** - A visually stunning sci-fi epic with deep world-building.
2. **Tenet (2020)** - A complex, cerebral action thriller involving time manipulation.
[etc]

Select {NUM_RECOMMENDATIONS} diverse, fresh, and high-quality matches now:"""

    logger.info(f"Asking {MODEL_NAME} for recommendations...")
    if seed_items:
        logger.info(f"Using seed items: {seed_items}")
        
    from openai import OpenAI
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE
    )
    
    result = response.choices[0].message.content
    return result if result else "No recommendations generated."

def main(seed_items: List[str] = []) -> None:
    try:
        logger.info("Loading data...")
        history = load_json(HISTORY_FILE)
        candidates_data = load_json(CANDIDATES_FILE)
        
        if not history or not candidates_data:
            logger.error("Missing history or candidates data. Run fetch_data.py first.")
            return

        # Create set of watched IDs
        watched_ids = set()
        for item in history:
            tid = get_item_id(item)
            if tid:
                watched_ids.add(tid)

        # Load preferences FIRST (for hard genre filtering)
        exclusions = []
        preferred_genres = []
        title_blocklist = []
        preferred_min_year = 0
        if Path("preferences.json").exists():
            try:
                with open("preferences.json", "r") as f:
                    prefs = json.load(f)
                    exclusions = prefs.get("genre_exclusions", [])
                    preferred_genres = prefs.get("preferred_genres", [])
                    title_blocklist = prefs.get("title_blocklist", [])
                    preferred_min_year = prefs.get("preferred_min_year", 0)
                    logger.info(f"Loaded preferences - Exclusions: {exclusions}, Preferred: {preferred_genres}, Blocklist: {title_blocklist}, Min Year: {preferred_min_year}")
            except Exception as e:
                logger.warning(f"Could not load preferences: {e}")
        
        
        # Filter candidates by watched status, excluded genres, AND blocked titles
        valid_candidates = filter_candidates(candidates_data, watched_ids, exclusions, title_blocklist, preferred_min_year)
        
        if not PROFILE_FILE.exists():
            logger.error(f"Profile file not found: {PROFILE_FILE}")
            return
            
        with open(PROFILE_FILE, "r") as f:
            profile_text = f.read()

        recommendations = generate_recommendations(profile_text, valid_candidates, exclusions, preferred_genres, seed_items)
        
        with open(RECOMMENDATIONS_FILE, "w") as f:
            f.write(f"# 📺 Personalized Recommendations\n\n**Source**: Trakt Trending (Filtered)\n\n")
            f.write(recommendations)
            
        logger.info(f"Done! Saved to {RECOMMENDATIONS_FILE.name}")

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise e

if __name__ == "__main__":
    main()
