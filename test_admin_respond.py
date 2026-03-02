#!/usr/bin/env python3
"""
Test admin responding to student message
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 80)
print("TESTING ADMIN RESPOND TO MESSAGE")
print("=" * 80)

# Login as admin
print("\n1. Logging in as admin...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={"email": "admin@masjid.com", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print("✅ Admin login successful")

# Get all messages
print("\n2. Fetching messages...")
messages_response = requests.get(
    f"{BASE_URL}/api/messages/admin/all",
    headers={"Authorization": f"Bearer {token}"}
)

if messages_response.status_code != 200:
    print(f"❌ Failed to fetch messages")
    exit(1)

messages = messages_response.json()
if not messages:
    print("❌ No messages found")
    exit(1)

# Get first message
message_id = messages[0]["id"]
print(f"✅ Found {len(messages)} messages")
print(f"   Testing with message ID: {message_id}")

# Try to respond
print(f"\n3. Attempting to respond to message {message_id}...")
response_request = requests.put(
    f"{BASE_URL}/api/messages/admin/{message_id}/respond",
    headers={"Authorization": f"Bearer {token}"},
    json={"response": "Thank you for contacting us. We will help you soon!"}
)

print(f"   Status Code: {response_request.status_code}")
print(f"   Response: {response_request.text}")

if response_request.status_code == 200:
    print(f"\n✅ RESPONSE SENT SUCCESSFULLY!")
    data = response_request.json()
    print(f"   Message: {data.get('message')}")
else:
    print(f"\n❌ FAILED TO SEND RESPONSE")
    try:
        error_data = response_request.json()
        print(f"   Error Details: {json.dumps(error_data, indent=2)}")
    except:
        print(f"   Raw Response: {response_request.text}")

print("\n" + "=" * 80)
