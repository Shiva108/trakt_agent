#!/usr/bin/env python3
"""Generate recommendations directly"""
import json
import os
from openai import OpenAI

# Configuration
API_BASE_URL = "http://127.0.0.1:1234/v1"
MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct-GGUF"
API_KEY = os.getenv("LOCAL_LLM_API_KEY", "not-needed")

# Load data
with open("data/watch_history.json") as f:
    history = json.load(f)

with open("data/candidates.json") as f:
    candidates = json.load(f)

# Get watched IDs
watched_ids = set()
for item in history:
    if "movie" in item:
        watched_ids.add(item["movie"]["ids"]["trakt"])
    elif "show" in item:
        watched_ids.add(item["show"]["ids"]["trakt"])

# Filter candidates
valid_candidates = []
for item in candidates:
    c_id = None
    title = "Unknown"
    year = ""
    
    if "movie" in item:
        c_id = item["movie"]["ids"]["trakt"]
        title = item["movie"]["title"]
        year = item["movie"].get("year", "")
    elif "show" in item:
        c_id = item["show"]["ids"]["trakt"]
        title = item["show"]["title"]
        year = item["show"].get("year", "")
    
    if c_id and c_id not in watched_ids:
        desc = f"{title} ({year})" if year else title
        valid_candidates.append(desc)

print(f"Valid candidates: {len(valid_candidates)}")

# Load profile
with open("../Trakt Taste Profile.md") as f:
    profile = f.read()

# Generate recommendations
candidate_list = "\n".join([f"- {c}" for c in valid_candidates[:100]])

prompt = f"""You are a recommendation engine. Select 10 items from the CANDIDATE LIST below that best match the USER PROFILE.

STRICT RULES: Only recommend items explicitly listed below. No hallucinations.

USER PROFILE:
{profile}

CANDIDATE LIST ({len(valid_candidates[:100])} items):
{candidate_list}

OUTPUT FORMAT (numbered list):
1. **Title (Year)** - One-sentence explanation linking to profile elements.
2. **Title (Year)** - One-sentence explanation linking to profile elements.
[etc]

Select 10 diverse, high-quality matches now:"""

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

print("Generating recommendations...")
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

result = response.choices[0].message.content

# Write output
with open("../Trakt Recommendations.md", "w") as f:
    f.write("# 📺 Personalized Recommendations\n\n**Source**: Trakt Trending (Filtered)\n\n")
    f.write(result)

print("✅ Done! Saved to ../Trakt Recommendations.md")
print("\nRecommendations:")
print(result)
