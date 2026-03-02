#!/usr/bin/env python3
"""Check what login endpoint actually returns"""
import requests
import json

BASE_URL = "http://localhost:5001/api"

response = requests.post(
    f"{BASE_URL}/auth/login/json",
    json={"email": "ali@student.com", "password": "student123"},
    timeout=5
)

print("Login response status:", response.status_code)
print("Full response:")
print(json.dumps(response.json(), indent=2))
