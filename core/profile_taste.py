#!/usr/bin/env -S venv/bin/python
"""
Taste Profile Analysis Module

Analyzes watch history to generate a personalized taste profile
using LLM-based pattern recognition.
"""
import json
from collections import Counter
from typing import Dict, List, Any

from config import (
    API_BASE_URL, MODEL_NAME, API_KEY, TEMPERATURE,
    HISTORY_FILE, PROFILE_FILE, PREFERENCES_FILE,
    PROFILE_ANALYSIS_LIMIT, logger
)

def calculate_statistics(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate viewing statistics from watch history.
    
    Args:
        history: List of watch history items from Trakt.
        
    Returns:
        Dictionary containing total items, movie/TV breakdown, decade analysis.
    """
    
    total_items = len(history)
    movies = [item for item in history if "movie" in item]
    shows = [item for item in history if "show" in item]
    
    # Count unique shows vs total episodes
    unique_shows = len(set(item["show"]["ids"]["trakt"] for item in shows))
    
    # Calculate percentages
    movie_pct = (len(movies) / total_items * 100) if total_items > 0 else 0
    tv_pct = 100 - movie_pct
    
    # Analyze decades (from movies and shows)
    decades = []
    for item in history:
        if "movie" in item and "year" in item["movie"]:
            year = item["movie"]["year"]
            if year:
                decades.append((year // 10) * 10)
        elif "show" in item and "year" in item["show"]:
            year = item["show"]["year"]
            if year:
                decades.append((year // 10) * 10)
    
    decade_counts = Counter(decades).most_common(3)
    
    stats = {
        "total_items": total_items,
        "movies": len(movies),
        "tv_episodes": len(shows),
        "unique_shows": unique_shows,
        "movie_pct": round(movie_pct, 1),
        "tv_pct": round(tv_pct, 1),
        "top_decades": decade_counts,
        "avg_episodes_per_show": round(len(shows) / unique_shows, 1) if unique_shows > 0 else 0
    }
    
    return stats

def analyze_taste() -> None:
    """
    Main taste analysis function.
    
    Loads watch history, calculates statistics, and uses LLM to generate
    a comprehensive taste profile. Saves output to PROFILE_FILE.
    """
    if not HISTORY_FILE.exists():
        logger.error("No history data found. Run 'cli.py fetch' first.")
        return

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    # Calculate statistics
    stats = calculate_statistics(history)
    
    # Pre-process history into a readable string
    watched_list = []
    for item in history:
        if "movie" in item:
            watched_list.append(f"Movie: {item['movie']['title']} ({item['movie'].get('year', 'N/A')})")
        elif "show" in item:
            watched_list.append(f"Show: {item['show']['title']} (S{item['episode']['season']}E{item['episode']['number']})")
    
    watched_text = "\n".join(watched_list[:PROFILE_ANALYSIS_LIMIT])
    
    # Load user preferences
    preferences = {}
    if PREFERENCES_FILE.exists():
        with open(PREFERENCES_FILE, "r") as f:
            preferences = json.load(f)
    
    genre_exclusions = preferences.get("genre_exclusions", [])
    min_scores = preferences.get("min_imdb_score", {})
    
    # Format statistics for prompt
    stats_text = f"""
VIEWING STATISTICS:
- Total items analyzed: {stats['total_items']} ({stats['movies']} movies, {stats['tv_episodes']} TV episodes from {stats['unique_shows']} shows)
- Content preference: TV {stats['tv_pct']}% | Movies {stats['movie_pct']}%
- Top decades: {', '.join([f"{d}s ({c} items)" for d, c in stats['top_decades']])}
- Binge behavior: Avg {stats['avg_episodes_per_show']} episodes per show
"""
    
    exclusions_text = ""
    if genre_exclusions:
        exclusions_text = f"\n\nHARD EXCLUSIONS (never recommend): {', '.join(genre_exclusions)}"
    
    quality_text = ""
    if min_scores:
        tv_min = min_scores.get("tv_shows", 0)
        movie_min = min_scores.get("movies", 0)
        if tv_min > 0 or movie_min > 0:
            quality_text = f"\n\nQUALITY STANDARDS: TV shows IMDb ≥{tv_min}, Movies IMDb ≥{movie_min}"
    
    logger.info(f"Analyzing {stats['total_items']} items with {MODEL_NAME}...")
    logger.info(f"  - {stats['movies']} movies, {stats['unique_shows']} unique TV shows")
    logger.info(f"  - Preference: {stats['tv_pct']}% TV, {stats['movie_pct']}% Movies")
    
    prompt = f"""You are an expert media analyst. Deeply analyze this watch history to understand the viewer's sophisticated taste.

WATCH HISTORY (Top {PROFILE_ANALYSIS_LIMIT} items):
{watched_text}

{stats_text}{exclusions_text}{quality_text}

Analyze deeply for:
1. Genre distribution and patterns
2. Psychological themes and narrative elements  
3. Viewing style (pacing, tone, complexity preferences)
4. Creative patterns (directors, visual styles, storytelling approaches)
5. Emotional drivers and what the viewer seeks
6. Both explicit and subtle preferences

OUTPUT FORMAT (be specific and insightful):

## Core Preferences
- **Primary Genres**: [List with percentages if detectable, e.g., "Sci-Fi (45%), Thriller (30%)"]
- **Content Type**: [TV vs Movies preference with insight]
- **Era Preference**: [Decades, classic vs modern]

## Themes & Psychology
- [List 4-6 recurring psychological themes, narrative patterns, or philosophical questions]
- [Be specific - not just "action" but "morally complex action with consequences"]

## Viewing Style
- **Pacing**: [Slow-burn vs fast-paced, patience for development]
- **Tone**: [Light/dark, optimistic/cynical, gritty/polished]
- **Complexity**: [Cerebral/layered vs straightforward, puzzle-box narratives]
- **Storytelling**: [Character-driven vs plot-driven, ambiguous endings vs resolution]

## Creative & Aesthetic Preferences
- **Visual Style**: [Cinematography, practical vs CGI, atmospheric vs clean]
- **Narrative Structure**: [Linear, non-linear, ensemble cast, single protagonist]
- **World-Building**: [Detailed universes vs focused settings]

## Emotional Drivers
- [What emotions/experiences does this viewer seek?]
- [Intellectual stimulation, emotional catharsis, escapism, challenge?]

## Quality Standards{quality_text if not quality_text else ""}
{exclusions_text if exclusions_text else "- No explicit exclusions set"}

## Taste Summary
[4-6 word evocative description capturing their essence, e.g., "Cerebral Sci-Fi Puzzle Solver" or "Dark Philosophical Thriller Enthusiast"]

Be perceptive and find patterns that aren't obvious. This profile will drive personalized recommendations."""

    from openai import OpenAI
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    response_obj = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE
    )
    
    response = response_obj.choices[0].message.content
    
    # Save to Markdown
    with open(PROFILE_FILE, "w") as f:
        f.write("# Taste Profile\n\n")
        f.write(f"*Generated from {stats['total_items']} watched items*\n\n")
        f.write(response)
        
    logger.info(f"Enhanced profile saved to {PROFILE_FILE}")
    logger.info(f"Profile includes: viewing patterns, themes, style preferences, and emotional drivers")

def main():
    analyze_taste()

if __name__ == "__main__":
    try:
        analyze_taste()
    except FileNotFoundError as e:
        print(f"\n❌ Error: Required file not found: {e}")
        print("Run 'fetch_data.py' first to download watch history.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error analyzing taste profile: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Check LLM server is running: ./validate_llm.py")
        print(f"2. Verify watch history exists: ./data/watch_history.json")
        print(f"3. Check config.py settings")
        exit(1)
