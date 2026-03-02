#!/usr/bin/env python3
"""Complete test: Send and check message"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*70)
print("COMPLETE TEST: Send Message & Check Badge")
print("="*70 + "\n")

try:
    # Admin login
    print("1️⃣  Admin login...")
    admin_resp = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'}
    )
    admin_token = admin_resp.json()['access_token']
    admin_id = admin_resp.json()['user']['id']
    print(f"   ✅ Admin ID: {admin_id}\n")
    
    # Student login
    print("2️⃣  Student login...")
    student_resp = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'ali@student.com', 'password': 'student123'}
    )
    student_token = student_resp.json()['access_token']
    student_id = student_resp.json()['user']['id']
    print(f"   ✅ Student ID: {student_id}\n")
    
    # SEND NEW MESSAGE
    print("3️⃣  Admin sends NEW message...")
    msg_text = f"TEST BADGE {int(time.time())}"
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': student_id, 'message': msg_text},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if send_resp.status_code != 200:
        print(f"   ❌ ERROR {send_resp.status_code}\n")
    else:
        send_data = send_resp.json()
        msg_id = send_data['message_id']
        print(f"   ✅ Message sent (ID: {msg_id})\n")
        
        # STUDENT FETCHES MESSAGES
        print("4️⃣  Student fetches messages...")
        fetch_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        messages = fetch_resp.json()
        
        # FIND THE NEWLY SENT MESSAGE
        print("5️⃣  Looking for newly sent message...")
        found_msg = None
        for msg in messages:
            if msg['id'] == msg_id:
                found_msg = msg
                break
        
        if found_msg:
            print(f"   ✅ FOUND!")
            print(f"      ID: {found_msg['id']}")
            print(f"      is_read: {found_msg['is_read']}")
            print(f"      sender_id: {found_msg['sender_id']}")
            print(f"      Text: {found_msg['message']}\n")
            
            if not found_msg['is_read'] and found_msg['sender_id'] != student_id:
                print("   🎉 ✅ UNREAD from ADMIN = BADGE SHOULD SHOW!\n")
            else:
                print("   ⚠️ Message is read or from student\n")
        else:
            print(f"   ❌ Message ID {msg_id} not found!\n")
        
        # COUNT UNREAD FROM ADMIN
        print("6️⃣  Checking total unread from admin...")
        unread = [m for m in messages if not m['is_read'] and m['sender_id'] != student_id]
        print(f"   Total unread: {len(unread)}")
        if unread:
            print(f"   🔴 BADGE COUNT SHOULD BE: {len(unread)}\n")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("="*70 + "\n")
