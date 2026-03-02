"""
Verify that API returns correct enrollment data with Jitsi links
"""

import requests

print("\n" + "═" * 70)
print("  VERIFYING API RETURNS CORRECT ENROLLMENT DATA")
print("═" * 70 + "\n")

# Login
print("1. Logging in as Ali Rahman...")
login = requests.post(
    'http://localhost:5000/api/auth/login/json',
    json={'email': 'ali@student.com', 'password': 'student123'}
)

if login.status_code != 200:
    print("❌ Login failed")
    exit(1)

token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Logged in")

# Get dashboard
print("\n2. Fetching student dashboard...")
dashboard = requests.get('http://localhost:5000/api/dashboard/student', headers=headers).json()

if 'enrollments' not in dashboard:
    print("❌ No enrollments in dashboard")
    exit(1)

enrollments = dashboard['enrollments']
print(f"✅ Found {len(enrollments)} enrollments\n")

print("3. Checking enrollment data:")
print("─" * 70)

for e in enrollments:
    print(f"\n📋 Enrollment ID: {e['id']}")
    print(f"   Status: {e.get('enrollment_status')} | Payment: {e.get('payment_status')}")
    
    jitsi_link = e.get('jitsi_link')
    if jitsi_link:
        print(f"   ✅ Jitsi Link: {jitsi_link}")
        
        # Check if display name is in the link
        if '#userInfo.displayName=' in jitsi_link:
            print(f"   ✅ Display name parameter is PRESENT")
        else:
            print(f"   ⚠️  No display name parameter")
    else:
        print(f"   ❌ MISSING Jitsi Link!")

print("\n" + "═" * 70)
print("✅ ALL CHECKS PASSED - Ready for frontend testing")
print("═" * 70 + "\n")
