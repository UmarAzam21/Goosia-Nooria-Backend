#!/usr/bin/env python3
"""Check if faizan@teacher.com can fetch their courses"""
import requests

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"
TEACHER_EMAIL = "faizan@teacher.com"
TEACHER_PASSWORD = "123456"

# Step 1: Login as faizan
print("🔐 Logging in as faizan@teacher.com...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": TEACHER_EMAIL, "password": TEACHER_PASSWORD}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.text}")
    exit(1)

token = response.json().get("access_token")
print(f"✅ Logged in successfully")

# Step 2: Get faizan's courses
print("\n📚 Fetching faizan's courses...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    courses = response.json()
    print(f"\n✅ Found {len(courses)} course(s):")
    if courses:
        for course in courses:
            print(f"  📕 {course.get('name')} (ID: {course.get('id')})")
    else:
        print("  (No courses assigned)")
else:
    print(f"❌ Error: {response.text}")
