#!/usr/bin/env python3
import requests
import json

BASE_URL = 'http://localhost:5001/api'

print("=" * 70)
print("COMPLETE BADGE TEST - Admin sends message and students see badge")
print("=" * 70)

# Step 1: Admin login
print("\n[1] Admin login...")
admin_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'admin@masjid.com',
    'password': 'admin123'
})

if not admin_login.ok:
    print("   ✗ FAILED")
    exit(1)

admin_token = admin_login.json()['access_token']
print("   ✓ Admin logged in")

# Step 2: Admin sends message to student
print("\n[2] Admin sends message to student ID 5...")
send_resp = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    json={'student_id': 5, 'message': 'Hello student! This is a test message'},
    headers={'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
)

if not send_resp.ok:
    print(f"   ✗ FAILED: {send_resp.status_code}")
    print(f"   {send_resp.text}")
    exit(1)

msg_id = send_resp.json().get('message_id')
print(f"   ✓ Message sent with ID {msg_id}")

# Step 3: Student login
print("\n[3] Student login...")
student_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'ali@student.com',
    'password': 'ali123'
})

if not student_login.ok:
    print("   ✗ FAILED")
    exit(1)

student_token = student_login.json()['access_token']
student_id = 5
print("   ✓ Student logged in")

# Step 4: Student fetches messages
print("\n[4] Student fetches messages...")
messages_resp = requests.get(
    f'{BASE_URL}/messages/my-messages',
    headers={'Authorization': f'Bearer {student_token}'}
)

if not messages_resp.ok:
    print(f"   ✗ FAILED: {messages_resp.status_code}")
    exit(1)

messages = messages_resp.json()
print(f"   ✓ Fetched {len(messages)} messages")

# Step 5: Calculate unread count
print("\n[5] Calculate unread messages...")
unread = [m for m in messages if m.get('sender_id') != student_id and not m.get('is_read')]
print(f"   Total unread from admin: {len(unread)}")

if len(unread) > 0:
    for msg in unread[-3:]:  # Show last 3
        print(f"     - ID {msg['id']}: {msg['message'][:50]}... (is_read={msg['is_read']})")
    print(f"\n   ✓ SUCCESS: Badge should show {len(unread)} unread message(s)")
else:
    print(f"\n   ✗ NO UNREAD MESSAGES - Badge won't show!")
    print("\n   Last 5 messages:")
    for msg in messages[-5:]:
        print(f"     - ID {msg['id']}: sender_id={msg['sender_id']}, is_read={msg['is_read']}")

print("\n" + "=" * 70)
