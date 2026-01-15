#!/usr/bin/env -S venv/bin/python
"""
Helper script to validate LLM connection and model availability
"""
import sys
from openai import OpenAI
from config import API_BASE_URL, MODEL_NAME, API_KEY

def validate_llm():
    """Validate LLM server connection and model availability"""
    try:
        print(f"Connecting to {API_BASE_URL}...")
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
        
        # List available models
        print("Fetching available models...")
        models = client.models.list()
        available_models = [m.id for m in models.data]
        
        print(f"\n✅ Connected to LLM server")
        print(f"Available models ({len(available_models)}):")
        for model in available_models:
            marker = "✓ CONFIGURED" if model == MODEL_NAME else " "
            print(f"  {marker} {model}")
        
        # Check if configured model is available
        if MODEL_NAME in available_models:
            print(f"\n✅ Configured model '{MODEL_NAME}' is available")
            
            # Test the model with a simple request
            print(f"\nTesting model response...")
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": "Reply with just 'OK'"}],
                temperature=0.1,
                max_tokens=10
            )
            result = response.choices[0].message.content
            print(f"✅ Model responded: {result}")
            return True
        else:
            print(f"\n❌ ERROR: Configured model '{MODEL_NAME}' not found!")
            print(f"\nTo fix:")
            print(f"1. Check that '{MODEL_NAME}' is loaded in LM Studio")
            print(f"2. Or update MODEL_NAME in config.py to match one of the available models above")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure LM Studio server is running on {API_BASE_URL}")
        print(f"2. Check that at least one model is loaded")
        print(f"3. Verify the server URL in config.py")
        return False

if __name__ == "__main__":
    success = validate_llm()
    sys.exit(0 if success else 1)
