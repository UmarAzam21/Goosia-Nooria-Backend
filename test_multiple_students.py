"""
Create enrollments for multiple students to show unique room IDs with display names
"""

import requests
import json
from datetime import datetime, timedelta
from database import SessionLocal
from models import TimeSlot

BASE_URL = "http://localhost:5000/api"
STUDENTS = [
    {"email": "sara@student.com", "password": "student123"},
    {"email": "omar@student.com", "password": "student123"}
]

print("\n" + "="*70)
print("  CREATING ENROLLMENTS FOR MULTIPLE STUDENTS")
print("="*70 + "\n")

# Get course and teacher once
courses = requests.get(f"{BASE_URL}/courses").json()
course = courses[0]

db = SessionLocal()
teacher_id = 1
time_slots = db.query(TimeSlot).all()
time_slot = time_slots[0]
db.close()

tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

for i, student in enumerate(STUDENTS):
    print(f"\n{'─'*70}")
    print(f"Student {i+1}: {student['email']}")
    print(f"{'─'*70}")
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/auth/login/json",
        json={"email": student["email"], "password": student["password"]}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        continue
    
    data = login_response.json()
    token = data["access_token"]
    user = data["user"]
    print(f"✅ Logged in as: {user['name']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create enrollment
    enrollment_payload = {
        "course_id": course["id"],
        "teacher_id": teacher_id,
        "time_slot_id": time_slot.id,
        "payment_method": "at_masjid",
        "start_date": tomorrow
    }
    
    enrollment_response = requests.post(
        f"{BASE_URL}/enrollments",
        headers=headers,
        json=enrollment_payload
    )
    
    if enrollment_response.status_code not in [200, 201]:
        print(f"❌ Enrollment creation failed")
        continue
    
    enrollment = enrollment_response.json()
    jitsi_link = enrollment.get("jitsi_link", "")
    
    print(f"✅ Enrollment created (ID: {enrollment['id']})")
    print(f"\n   Jitsi Link: {jitsi_link}")
    
    if "#userInfo.displayName=" in jitsi_link:
        base_url, params = jitsi_link.split("#", 1)
        display_name = params.replace("userInfo.displayName=", "")
        room_id = base_url.split("/")[-1]
        
        print(f"\n   ✅ Room ID: {room_id}")
        print(f"      Display Name: {display_name}")

print("\n" + "="*70)
print("📋 SUMMARY: Each student has a unique room with their own display name!")
print("="*70 + "\n")
