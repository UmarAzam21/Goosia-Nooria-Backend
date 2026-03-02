"""
Test messaging storage - verify messages are being saved to database
"""
import sys
import json
import base64
from datetime import datetime

# Test Database Connection
print("\n" + "="*80)
print("1. TESTING DATABASE CONNECTION")
print("="*80)

try:
    from database import SessionLocal, engine
    from models import AdminMessage, User, Base
    
    db = SessionLocal()
    
    # Verify table exists
    print("✓ Database connected")
    
    # Check existing messages
    all_messages = db.query(AdminMessage).all()
    print(f"✓ Found {len(all_messages)} existing messages in database")
    
    if all_messages:
        print("\nExisting messages:")
        for msg in all_messages:
            print(f"  - ID: {msg.id}, Student: {msg.student_name}, Message: {msg.message[:50]}..., Response: {msg.response is not None}")
    
    db.close()
    
except Exception as e:
    print(f"✗ Database error: {e}")
    sys.exit(1)

# Test 2: Verify Backend is Running
print("\n" + "="*80)
print("2. TESTING BACKEND API CONNECTION")
print("="*80)

import requests
import subprocess
import time

API_URL = "http://localhost:5000/api"

# Check if server is running
try:
    response = requests.get(f"{API_URL}/health", timeout=2)
    print(f"✓ Backend responding at {API_URL}")
except:
    print(f"✗ Backend not responding at {API_URL}")
    print("\nStarting backend server...")
    # Start backend in background
    # subprocess.Popen(['python', 'main.py'], cwd='.', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # time.sleep(3)

# Test 3: Create a test student and send message
print("\n" + "="*80)
print("3. TESTING MESSAGE SEND ENDPOINT")
print("="*80)

# First, get a valid student token
db = SessionLocal()

# Check if test student exists
test_student = db.query(User).filter(User.email == "ali@student.com").first()

if not test_student:
    print("✗ Test student not found. Please create a student account first.")
    db.close()
    sys.exit(1)

print(f"✓ Found test student: {test_student.email}")

db.close()

# Simulate login to get token
print("\nAttempting login...")
login_response = requests.post(
    f"{API_URL}/auth/login/json",
    json={"email": "ali@student.com", "password": "ali123"}
)

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    print(f"✓ Login successful, got token: {token[:20]}...")
else:
    print(f"✗ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    sys.exit(1)

# Test 4: Send a message
print("\n" + "="*80)
print("4. SENDING TEST MESSAGE TO ADMIN")
print("="*80)

message_data = {
    "student_name": "Ali Student",
    "message": f"Test message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

send_response = requests.post(
    f"{API_URL}/messages/send-to-admin",
    json=message_data,
    headers=headers
)

print(f"Response Status: {send_response.status_code}")
print(f"Response Body: {send_response.text}")

if send_response.status_code == 200:
    response_data = send_response.json()
    print(f"✓ Message sent successfully!")
    print(f"  Message ID: {response_data.get('message_id')}")
    print(f"  Message: {response_data.get('message')}")
else:
    print(f"✗ Failed to send message")
    sys.exit(1)

# Test 5: Verify message was saved to database
print("\n" + "="*80)
print("5. VERIFYING MESSAGE IN DATABASE")
print("="*80)

db = SessionLocal()
time.sleep(1)  # Give database time to save

all_messages = db.query(AdminMessage).all()
print(f"Total messages in database: {len(all_messages)}")

if all_messages:
    latest_msg = all_messages[-1]
    print(f"\n✓ Latest message found:")
    print(f"  ID: {latest_msg.id}")
    print(f"  Student: {latest_msg.student_name}")
    print(f"  Message: {latest_msg.message}")
    print(f"  Created: {latest_msg.created_at}")
    print(f"  Is Read: {latest_msg.is_read}")
    print(f"  Is Responded: {latest_msg.is_responded}")
else:
    print("✗ No messages found in database!")

db.close()

# Test 6: Query API to get messages
print("\n" + "="*80)
print("6. TESTING GET MESSAGES ENDPOINT")
print("="*80)

get_response = requests.get(
    f"{API_URL}/messages/my-messages",
    headers=headers
)

if get_response.status_code == 200:
    messages = get_response.json()
    print(f"✓ Retrieved {len(messages)} messages from API")
    for msg in messages:
        print(f"  - {msg['student_name']}: {msg['message'][:50]}...")
else:
    print(f"✗ Failed to get messages: {get_response.status_code}")
    print(f"   {get_response.text}")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
