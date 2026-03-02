#!/usr/bin/env python
"""Final badge test - send message and verify it's unread, then check badge"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n=== Final Badge Test ===\n")

try:
    # Step 1: Admin sends a message
    print("Step 1: Admin sends message to student 5...")
    admin_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'},
        timeout=5
    )
    admin_token = admin_login.json()['access_token']
    
    send_response = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': 5, 'message': 'Test badge message!'},
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=5
    )
    result = send_response.json()
    msg_id = result.get('message_id')
    print(f"   ✓ Message sent with ID {msg_id}\n")
    
    time.sleep(1)
    
    # Step 2: Verify message is in database as unread
    print("Step 2: Verify message in database...")
    from database import SessionLocal
    from models import AdminMessage
    db = SessionLocal()
    msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
    print(f"   - Message ID: {msg.id}")
    print(f"   - is_read: {msg.is_read}")
    print(f"   - Message: {msg.message}\n")
    
    if msg.is_read:
        print("   ❌ ERROR: Message marked as read in database!")
    else:
        print("   ✓ Message is UNREAD in database\n")
    db.close()
    
    # Step 3: Check sidebar badge via API
    print("Step 3: Testing sidebar badge (using admin account)...")
    all_msgs_response = requests.get(
        f'{BASE_URL}/messages/admin/all',
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=5
    )
    all_messages = all_msgs_response.json()
    
    # Filter for messages sent to student 5 that are unread (not responded to by admin yet)
    student_5_unread = [m for m in all_messages if m['student_id'] == 5 and not m['is_read']]
    
    print(f"   - All admin messages: {len(all_messages)}")
    print(f"   - Messages from student 5: {sum(1 for m in all_messages if m['student_id'] == 5)}")
    print(f"   - Unread from student 5: {len(student_5_unread)}\n")
    
    if len(student_5_unread) > 0:
        print(f"✅ SUCCESS! Badge should show {len(student_5_unread)} unread message(s)\n")
        print("Badge-related details")
        for msg in student_5_unread:
            print(f"  - ID {msg['id']}: is_read={msg['is_read']}, sender_id={msg['sender_id']}")
    else:
        print("⚠️  No unread messages found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
