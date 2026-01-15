import requests
import json
import sys

SECRETS_FILE = "secrets.json"
TOKEN_FILE = "token.json"
BASE_URL = "https://api.trakt.tv"

def exchange_pin(pin):
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        
    payload = {
        "code": pin,
        "client_id": secrets["client_id"],
        "client_secret": secrets["client_secret"],
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code"
    }
    
    print(f"Exchanging PIN {pin} for token...")
    response = requests.post(f"{BASE_URL}/oauth/token", json=payload)
    
    if response.status_code == 200:
        token_data = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        print("Success! Token saved.")
    else:
        print(f"Error exchange PIN: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exchange_pin.py <PIN>")
        sys.exit(1)
    exchange_pin(sys.argv[1])
