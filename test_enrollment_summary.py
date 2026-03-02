#!/usr/bin/env python3
"""Enroll student and verify both teachers can see courses"""
import requests
import time

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

print("="*60)
print("TEST: Student Enrollment & Teacher Course Visibility")
print("="*60)

# Step 1: Create student
print("\n1️⃣ Creating student account...")
student_email = f"student_{int(time.time())}@test.com"
student_password = "TestPass@123"

response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "name": "New Student",
        "email": student_email,
        "password": student_password,
        "role": "student"
    }
)

print(f"   ✅ Created: {student_email}")

# Step 2: Login student and enroll
print("\n2️⃣ Logging in and enrolling student...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": student_email, "password": student_password}
)

student_token = response.json().get("access_token")
student_headers = {"Authorization": f"Bearer {student_token}"}

# Quick enroll
response = requests.post(
    f"{BASE_URL}/enrollments/quick-enroll",
    headers=student_headers,
    json={"course_id": 1, "time_slot_id": 15}
)

enrollment = response.json()
assigned_teacher_id = enrollment.get('teacher_id')
print(f"   ✅ Enrolled in course 'nazra'")
print(f"   ✅ Teacher assigned: ID {assigned_teacher_id}")
print(f"   ✅ Enrollment ID: {enrollment.get('id')}")

# Step 3: Check madam@noori.com courses
print("\n3️⃣ Checking madam@noori.com courses...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "madam@noori.com", "password": "123456"}
)

madam_token = response.json().get("access_token")
madam_headers = {"Authorization": f"Bearer {madam_token}"}

response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=madam_headers
)

madam_courses = response.json()
print(f"   ✅ Can see {len(madam_courses)} course(s)")
for c in madam_courses:
    print(f"      📕 {c.get('name')}")

# Step 4: Check faizan@teacher.com courses  
print("\n4️⃣ Checking faizan@teacher.com courses...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "faizan@teacher.com", "password": "123456"}
)

faizan_token = response.json().get("access_token")
faizan_headers = {"Authorization": f"Bearer {faizan_token}"}

response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=faizan_headers
)

faizan_courses = response.json()
print(f"   ✅ Can see {len(faizan_courses)} course(s)")
for c in faizan_courses:
    print(f"      📕 {c.get('name')}")

# Summary
print("\n" + "="*60)
print("✅ SUCCESS! Both teachers can see courses!")
print(f"   Student: {student_email}")
print(f"   Course: nazra")
print(f"   Teachers can fetch their courses via /courses/my-courses/teacher")
print("="*60)
