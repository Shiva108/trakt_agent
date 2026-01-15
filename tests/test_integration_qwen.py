
import pytest
import requests
import json
from config import API_BASE_URL, MODEL_NAME

def test_llm_connection():
    """Verify that the configured LLM is reachable and responds."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=10)
        assert response.status_code == 200, f"Failed to connect to LLM: {response.text}"
        
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        message = data["choices"][0]["message"]["content"]
        assert message is not None
        print(f"\nModel Response: {message}")
        
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Could not connect to LLM at {API_BASE_URL}. Ensure the server is running.")

if __name__ == "__main__":
    test_llm_connection()
