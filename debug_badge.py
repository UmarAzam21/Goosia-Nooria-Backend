#!/usr/bin/env python
"""
COMPREHENSIVE BADGE DEBUG TEST - STEP BY STEP
"""
import requests

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*70)
print("BADGE SYSTEM - COMPREHENSIVE DEBUG TEST")
print("="*70 + "\n")

try:
    # STEP 1: Clean up old messages
    print("STEP 1: Clean up database")
    print("-" * 70)
    from database import SessionLocal
    from models import AdminMessage, User
    db = SessionLocal()
    count = db.query(AdminMessage).delete()
    db.commit()
    print(f"✓ Database cleaned - deleted {count} old messages\n")
    db.close()
    
    # STEP 2: Admin login
    print("STEP 2: Admin login")
    print("-" * 70)
    admin_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'},
        timeout=5
    )
    admin_token = admin_login.json()['access_token']
    print(f"✓ Admin authenticated\n")
    
    # STEP 3: Admin sends message
    print("STEP 3: Admin sends message to student ID 5")
    print("-" * 70)
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': 5, 'message': 'Hello! This is a badge test message'},
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=5
    )
    msg_id = send_resp.json()['message_id']
    print(f"✓ Message sent via API")
    print(f"  - Message ID: {msg_id}")
    print(f"  - Content: 'Hello! This is a badge test message'\n")
    
    # STEP 4: Check database - verify is_read=False
    print("STEP 4: Check database - verify is_read status")
    print("-" * 70)
    db = SessionLocal()
    msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
    print(f"✓ Message in database:")
    print(f"  - ID: {msg.id}")
    print(f"  - student_id: {msg.student_id}")
    print(f"  - sender_id: {msg.sender_id} (1=admin)")
    print(f"  - is_read: {msg.is_read}")
    
    if msg.is_read:
        print(f"\n❌ PROBLEM: is_read={msg.is_read} (should be False)\n")
    else:
        print(f"✅ CORRECT: is_read=False - badge will show\n")
    
    # STEP 5: Get student info
    print("STEP 5: Get student info")
    print("-" * 70)
    student = db.query(User).filter(User.id == 5).first()
    student_id = student.id
    print(f"✓ Student ID 5:")
    print(f"  - Email: {student.email}")
    print(f"  - Name: {student.name}\n")
    
    # STEP 6: Simulate API response - what /messages/my-messages returns
    print("STEP 6: Simulate /messages/my-messages response")
    print("-" * 70)
    all_msgs = db.query(AdminMessage).filter(
        AdminMessage.student_id == student_id
    ).order_by(AdminMessage.created_at).all()
    
    print(f"✓ API would return {len(all_msgs)} message(s):\n")
    
    for i, m in enumerate(all_msgs, 1):
        print(f"  Message {i}:")
        print(f"    - id: {m.id}")
        print(f"    - sender_id: {m.sender_id}")
        print(f"    - is_read: {m.is_read}")
        print(f"    - message: '{m.message}'")
    
    # STEP 7: Calculate unread count (sidebar logic)
    print("\nSTEP 7: Badge calculation (frontend logic)")
    print("-" * 70)
    print(f"✓ Frontend receives messages, calculates unread:")
    print(f"  - Filter: sender_id !== {student_id} AND is_read === false")
    
    unread_count = sum(1 for m in all_msgs if m.sender_id != student_id and not m.is_read)
    
    for m in all_msgs:
        from_admin = m.sender_id != student_id
        is_unread = not m.is_read
        matches = from_admin and is_unread
        status = "✓ COUNTS" if matches else "✗ ignored"
        print(f"    - ID {m.id}: sender_id={m.sender_id}, is_read={m.is_read} {status}")
    
    print(f"\n  Total unread messages: {unread_count}\n")
    
    # FINAL RESULT
    print("="*70)
    if unread_count > 0:
        print(f"✅ BADGE WILL SHOW: {unread_count} unread message(s)")
        print(f"\nThe sidebar badge will display the number: {unread_count}")
    else:
        print(f"❌ BADGE WILL NOT SHOW: 0 unread messages")
    print("="*70 + "\n")
    
    db.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
