import requests
import json

url = "https://api.simkl.com/movies/popular?limit=1&extended=full"
headers = {
    "Content-Type": "application/json",
    "simkl-api-key": "b574122fab7167ae547bd149020821d7cf742f06e7d82acefbee2b6ebb6bb701"
}

try:
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Content: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(e)
