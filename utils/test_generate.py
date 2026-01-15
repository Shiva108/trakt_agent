#!/usr/bin/env python3
"""
Quick test to verify end-to-end recommendation generation
"""
import json
import sys
import os
from openai import OpenAI

# Configuration
API_BASE_URL = "http://127.0.0.1:1234/v1"
MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct-GGUF"
NUM_RECOMMENDATIONS = 10
API_KEY = os.getenv("LOCAL_LLM_API_KEY", "not-needed")

print("Testing recommendation generation...")
print(f"API: {API_BASE_URL}")
print(f"Model: {MODEL_NAME}")
print(f"Recommendations to generate: {NUM_RECOMMENDATIONS}")

try:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    prompt = f"""You are a recommendation engine. Recommend {NUM_RECOMMENDATIONS} diverse, high-quality sci-fi movies or TV shows.

OUTPUT FORMAT (numbered list):
1. **Title (Year)** - Brief description
2. **Title (Year)** - Brief description
[etc]

Generate {NUM_RECOMMENDATIONS} recommendations now:"""
    
    print(f"\nSending prompt to {MODEL_NAME}...")
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    result = response.choices[0].message.content
    
    print("\n" + "="*70)
    print("LLM RESPONSE:")
    print("="*70)
    print(result)
    print("="*70)
    
    # Write to file
    output_file = "../Trakt Recommendations.md"
    with open(output_file, "w") as f:
        f.write(f"# 📺 Personalized Recommendations\n\n**Source**: Trakt Trending (Filtered)\n\n")
        f.write(result)
    
    print(f"\n✅ Successfully wrote to: {output_file}")
    print(f"Lines in output: {len(result.splitlines())}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
