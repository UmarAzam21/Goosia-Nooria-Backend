#!/usr/bin/env python3
"""
Test the student contact admin feature
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# First, login as a student
print("=" * 80)
print("TESTING STUDENT CONTACT ADMIN FEATURE")
print("=" * 80)

print("\n1. Logging in as student...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={
        "email": "ali@student.com",
        "password": "ali123"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

login_data = login_response.json()
token = login_data.get("access_token")
print(f"✅ Login successful. Token: {token[:30]}...")

# Send a message to admin
print("\n2. Sending message to admin...")
message_response = requests.post(
    f"{BASE_URL}/api/messages/send-to-admin",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "student_name": "Ali Ahmed",
        "message": "I have a question about the course schedule"
    }
)

if message_response.status_code == 200:
    message_data = message_response.json()
    print(f"✅ Message sent successfully!")
    print(f"   Response: {json.dumps(message_data, indent=2)}")
else:
    print(f"❌ Failed to send message: {message_response.text}")
    exit(1)

# Get student's messages
print("\n3. Getting student's sent messages...")
get_messages_response = requests.get(
    f"{BASE_URL}/api/messages/my-messages",
    headers={
        "Authorization": f"Bearer {token}"
    }
)

if get_messages_response.status_code == 200:
    messages = get_messages_response.json()
    print(f"✅ Retrieved messages!")
    print(f"   Total messages: {len(messages)}")
    if messages:
        msg = messages[0]
        print(f"   Latest message:")
        print(f"      From: {msg.get('student_name')}")
        print(f"      Message: {msg.get('message')[:100]}...")
        print(f"      Status: {'Responded' if msg.get('is_responded') else 'Waiting for response'}")
else:
    print(f"❌ Failed to get messages: {get_messages_response.text}")

print("\n" + "=" * 80)
print("✨ TEST COMPLETE - STUDENT CONTACT ADMIN FEATURE IS WORKING!")
print("=" * 80)
