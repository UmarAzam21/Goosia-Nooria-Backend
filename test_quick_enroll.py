#!/usr/bin/env python3
"""Enroll a student in a course using quick-enroll endpoint"""
import requests
import json
import time

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

# Step 1: Get all courses
print("📚 Fetching available courses...")
response = requests.get(f"{BASE_URL}/courses")
courses = response.json()
print(f"✅ Found {len(courses)} course(s): {[c['name'] for c in courses]}")

course_id = courses[0]['id']
course_name = courses[0]['name']

# Step 2: Create student
print("\n👤 Creating student account...")
student_email = f"student_{int(time.time())}@test.com"
student_password = "TestPass@123"

response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "name": "Test Student",
        "email": student_email,
        "password": student_password,
        "role": "student"
    }
)

print(f"✅ Student created: {student_email}")

# Step 3: Login as student
print(f"\n🔐 Logging in as student...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": student_email, "password": student_password}
)

student_token = response.json().get("access_token")
print(f"✅ Logged in")

# Step 4: Quick enroll
print(f"\n📝 Enrolling in course using auto-selection...")
student_headers = {"Authorization": f"Bearer {student_token}"}

# Get a time slot to use
response = requests.get(f"{BASE_URL}/teachers/1/time-slots")
time_slots = response.json()
time_slot_id = time_slots[0]['id'] if time_slots else 1

print(f"   Course: {course_name} (ID: {course_id})")
print(f"   Time slot: {time_slot_id}")

response = requests.post(
    f"{BASE_URL}/enrollments/quick-enroll",
    headers=student_headers,
    json={
        "course_id": course_id,
        "time_slot_id": time_slot_id
    }
)

if response.status_code != 201:
    print(f"❌ Enrollment failed: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

enrollment = response.json()
print(f"✅ Enrolled successfully!")
print(f"   Enrollment ID: {enrollment.get('id')}")
print(f"   Teacher ID: {enrollment.get('teacher_id')}")
print(f"   Status: {enrollment.get('enrollment_status')}")

teacher_id = enrollment.get('teacher_id')

# Step 5: Get teacher info
print(f"\n👨‍🏫 Checking teacher details...")
response = requests.get(f"{BASE_URL}/teachers/{teacher_id}")
if response.status_code == 200:
    teacher = response.json()
    print(f"   Teacher: {teacher}")

# Step 6: Login as faizan and check courses
print(f"\n🔐 Logging in as faizan@teacher.com...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "faizan@teacher.com", "password": "123456"}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.text}")
    exit(1)

faizan_token = response.json().get("access_token")
print(f"✅ Logged in as faizan")

# Step 7: Check faizan's courses
print(f"\n📚 Fetching faizan's courses...")
faizan_headers = {"Authorization": f"Bearer {faizan_token}"}
response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=faizan_headers
)

faizan_courses = response.json()
print(f"✅ Faizan can see {len(faizan_courses)} course(s):")
for course in faizan_courses:
    print(f"   📕 {course.get('name')} (ID: {course.get('id')})")

if faizan_courses:
    print(f"\n✅ SUCCESS! Teacher can see courses!")
else:
    print(f"\n⚠️  No courses visible to faizan")
