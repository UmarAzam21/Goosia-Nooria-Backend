#!/usr/bin/env python3
"""Enroll student specifically with faizan@teacher.com"""
import requests
import json
import time

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

# Step 1: Get faizan's user ID
print("🔍 Finding faizan's teacher profile...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "faizan@teacher.com", "password": "123456"}
)

if response.status_code != 200:
    print(f"❌ Failed to login as faizan: {response.text}")
    exit(1)

faizan_token = response.json().get("access_token")
faizan_headers = {"Authorization": f"Bearer {faizan_token}"}

# Get faizan's profile to find teacher ID
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers=faizan_headers
)

if response.status_code == 200:
    faizan_user = response.json()
    faizan_user_id = faizan_user.get('id')
    print(f"✅ Faizan user ID: {faizan_user_id}")
    
    # Get faizan's teacher profile
    response = requests.get(f"{BASE_URL}/teachers")
    teachers = response.json()
    faizan_teacher = None
    for teacher in teachers:
        if teacher.get('user_id') == faizan_user_id:
            faizan_teacher = teacher
            break
    
    if faizan_teacher:
        faizan_teacher_id = faizan_teacher['id']
        print(f"✅ Faizan teacher ID: {faizan_teacher_id}")
    else:
        print("⚠️  Could not find faizan's teacher profile")
        exit(1)

# Step 2: Get course and time slot
print("\n📚 Fetching course information...")
response = requests.get(f"{BASE_URL}/courses")
courses = response.json()
course_id = courses[0]['id']
course_name = courses[0]['name']
print(f"✅ Course: {course_name} (ID: {course_id})")

response = requests.get(f"{BASE_URL}/teachers/{faizan_teacher_id}/time-slots")
time_slots = response.json()
time_slot_id = time_slots[0]['id'] if time_slots else 15
print(f"✅ Time slot: {time_slot_id}")

# Step 3: Create student
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

print(f"✅ Student: {student_email}")

# Step 4: Login as student
print(f"\n🔐 Logging in as student...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": student_email, "password": student_password}
)

student_token = response.json().get("access_token")
student_headers = {"Authorization": f"Bearer {student_token}"}
print(f"✅ Logged in")

# Step 5: Enroll with specific teacher
print(f"\n📝 Enrolling with faizan as teacher...")
response = requests.post(
    f"{BASE_URL}/enrollments/quick-enroll",
    headers=student_headers,
    json={
        "course_id": course_id,
        "time_slot_id": time_slot_id,
        "teacher_id": faizan_teacher_id  # Explicitly specify faizan
    }
)

if response.status_code != 201:
    print(f"❌ Enrollment failed: {response.status_code}")
    print(f"Response: {response.text}")
    # Try without explicit teacher_id
    response = requests.post(
        f"{BASE_URL}/enrollments/quick-enroll",
        headers=student_headers,
        json={
            "course_id": course_id,
            "time_slot_id": time_slot_id
        }
    )

enrollment = response.json()
assigned_teacher_id = enrollment.get('teacher_id')
print(f"✅ Enrolled successfully!")
print(f"   Enrollment ID: {enrollment.get('id')}")
print(f"   Assigned Teacher ID: {assigned_teacher_id}")

# Step 6: Check faizan's courses
print(f"\n📚 Checking faizan's courses...")
response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=faizan_headers
)

faizan_courses = response.json()
print(f"✅ Faizan sees {len(faizan_courses)} course(s):")
for course in faizan_courses:
    print(f"   📕 {course.get('name')} (ID: {course.get('id')})")

if any(c['id'] == course_id for c in faizan_courses):
    print(f"\n✅ SUCCESS! Faizan can see the '{course_name}' course!")
else:
    print(f"\n⚠️  Course not yet visible to faizan")
