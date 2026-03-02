"""
Create a test enrollment through the API to test display name generation
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

print("\n" + "="*70)
print("  CREATING TEST ENROLLMENT WITH DISPLAY NAMES")
print("="*70 + "\n")

# Step 1: Login
print("1. Logging in as student...")
login_response = requests.post(
    f"{BASE_URL}/auth/login/json",
    json={"email": "ali@student.com", "password": "student123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

data = login_response.json()
token = data["access_token"]
user = data["user"]
print(f"✅ Logged in as {user['name']}")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Get available data
print("\n2. Fetching available courses...")
courses = requests.get(f"{BASE_URL}/courses", headers=headers).json()
course = courses[0] if courses else None
if not course:
    print("❌ No courses available")
    exit(1)
print(f"✅ Found course: {course['name']} (ID: {course['id']})")

print("\n3. Fetching available teachers...")
teachers_response = requests.get(f"{BASE_URL}/teachers", headers=headers)
if teachers_response.status_code != 200:
    print(f"❌ Failed to get teachers: {teachers_response.text}")
    exit(1)
teachers_data = teachers_response.json()

# Extract teacher ID from response
teacher_id = None
if isinstance(teachers_data, list) and len(teachers_data) > 0:
    # Might be a list of dicts
    if isinstance(teachers_data[0], dict) and 'id' in teachers_data[0]:
        teacher_id = teachers_data[0]['id']

if not teacher_id:
    # Try to get from database directly
    from database import SessionLocal
    from models import Teacher
    db = SessionLocal()
    teacher = db.query(Teacher).first()
    if teacher:
        teacher_id = teacher.user_id
    db.close()

if not teacher_id:
    print("❌ No teachers available")
    exit(1)

print(f"✅ Found teacher ID: {teacher_id}")

print("\n4. Fetching available time slots...")
# Get time slots from database directly since API endpoint has routing issues
from database import SessionLocal
from models import TimeSlot
db = SessionLocal()
time_slots = db.query(TimeSlot).all()
db.close()

if not time_slots:
    print("❌ No time slots available")
    exit(1)
    
time_slot = time_slots[0]
print(f"✅ Found time slot ID: {time_slot.id}")

# Step 3: Create enrollment
print("\n5. Creating enrollment...")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

enrollment_payload = {
    "course_id": course["id"],
    "teacher_id": teacher_id,
    "time_slot_id": time_slot.id,
    "payment_method": "at_masjid",
    "start_date": tomorrow
}

print(f"   Payload: {json.dumps(enrollment_payload, indent=6)}")

enrollment_response = requests.post(
    f"{BASE_URL}/enrollments",
    headers=headers,
    json=enrollment_payload
)

if enrollment_response.status_code not in [200, 201]:
    print(f"❌ Enrollment creation failed (Status {enrollment_response.status_code})")
    print(f"   Response: {enrollment_response.text[:300]}")
    exit(1)

enrollment = enrollment_response.json()
print(f"✅ Enrollment created successfully! (ID: {enrollment.get('id')})")

# Step 4: Display the Jitsi link
print("\n" + "="*70)
print("  JITSI LINK RESULT")
print("="*70 + "\n")

jitsi_link = enrollment.get("jitsi_link")
if not jitsi_link:
    print("❌ No jitsi_link in response!")
    print(f"Response: {json.dumps(enrollment, indent=2)[:500]}")
else:
    print(f"✅ Jitsi Link Generated!")
    print(f"\n   Full URL: {jitsi_link}")
    
    # Parse components
    if "#userInfo.displayName=" in jitsi_link:
        base_url, params = jitsi_link.split("#", 1)
        display_name = params.replace("userInfo.displayName=", "")
        
        print(f"\n   Components:")
        print(f"   - Base Room URL: {base_url}")
        print(f"   - Display Name Parameter: {params}")
        print(f"   - Display Name Value: {display_name}")
        print(f"\n   ✅ Display Name is INCLUDED in the Jitsi URL!")
        print(f"      The student will auto-join as: {display_name}")
    else:
        print(f"\n   ⚠️  No display name parameter found")
        
print("\n" + "="*70 + "\n")

# Test in browser
print("🌐 BROWSER TEST:")
print(f"   Open this URL to test: {jitsi_link}")
print("\n" + "="*70 + "\n")
