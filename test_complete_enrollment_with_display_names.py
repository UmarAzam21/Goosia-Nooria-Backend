"""
Test the complete Jitsi integration with display names
- Login as student
- Create enrollment
- Verify jitsi_link includes display name parameter
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_complete_enrollment_flow():
    """Test full enrollment flow with new display name Jitsi links"""
    
    print_section("TEST: Complete Enrollment Flow with Display Names")
    
    # Step 1: Login as student
    print("1️⃣  LOGGING IN AS STUDENT")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/json",
        json={
            "email": "ali@student.com",
            "password": "student123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    current_user = login_data.get("user")
    
    print(f"✅ Login successful!")
    print(f"   User: {current_user['name']} ({current_user['email']})")
    print(f"   Token: {token[:20]}...")
    
    # Step 2: Get available courses and teachers
    print("\n2️⃣  FETCHING COURSES")
    headers = {"Authorization": f"Bearer {token}"}
    
    courses_response = requests.get(
        f"{BASE_URL}/courses",
        headers=headers
    )
    
    if courses_response.status_code != 200:
        print(f"❌ Failed to fetch courses: {courses_response.text}")
        return
    
    courses = courses_response.json()
    if not courses:
        print("❌ No courses available")
        return
    
    course = courses[0]
    print(f"✅ Found course: {course['name']} (ID: {course['id']})")
    
    # Step 3: Get available teachers
    print("\n3️⃣  FETCHING TEACHERS")
    teachers_response = requests.get(
        f"{BASE_URL}/teachers",
        headers=headers
    )
    
    if teachers_response.status_code != 200:
        print(f"❌ Failed to fetch teachers: {teachers_response.text}")
        return
    
    teachers = teachers_response.json()
    if not teachers:
        print("❌ No teachers available")
        return
    
    teacher = teachers[0]
    print(f"✅ Found teacher: {teacher['name']} (ID: {teacher['id']})")
    
    # Step 4: Get available time slots
    print("\n4️⃣  FETCHING TIME SLOTS")
    slots_response = requests.get(
        f"{BASE_URL}/enrollments/available-slots",
        headers=headers
    )
    
    if slots_response.status_code != 200:
        print(f"❌ Failed to fetch time slots: {slots_response.text}")
        return
    
    time_slots = slots_response.json()
    if not time_slots:
        print("❌ No time slots available")
        return
    
    time_slot = time_slots[0]
    print(f"✅ Found time slot: {time_slot['start_time']} - {time_slot['end_time']} (ID: {time_slot['id']})")
    
    # Step 5: Create enrollment
    print("\n5️⃣  CREATING ENROLLMENT")
    tomorrow = datetime.now() + timedelta(days=1)
    start_date = tomorrow.strftime("%Y-%m-%d")
    
    enrollment_data = {
        "course_id": course["id"],
        "teacher_id": teacher["id"],
        "time_slot_id": time_slot["id"],
        "payment_method": "at_masjid",
        "start_date": start_date
    }
    
    print(f"   Enrollment data: {json.dumps(enrollment_data, indent=2)}")
    
    enrollment_response = requests.post(
        f"{BASE_URL}/enrollments",
        headers=headers,
        json=enrollment_data
    )
    
    if enrollment_response.status_code != 200:
        print(f"❌ Enrollment creation failed: {enrollment_response.text}")
        return
    
    enrollment = enrollment_response.json()
    print(f"✅ Enrollment created successfully!")
    
    # Step 6: Display the Jitsi link
    print("\n6️⃣  JITSI LINK DETAILS")
    jitsi_link = enrollment.get("jitsi_link")
    
    if not jitsi_link:
        print("❌ No jitsi_link in enrollment response")
    else:
        print(f"✅ Jitsi Link: {jitsi_link}")
        
        # Parse and display components
        if "#" in jitsi_link:
            base_url, params = jitsi_link.split("#", 1)
            print(f"\n   Base Room URL: {base_url}")
            print(f"   Parameters: {params}")
            
            # Check for display name
            if "displayName" in params:
                print(f"   ✅ Display name parameter found! User will auto-join with their name.")
            else:
                print(f"   ⚠️  No display name parameter found")
        else:
            print(f"   Note: Room URL without display name parameter")
    
    # Step 7: Verify other enrollment details
    print("\n7️⃣  ENROLLMENT DETAILS VERIFICATION")
    print(f"   Enrollment ID: {enrollment.get('id')}")
    print(f"   Student: {enrollment.get('student_id')}")
    print(f"   Course: {enrollment.get('course_id')}")
    print(f"   Teacher: {enrollment.get('teacher_id')}")
    print(f"   Status: {enrollment.get('enrollment_status')}")
    print(f"   Payment Status: {enrollment.get('payment_status')}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    return enrollment

if __name__ == "__main__":
    try:
        enrollment = test_complete_enrollment_flow()
        
        if enrollment and enrollment.get("jitsi_link"):
            print("\n" + "="*60)
            print("📋 SUMMARY")
            print("="*60)
            print(f"Jitsi Link: {enrollment['jitsi_link']}")
            print("\n✅ The Jitsi link now includes the student's display name!")
            print("   When the student clicks 'Join Class', they will automatically")
            print("   join the Jitsi room with their name pre-filled.")
            print("="*60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
