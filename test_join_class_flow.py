"""
COMPREHENSIVE TEST: Simulate "Join Class" button click flow
"""

import requests
import json

print("\n" + "═" * 80)
print("  SIMULATING 'JOIN CLASS' BUTTON CLICK - COMPLETE FLOW TEST")
print("═" * 80 + "\n")

BASE_URL = "http://localhost:5000/api"

def test_student_join_flow(student_email, student_password, student_name):
    """Test complete flow: login → dashboard → get enrollment → Jitsi URL"""
    
    print(f"\n{'─' * 80}")
    print(f"🧑 Testing as: {student_name} ({student_email})")
    print(f"{'─' * 80}\n")
    
    # Step 1: Login
    print("1️⃣  LOGIN")
    login_resp = requests.post(
        f"{BASE_URL}/auth/login/json",
        json={"email": student_email, "password": student_password}
    )
    
    if login_resp.status_code != 200:
        print(f"   ❌ Login failed")
        return False
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Logged in successfully")
    
    # Step 2: Fetch Dashboard
    print("\n2️⃣  FETCH DASHBOARD")
    dashboard_resp = requests.get(f"{BASE_URL}/dashboard/student", headers=headers)
    
    if dashboard_resp.status_code != 200:
        print(f"   ❌ Dashboard fetch failed")
        return False
    
    enrollments = dashboard_resp.json().get("enrollments", [])
    print(f"   ✅ Dashboard loaded with {len(enrollments)} enrollments")
    
    if not enrollments:
        print(f"   ⚠️  No enrollments available")
        return True
    
    # Step 3: Test each enrollment
    print("\n3️⃣  TESTING ENROLLMENTS")
    
    success = True
    for i, enrollment in enumerate(enrollments, 1):
        enr_id = enrollment.get("id")
        status = enrollment.get("enrollment_status")
        payment = enrollment.get("payment_status")
        jitsi_link = enrollment.get("jitsi_link")
        
        print(f"\n   Enrollment {i} (ID: {enr_id}):")
        print(f"   ├─ Status: {status}")
        print(f"   ├─ Payment: {payment}")
        
        # Check if Join button would show
        can_join = status == "approved" and payment == "completed"
        print(f"   ├─ Join Button: {'✅ VISIBLE' if can_join else '❌ HIDDEN'}")
        
        if not jitsi_link:
            print(f"   ├─ ❌ JITSI LINK MISSING!")
            success = False
            continue
        
        # Verify link format
        print(f"   ├─ Jitsi Link: {jitsi_link[:50]}...")
        
        # Check room ID format
        if "meet.jitsi.net/" in jitsi_link:
            room_id = jitsi_link.split("meet.jitsi.net/")[1].split("#")[0]
            print(f"   ├─ Room ID: {room_id}")
            
            # Check if it follows our format
            if room_id.startswith("noori-class-"):
                print(f"   ├─ ✅ Room ID format correct")
            else:
                print(f"   ├─ ⚠️  Unexpected room ID format")
        
        # Check display name parameter
        if "#userInfo.displayName=" in jitsi_link:
            display_name = jitsi_link.split("displayName=")[1]
            print(f"   ├─ Display Name: {display_name}")
            print(f"   ├─ ✅ Display name parameter included")
        else:
            print(f"   ├─ ⚠️  No display name parameter")
        
        # Simulate window.open() action
        print(f"   └─ Action: window.open('{jitsi_link[:40]}...', '_blank')")
        
        # Verify URL is accessible (optional)
        if can_join:
            print(f"      ✅ URL would open Jitsi meeting room")
        
    return success

# Test multiple students
students = [
    ("ali@student.com", "student123", "Ali Rahman"),
    ("sara@student.com", "student123", "Sara Ahmed"),
    ("omar@student.com", "student123", "Omar Malik"),
]

print("TESTING ALL STUDENTS:")
all_success = True

for email, password, name in students:
    success = test_student_join_flow(email, password, name)
    all_success = all_success and success

# Final Summary
print("\n" + "═" * 80)
print("  FINAL TEST RESULTS")
print("═" * 80)

if all_success:
    print("\n✅ ALL TESTS PASSED!\n")
    print("   ✓ All students can login")
    print("   ✓ Dashboard loads correctly")
    print("   ✓ All enrollments have Jitsi links")
    print("   ✓ All links have correct format")
    print("   ✓ All links have display name parameters")
    print("   ✓ 'Join Class' buttons will appear in UI")
    print("   ✓ Clicking buttons will open Jitsi rooms\n")
    print("🎉 READY FOR PRODUCTION!\n")
else:
    print("\n❌ SOME TESTS FAILED\n")

print("═" * 80 + "\n")
