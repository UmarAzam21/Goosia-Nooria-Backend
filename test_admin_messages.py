#!/usr/bin/env python3
"""
Test admin viewing student messages
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Login as admin
print("=" * 80)
print("TESTING ADMIN MESSAGE VIEW")
print("=" * 80)

print("\n1. Logging in as admin...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={"email": "admin@masjid.com", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Admin login successful")

# Get all messages as admin
print("\n2. Fetching all student messages...")
messages_response = requests.get(
    f"{BASE_URL}/api/messages/admin/all",
    headers={"Authorization": f"Bearer {token}"}
)

if messages_response.status_code == 200:
    messages = messages_response.json()
    print(f"✅ ADMIN CAN VIEW STUDENT MESSAGES!")
    print(f"   Total messages: {len(messages)}")
    
    for msg in messages:
        student_name = msg.get("student_name", "Unknown")
        message_text = msg.get("message", "")[:60]
        status = "✅ Responded" if msg.get("is_responded") else "⏳ Waiting"
        print(f"\n📧 From: {student_name}")
        print(f"   Message: {message_text}...")
        print(f"   Status: {status}")
else:
    print(f"❌ Error: {messages_response.text}")
    exit(1)

# Get unread messages
print("\n\n3. Fetching unread messages...")
unread_response = requests.get(
    f"{BASE_URL}/api/messages/admin/unread",
    headers={"Authorization": f"Bearer {token}"}
)

if unread_response.status_code == 200:
    unread = unread_response.json()
    print(f"✅ Unread messages: {len(unread)}")
else:
    print(f"❌ Error: {unread_response.text}")

print("\n" + "=" * 80)
print("✨ ADMIN MESSAGE FEATURE IS WORKING!")
print("=" * 80)
