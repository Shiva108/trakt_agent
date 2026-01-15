#!/usr/bin/env python3
"""
Quick Configuration Script for Trakt Agent
Helps users easily configure their local LLM settings
"""

import json
import os


def main():
    print("=" * 70)
    print("Trakt Agent - LLM Configuration Helper")
    print("=" * 70)
    print()
    
    # Check if config.py exists
    if not os.path.exists("config.py"):
        print("❌ Error: config.py not found. Please run this from the trakt_agent directory.")
        return
    
    print("Current configuration:")
    print("-" * 70)
    
    # Read current config
    with open("config.py", "r") as f:
        content = f.read()
        
    # Extract current values
    import re
    api_url_match = re.search(r'API_BASE_URL = "(.*?)"', content)
    model_name_match = re.search(r'MODEL_NAME = "(.*?)"', content)
    
    current_url = api_url_match.group(1) if api_url_match else "Not found"
    current_model = model_name_match.group(1) if model_name_match else "Not found"
    
    print(f"  LLM Server URL: {current_url}")
    print(f"  Model Name: {current_model}")
    print()
    
    print("Do you want to change these settings? (y/n): ", end="")
    if input().strip().lower() != 'y':
        print("\n✅ Configuration unchanged.")
        return
    
    print()
    print("=" * 70)
    print("LLM Server Configuration")
    print("=" * 70)
    print()
    print("Common LLM Servers:")
    print("  1. LM Studio:        http://127.0.0.1:1234/v1")
    print("  2. Ollama (direct):  http://127.0.0.1:11434/v1")
    print("  3. OpenWebUI:        http://127.0.0.1:3000/v1")
    print("  4. Custom")
    print()
    
    choice = input("Select option (1-4) [1]: ").strip() or "1"
    
    url_map = {
        "1": "http://127.0.0.1:1234/v1",
        "2": "http://127.0.0.1:11434/v1",
        "3": "http://127.0.0.1:3000/v1",
    }
    
    if choice in url_map:
        new_url = url_map[choice]
    else:
        new_url = input("Enter custom LLM server URL (with /v1): ").strip()
    
    print()
    print("=" * 70)
    print("Model Name Configuration")
    print("=" * 70)
    print()
    print("Popular models (examples):")
    print("  1. Qwen/Qwen2.5-14B-Instruct-GGUF")
    print("  2. Meta-Llama-3-8B-Instruct")
    print("  3. Mistral-7B-Instruct-v0.2")
    print("  4. Custom (enter manually)")
    print()
    print("💡 Tip: Copy the exact model name from your LLM server interface!")
    print()
    
    model_choice = input("Select option (1-4) or enter custom model name [1]: ").strip() or "1"
    
    model_map = {
        "1": "Qwen/Qwen2.5-14B-Instruct-GGUF",
        "2": "Meta-Llama-3-8B-Instruct",
        "3": "Mistral-7B-Instruct-v0.2",
    }
    
    if model_choice in model_map:
        new_model = model_map[model_choice]
    elif model_choice == "4":
        new_model = input("Enter model name: ").strip()
    else:
        new_model = model_choice  # User entered custom name directly
    
    # Update config.py
    print()
    print("Updating config.py...")
    
    new_content = re.sub(
        r'API_BASE_URL = ".*?"',
        f'API_BASE_URL = "{new_url}"',
        content
    )
    new_content = re.sub(
        r'MODEL_NAME = ".*?"',
        f'MODEL_NAME = "{new_model}"',
        new_content
    )
    
    with open("config.py", "w") as f:
        f.write(new_content)
    
    print()
    print("=" * 70)
    print("✅ Configuration Updated Successfully!")
    print("=" * 70)
    print()
    print(f"  LLM Server URL: {new_url}")
    print(f"  Model Name: {new_model}")
    print()
    print("Next steps:")
    print("  1. Make sure your LLM server is running")
    print("  2. Verify the model is loaded")
    print("  3. Run: python fetch_data.py && python profile_taste.py && python recommend.py")
    print()


if __name__ == "__main__":
    main()
