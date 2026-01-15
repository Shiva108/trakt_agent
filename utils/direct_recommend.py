#!/usr/bin/env -S venv/bin/python
"""Direct recommendation generation bypassing file write issues"""
import json
from openai import OpenAI

# Load data
with open("data/watch_history.json") as f:
    history = json.load(f)
with open("data/candidates.json") as f:
    candidates = json.load(f)
with open("Trakt Taste Profile.md") as f:
    profile = f.read()

# Get watched IDs
watched_ids = set()
for item in history:
    if "movie" in item:
        watched_ids.add(item["movie"]["ids"]["trakt"])
    elif "show" in item:
        watched_ids.add(item["show"]["ids"]["trakt"])

print(f"Watched items: {len(watched_ids)}")

# Filter candidates
valid = []
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
        valid.append(desc)

print(f"Valid candidates: {len(valid)}")

# Generate recommendations
candidate_list = "\n".join([f"- {c}" for c in valid[:100]])

prompt = f"""You are an expert media curator specializing in unique recommendations. Each suggestion must be:
- Critically acclaimed or culturally significant
- Distinct from all previous recommendations
- Fresh: recent releases or underappreciated gems

USER PROFILE:
{profile}

CANDIDATE LIST ({len(valid[:100])} items):
{candidate_list}

OUTPUT FORMAT (numbered list):
1. **Title (Year)** - One-sentence explanation linking to profile elements.

Select 10 diverse, high-quality matches now:"""

import os

API_BASE_URL = "http://127.0.0.1:1234/v1"
API_KEY = os.getenv("LOCAL_LLM_API_KEY", "not-needed")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

print("Generating recommendations...")
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct-GGUF",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

result = response.choices[0].message.content

# Print to stdout so I can capture it
print("\n" + "="*70)
print("NEW RECOMMENDATIONS:")
print("="*70)
print(result)
print("="*70)
