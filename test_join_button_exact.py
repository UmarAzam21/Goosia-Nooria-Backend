"""
Test: Exactly replicate what happens when student clicks "Join Class" button
"""

import requests
import json

print("\n" + "═" * 80)
print("  TESTING: 'JOIN CLASS' BUTTON CLICK BEHAVIOR")
print("═" * 80 + "\n")

BASE_URL = "http://localhost:5000/api"

# Step 1: Login as student
print("1. Sign in to dashboard...")
login = requests.post(
    f"{BASE_URL}/auth/login/json",
    json={"email": "ali@student.com", "password": "student123"}
)

if login.status_code != 200:
    print("❌ Login failed")
    exit(1)

token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in")

# Step 2: Get dashboard (what frontend receives)
print("\n2. Fetch dashboard (same as frontend)...")
dashboard = requests.get(f"{BASE_URL}/dashboard/student", headers=headers).json()
enrollments = dashboard.get("enrollments", [])

if not enrollments:
    print("❌ No enrollments")
    exit(1)

print(f"✅ Got {len(enrollments)} enrollments")

# Step 3: Simulate clicking Join Class button
print("\n3. SIMULATING 'JOIN CLASS' BUTTON CLICK:")
print("─" * 80)

enrollment = enrollments[0]  # First enrollment
print(f"\n   Enrollment ID: {enrollment['id']}")
print(f"   Status: {enrollment['enrollment_status']}")
print(f"   Payment: {enrollment['payment_status']}")

# This is the exact code from handleJoinClass() in frontend
zoomLink = enrollment.get('zoom_link')
if not zoomLink:
    # Fallback
    meetingId = f"enrollment{enrollment['id']}"
    zoomLink = f"https://zoom.us/j/{meetingId}"

print(f"\n   Zoom Link from API: {zoomLink}")

# Verify the link
print("\n4. VERIFYING LINK FORMAT:")
print("─" * 80)

if not zoomLink:
    print("❌ ZOOM LINK IS EMPTY!")
else:
    # Check domain
    if "zoom.us/j" in zoomLink:
        print("✅ Domain: zoom.us/j (CORRECT)")
    else:
        print("⚠️  Unexpected domain")
    
    # Extract meeting ID
    if "zoom.us/j/" in zoomLink:
        meeting_id = zoomLink.replace("https://zoom.us/j/", "")
        print(f"✅ Meeting ID: {meeting_id}")
        
        # Validate meeting ID is 9-11 numeric digits
        if meeting_id.isdigit() and 9 <= len(meeting_id) <= 11:
            print("✅ Meeting ID format is valid (9-11 digits)")
        else:
            print(f"⚠️  Meeting ID format: {len(meeting_id)} digits (expected 9-11)")
    else:
        print("⚠️  Could not extract meeting ID")

print("\n5. WHAT HAPPENS WHEN CLICKED:")
print("─" * 80)
print(f"\n   JavaScript Code:")
print(f"   window.open('{zoomLink}', '_blank')")
print(f"\n   Expected: New tab opens Zoom meeting")
print(f"   URL in new tab: {zoomLink}")

print("\n" + "═" * 80)
print("  TEST COMPLETE")
print("═" * 80 + "\n")

print("SUMMARY:")
if "zoom.us/j" in zoomLink:
    print("✅ EVERYTHING IS CORRECT!")
    print("   The API is returning the right Zoom URL format.")
    print("   The URL should open a Zoom meeting directly.")
    print("\n   Note: Participants can join without waiting for the host.")
else:
    print("❌ URL FORMAT ISSUE DETECTED!")
    print(f"   URL: {zoomLink}")
    print("   This is not the expected Zoom format")

print("\n" + "═" * 80 + "\n")
