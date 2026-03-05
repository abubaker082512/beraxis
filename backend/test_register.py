import requests
import json

url = "http://localhost:8002/api/v1/auth/register"
payload = {
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "organization_name": "Test Org"
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
