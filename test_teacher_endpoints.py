#!/usr/bin/env python3
"""Test /classes/my-classes endpoint for teacher"""
import requests

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

# Login as teacher
print("🔐 Testing /classes/my-classes endpoint...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "rehan@teacher.com", "password": "123456"}
)

if response.status_code != 200:
    print(f"❌ Login failed")
    exit(1)

token = response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Test /classes/my-classes
print("\n1️⃣ Testing /classes/my-classes...")
response = requests.get(f"{BASE_URL}/classes/my-classes", headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test /courses/my-courses/teacher
print("\n2️⃣ Testing /courses/my-courses/teacher...")
response = requests.get(f"{BASE_URL}/courses/my-courses/teacher", headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")
