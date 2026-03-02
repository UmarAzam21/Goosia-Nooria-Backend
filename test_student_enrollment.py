#!/usr/bin/env python3
"""Enroll a student in a course with faizan as teacher, then verify teacher sees it"""
import requests
import json

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

# Step 1: Get all courses
print("📚 Fetching available courses...")
response = requests.get(f"{BASE_URL}/courses")
if response.status_code != 200:
    print(f"❌ Failed to fetch courses: {response.text}")
    exit(1)

courses = response.json()
print(f"✅ Found {len(courses)} course(s)")
for course in courses:
    print(f"  - {course.get('name')} (ID: {course.get('id')})")

if not courses:
    print("❌ No courses available")
    exit(1)

course_id = courses[0]['id']
course_name = courses[0]['name']
print(f"\n✅ Using course: {course_name} (ID: {course_id})")

# Step 2: Get teachers for this course
print(f"\n👨‍🏫 Fetching teachers for course {course_name}...")
response = requests.get(f"{BASE_URL}/teachers?course_id={course_id}")
if response.status_code != 200:
    print(f"❌ Failed to fetch teachers: {response.text}")
    exit(1)

teachers = response.json()
print(f"✅ Found {len(teachers)} teacher(s)")
for teacher in teachers:
    print(f"  - {teacher.get('name')} (ID: {teacher.get('id')}, Email: {teacher.get('email')})")

# Find faizan
faizan_teacher = None
for teacher in teachers:
    if 'faizan' in (teacher.get('email') or '').lower():
        faizan_teacher = teacher
        break

if not faizan_teacher:
    print(f"\n⚠️  faizan@teacher.com not found in teacher list")
    print("Available teachers:", [t.get('email') for t in teachers])
    if teachers:
        faizan_teacher = teachers[0]
        print(f"Using first teacher instead: {faizan_teacher.get('name')}")
    else:
        print("❌ No teachers available")
        exit(1)

teacher_id = faizan_teacher['id']
print(f"✅ Using teacher: {faizan_teacher.get('name')} (ID: {teacher_id})")

# Step 3: Get time slots for this teacher
print(f"\n⏰ Fetching time slots for teacher...")
response = requests.get(f"{BASE_URL}/teachers/{teacher_id}/time-slots")
if response.status_code != 200:
    print(f"❌ Failed to fetch time slots: {response.text}")
    exit(1)

time_slots = response.json()
print(f"✅ Found {len(time_slots)} time slot(s)")
for slot in time_slots:
    print(f"  - {slot.get('start_time')} - {slot.get('end_time')} on {slot.get('day_of_week')}")

if not time_slots:
    print("❌ No time slots available")
    exit(1)

time_slot_id = time_slots[0]['id']
print(f"✅ Using time slot: {time_slots[0].get('start_time')} - {time_slots[0].get('end_time')}")

# Step 4: Create a student or use existing one
print("\n👤 Creating/Using student account...")
student_email = f"test_student_{int(__import__('time').time())}@test.com"
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

if response.status_code == 201:
    print(f"✅ Created student: {student_email}")
elif response.status_code == 422:
    print(f"⚠️  Student might already exist: {student_email}")
    print(f"Response: {response.text}")
else:
    print(f"❌ Failed to create student: {response.text}")
    exit(1)

# Step 5: Login as student
print(f"\n🔐 Logging in as student...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": student_email, "password": student_password}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.text}")
    exit(1)

student_token = response.json().get("access_token")
print(f"✅ Logged in successfully")

# Step 6: Enroll in course
print(f"\n📝 Enrolling student in course {course_name}...")
student_headers = {"Authorization": f"Bearer {student_token}"}
response = requests.post(
    f"{BASE_URL}/enrollments",
    headers=student_headers,
    json={
        "course_id": course_id,
        "teacher_id": teacher_id,
        "time_slot_id": time_slot_id,
        "start_date": "2026-03-05",
        "payment_method": "bank_transfer"
    }
)

if response.status_code != 201:
    print(f"❌ Enrollment failed: {response.text}")
    exit(1)

enrollment = response.json()
print(f"✅ Enrolled successfully!")
print(f"   Enrollment ID: {enrollment.get('id')}")
print(f"   Course: {course_name}")
print(f"   Teacher: {faizan_teacher.get('name')}")
print(f"   Status: {enrollment.get('enrollment_status')}")

# Step 7: Now login as faizan and check if course is visible
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

# Step 8: Check faizan's courses
print(f"\n📚 Fetching faizan's courses...")
faizan_headers = {"Authorization": f"Bearer {faizan_token}"}
response = requests.get(
    f"{BASE_URL}/courses/my-courses/teacher",
    headers=faizan_headers
)

if response.status_code != 200:
    print(f"❌ Failed to fetch courses: {response.text}")
    exit(1)

faizan_courses = response.json()
print(f"\n✅ Faizan can now see {len(faizan_courses)} course(s):")
for course in faizan_courses:
    print(f"  📕 {course.get('name')} (ID: {course.get('id')})")

# Check if enrolled course is visible
if any(c['id'] == course_id for c in faizan_courses):
    print(f"\n✅ SUCCESS! Faizan can see the '{course_name}' course after student enrollment!")
else:
    print(f"\n⚠️  Course '{course_name}' not yet visible to faizan")
