#!/usr/bin/env python3
"""Test script to verify LLM connection and generate recommendations"""
import sys
import json

# Add diagnostic output
print("=" * 70, file=sys.stderr)
print("DIAGNOSTIC: Starting recommendation generation", file=sys.stderr)
print("=" * 70, file=sys.stderr)

try:
    from openai import OpenAI
    from config import API_BASE_URL, MODEL_NAME, NUM_RECOMMENDATIONS, API_KEY
    
    print(f"API_BASE_URL: {API_BASE_URL}", file=sys.stderr)
    print(f"MODEL_NAME: {MODEL_NAME}", file=sys.stderr)
    print(f"NUM_RECOMMENDATIONS: {NUM_RECOMMENDATIONS}", file=sys.stderr)
    
    # Test LLM connection
    print("\nTesting LLM connection...", file=sys.stderr)
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Say 'Hello' in exactly 1 word"}],
        temperature=0.7
    )
    
    print(f"LLM Response: {response.choices[0].message.content}", file=sys.stderr)
    print("✅ LLM connection successful!", file=sys.stderr)
    
except Exception as e:
    print(f"❌ ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
