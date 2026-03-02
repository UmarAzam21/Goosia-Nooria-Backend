#!/usr/bin/env python3
"""Test sending and receiving a message"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*70)
print("TEST: SEND MESSAGE AND CHECK UNREAD")
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
    msg_text = f"NEW TEST [{int(time.time())}]"
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': student_id, 'message': msg_text},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if send_resp.status_code != 200:
        print(f"   ❌ ERROR {send_resp.status_code}: {send_resp.text}\n")
    else:
        sent_msg = send_resp.json()
        msg_id = sent_msg['id']
        is_read = sent_msg.get('is_read', 'NOT_SET')
        print(f"   ✅ Message sent!")
        print(f"      ID: {msg_id}")
        print(f"      is_read in response: {is_read}\n")
        
        # STUDENT IMMEDIATELY FETCHES
        print("4️⃣  Student fetches messages (immediately)...")
        fetch_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        messages = fetch_resp.json()
        print(f"   ✅ Got {len(messages)} total messages\n")
        
        # FIND THE NEWLY SENT MESSAGE
        print("5️⃣  Looking for the newly sent message...")
        found = False
        for msg in messages:
            if msg['id'] == msg_id:
                found = True
                print(f"   ✅ FOUND IT!")
                print(f"      ID: {msg['id']}")
                print(f"      is_read in DB: {msg['is_read']}")
                print(f"      sender_id: {msg['sender_id']}")
                print(f"      message: {msg['message']}\n")
                
                if not msg['is_read']:
                    print(f"   🎉 Message is UNREAD in database!")
                    print(f"   🔴 BADGE SHOULD SHOW!\n")
                else:
                    print(f"   ⚠️ Message is ALREADY READ in database!")
                    print(f"   😞 Badge will NOT show\n")
                break
        
        if not found:
            print(f"   ❌ Message ID {msg_id} not found in student's messages!\n")
        
        # COUNT ALL UNREAD FROM ADMIN
        print("6️⃣  Count all unread messages from admin...")
        unread = [m for m in messages if not m['is_read'] and m['sender_id'] != student_id]
        print(f"   Total unread from admin: {len(unread)}\n")
        
        if unread:
            print("   🔴 Unread messages:")
            for u in unread[:3]:
                print(f"      - ID:{u['id']} | {u['message'][:50]}")

except Exception as e:
    print(f"❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
