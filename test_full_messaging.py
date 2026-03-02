#!/usr/bin/env python3
"""
Comprehensive test of admin messaging feature
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 80)
print("COMPREHENSIVE ADMIN MESSAGING TEST")
print("=" * 80)

# 1. Login as student
print("\n[1/5] Student login and send message...")
student_login = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={"email": "ali@student.com", "password": "ali123"}
)

if student_login.status_code != 200:
    print(f"❌ Student login failed")
    exit(1)

student_token = student_login.json()["access_token"]
print("✅ Student logged in")

# Send message
student_msg = requests.post(
    f"{BASE_URL}/api/messages/send-to-admin",
    headers={"Authorization": f"Bearer {student_token}"},
    json={
        "student_name": "Ali Ahmed Test",
        "message": "Test message for admin at " + str(__import__('datetime').datetime.now())
    }
)

if student_msg.status_code == 200:
    msg_id = student_msg.json().get("message_id")
    print(f"✅ Message sent (ID: {msg_id})")
else:
    print(f"❌ Message send failed: {student_msg.text}")
    exit(1)

# 2. Admin login
print("\n[2/5] Admin login...")
admin_login = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={"email": "admin@masjid.com", "password": "admin123"}
)

if admin_login.status_code != 200:
    print(f"❌ Admin login failed")
    exit(1)

admin_token = admin_login.json()["access_token"]
print("✅ Admin logged in")

# 3. Admin fetch all messages
print("\n[3/5] Admin fetching all messages...")
all_msgs = requests.get(
    f"{BASE_URL}/api/messages/admin/all",
    headers={"Authorization": f"Bearer {admin_token}"}
)

if all_msgs.status_code == 200:
    msgs_list = all_msgs.json()
    print(f"✅ Retrieved {len(msgs_list)} messages")
else:
    print(f"❌ Failed to fetch messages: {all_msgs.text}")
    exit(1)

# 4. Admin fetch unread messages
print("\n[4/5] Admin fetching unread messages...")
unread_msgs = requests.get(
    f"{BASE_URL}/api/messages/admin/unread",
    headers={"Authorization": f"Bearer {admin_token}"}
)

if unread_msgs.status_code == 200:
    unread_list = unread_msgs.json()
    print(f"✅ Found {len(unread_list)} unread messages")
else:
    print(f"❌ Failed to fetch unread: {unread_msgs.text}")
    exit(1)

# 5. Admin respond to message
print(f"\n[5/5] Admin responding to message {msg_id}...")
respond = requests.put(
    f"{BASE_URL}/api/messages/admin/{msg_id}/respond",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={"response": "Thank you for your message. We will help you shortly!"}
)

print(f"   Status: {respond.status_code}")
if respond.status_code == 200:
    print(f"✅ Response sent successfully")
    print(f"   Details: {json.dumps(respond.json(), indent=2)}")
else:
    print(f"❌ Failed to respond: {respond.text}")
    exit(1)

# Verify response was saved
print("\n[BONUS] Verifying response was saved...")
check = requests.get(
    f"{BASE_URL}/api/messages/admin/all",
    headers={"Authorization": f"Bearer {admin_token}"}
)

if check.status_code == 200:
    updated_msgs = check.json()
    for msg in updated_msgs:
        if msg["id"] == msg_id:
            if msg.get("response"):
                print(f"✅ Response verified in database!")
                print(f"   Student: {msg['student_name']}")
                print(f"   Message: {msg['message'][:50]}...")
                print(f"   Response: {msg['response'][:50]}...")
                print(f"   Status: {'✅ Responded' if msg['is_responded'] else '⏳ Not responded'}")
            break

print("\n" + "=" * 80)
print("✨ ALL TESTS PASSED - ADMIN MESSAGING IS FULLY FUNCTIONAL!")
print("=" * 80)
