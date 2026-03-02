#!/usr/bin/env python
"""Test endpoint to trigger debug output"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n=== Testing Admin Message Endpoint ===\n")

try:
    print("1. Admin login...")
    admin_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'},
        timeout=5
    )
    admin_token = admin_login.json()['access_token']
    print("   ✓ Logged in\n")
    
    print("2. Sending message via endpoint...")
    response = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': 5, 'message': 'Badge test message'},
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=5
    )
    result = response.json()
    message_id = result.get('message_id')
    print(f"   ✓ Response: {result}\n")
    
    time.sleep(1)
    
    print(f"3. Checking database for message {message_id}...")
    import sys
    sys.path.insert(0, 'c:\\Users\\lenovo\\Desktop\\noori\\backend')
    from database import SessionLocal
    from models import AdminMessage
    
    db = SessionLocal()
    msg = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    if msg:
        print(f"   ID: {msg.id}")
        print(f"   is_read: {msg.is_read}")
        print(f"   sender_id: {msg.sender_id}")
        print(f"   message: {msg.message}\n")
        
        if msg.is_read == False:
            print("✅ SUCCESS: Message correctly marked as unread!")
        else:
            print(f"❌ FAILED: Message is_read={msg.is_read} (should be False)")
    else:
        print(f"   ❌ Message not found!")
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
