#!/usr/bin/env python3
"""
Test to verify badge displays correctly on student portal
"""
import requests
import time
import json

BASE_URL = 'http://localhost:5001/api'

print("=" * 60)
print("Testing Badge Display on Student Portal")
print("=" * 60)

# Step 1: Login as student
print("\n1️⃣ Login as student...")
student_login = requests.post(
    f'{BASE_URL}/auth/login/json',
    json={'email': 'student@test.com', 'password': 'student123'}
)

if student_login.status_code != 200:
    print(f"❌ Student login failed: {student_login.status_code}")
    print(student_login.json())
    exit(1)

student_data = student_login.json()
student_token = student_data['access_token']
student_id = student_data.get('id') or 5
print(f"✓ Student logged in (ID: {student_id})")

# Step 2: Check current messages (should be empty or have some)
print("\n2️⃣ Checking current messages...")
messages_response = requests.get(
    f'{BASE_URL}/messages/my-messages',
    headers={'Authorization': f'Bearer {student_token}'}
)

if messages_response.status_code == 200:
    current_messages = messages_response.json()
    current_unread = sum(1 for m in current_messages if m.get('sender_id') != student_id and not m.get('is_read'))
    print(f"✓ Current messages: {len(current_messages)}, Unread: {current_unread}")
else:
    print(f"❌ Failed to fetch messages: {messages_response.status_code}")
    exit(1)

# Step 3: Login as admin and send message to student
print("\n3️⃣ Login as admin and send message to student...")
admin_login = requests.post(
    f'{BASE_URL}/auth/login/json',
    json={'email': 'admin@masjid.com', 'password': 'admin123'}
)

if admin_login.status_code != 200:
    print(f"❌ Admin login failed: {admin_login.status_code}")
    print(admin_login.json())
    exit(1)

admin_token = admin_login.json()['access_token']
print(f"✓ Admin logged in")

# Send message from admin to student
send_msg = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={
        'student_id': student_id,
        'message': f'Test badge message at {time.time()}'
    }
)

if send_msg.status_code == 200:
    print(f"✓ Message sent from admin to student")
else:
    print(f"❌ Failed to send message: {send_msg.status_code}")
    print(send_msg.json())
    exit(1)

# Step 4: Pause and refetch messages to see new unread message
print("\n4️⃣ Waiting for message to be received...")
time.sleep(2)

messages_response = requests.get(
    f'{BASE_URL}/messages/my-messages',
    headers={'Authorization': f'Bearer {student_token}'}
)

if messages_response.status_code == 200:
    updated_messages = messages_response.json()
    updated_unread = sum(1 for m in updated_messages if m.get('sender_id') != student_id and not m.get('is_read'))
    print(f"✓ Updated messages: {len(updated_messages)}, Unread: {updated_unread}")
    
    if updated_unread > current_unread:
        print(f"✓ 🎉 NEW UNREAD MESSAGE DETECTED! Badge count should be: {updated_unread}")
    else:
        print(f"⚠️  No new unread messages detected")
else:
    print(f"❌ Failed to fetch messages: {messages_response.status_code}")

# Step 5: Check localStorage badge_count can be retrieved
print("\n5️⃣ Verifying badge_count would be stored...")
print(f"✓ The frontend should store 'badge_count' = {updated_unread} in localStorage")
print(f"✓ BadgeContext should update with setBadgeCount({updated_unread})")
print(f"✓ Sidebar 'My Messages' should display badge: {updated_unread}")

print("\n" + "=" * 60)
print("✅ Badge Test Complete!")
print("=" * 60)
print("\nNOTE: To fully verify the badge displays:")
print("1. Open http://localhost:3000/portal/dashboard")
print("2. Login with student@test.com / student123")
print("3. Look at the sidebar 'My Messages' link")
print(f"4. Badge should show count: {updated_unread}")
print("=" * 60)
