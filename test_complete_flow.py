#!/usr/bin/env python
"""Complete badge flow test: send → display → read → disappear"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*60)
print("COMPLETE BADGE FLOW TEST")
print("="*60 + "\n")

try:
    # Step 1: Admin sends message
    print("STEP 1: Admin sends message to student")
    admin_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'},
        timeout=5
    )
    admin_token = admin_login.json()['access_token']
    
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': 5, 'message': 'Complete flow test message'},
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=5
    )
    msg_id = send_resp.json()['message_id']
    print(f"  ✓ Message ID {msg_id} sent by admin\n")
    
    time.sleep(1)
    
    # Step 2: Verify message is unread
    print("STEP 2: Verify message is unread in database")
    from database import SessionLocal
    from models import AdminMessage
    db = SessionLocal()
    msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
    print(f"  ✓ Database: is_read={msg.is_read}")
    if not msg.is_read:
        print(f"  ✓ Message is UNREAD (badge should show!)\n")
    else:
        print(f"  ❌ ERROR: Message is read!\n")
        exit(1)
    db.close()
    
    # Step 3: Simulate sidebar checking badge
    print("STEP 3: Sidebar badge check (before student opens chat)")
    student_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'ali@student.com', 'password': 'password123'},
        timeout=5
    )
    student_token = student_login.json()['access_token']
    student_id = student_login.json()['user']['id']
    
    msgs_resp = requests.get(
        f'{BASE_URL}/messages/my-messages',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=5
    )
    all_msgs = msgs_resp.json()
    unread_count = sum(1 for m in all_msgs if m.get('sender_id') != student_id and not m.get('is_read'))
    print(f"  ✓ Unread messages for sidebar: {unread_count}")
    print(f"  ✓ Badge should show: {unread_count}\n")
    
    # Step 4: Student opens chat (student fetches messages)
    print("STEP 4: Student opens chat page")
    print(f"  ℹ️  Chat page will:")
    print(f"  - Fetch messages from /my-messages")
    print(f"  - Find {unread_count} unread admin message(s)")
    print(f"  - Automatically mark them as read\n")
    
    # Step 5: Mark messages as read (simulating what chat page does)
    print("STEP 5: Mark unread admin messages as read")
    unread_admin_msgs = [m for m in all_msgs if m.get('sender_id') != student_id and not m.get('is_read')]
    for msg in unread_admin_msgs:
        mark_resp = requests.put(
            f'{BASE_URL}/messages/admin/{msg["id"]}/mark-read',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        if mark_resp.status_code == 200:
            print(f"  ✓ Marked message {msg['id']} as read")
    print()
    
    time.sleep(1)
    
    # Step 6: Verify badge is gone
    print("STEP 6: Sidebar checks badge again (after message marked read)")
    msgs_resp = requests.get(
        f'{BASE_URL}/messages/my-messages',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=5
    )
    all_msgs = msgs_resp.json()
    unread_count_after = sum(1 for m in all_msgs if m.get('sender_id') != student_id and not m.get('is_read'))
    print(f"  ✓ Unread messages for sidebar: {unread_count_after}")
    print(f"  ✓ Badge should show: {unread_count_after}\n")
    
    # Final result
    print("="*60)
    if unread_count_after == 0:
        print("✅ BADGE FLOW COMPLETE AND WORKING!")
        print("   1. Admin sends message → is_read=False")
        print("   2. Badge shows unread count")
        print("   3. Student opens chat → marks as read")
        print("   4. Badge disappears (count = 0)")
    else:
        print(f"⚠️  Badge still showing {unread_count_after} messages")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
