#!/usr/bin/env python3
"""Test login with admin credentials"""
import requests
import json

BASE_URL = "http://localhost:5001/api"  # Updated to port 5001
EMAIL = "admin@masjid.com"
PASSWORD = "admin123"

print("=" * 80)
print("TESTING ADMIN LOGIN")
print("=" * 80)
print(f"Email: {EMAIL}")
print(f"Password: {PASSWORD}")
print(f"URL: {BASE_URL}/auth/login/json")
print()

try:
    response = requests.post(
        f"{BASE_URL}/auth/login/json",
        json={"email": EMAIL, "password": PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 80)
        print("✅ LOGIN SUCCESSFUL!")
        print("=" * 80)
        user = data.get('user', {})
        print(f"Name: {user.get('name')}")
        print(f"Email: {user.get('email')}")
        print(f"Role: {user.get('role')}")
        print(f"User ID: {user.get('id')}")
        print(f"Phone: {user.get('phone')}")
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
    else:
        print("\n❌ LOGIN FAILED")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
