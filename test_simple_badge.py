#!/usr/bin/env python3
"""Simple test to debug the badge issue"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("🧪 Testing Unread Badge Functionality\n")

try:
    # 1. Admin login
    print("1️⃣ Admin LOGIN...")
    admin_resp = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'admin@masjid.com', 'password': 'admin123'},
        timeout=3
    )
    print(f"   Status: {admin_resp.status_code}")
    if admin_resp.status_code != 200:
        print(f"   ERROR: {admin_resp.text}")
        exit(1)
    
    admin_data = admin_resp.json()
    admin_token = admin_data['access_token']
    print(f"   ✅ Token: {admin_token[:20]}...")

    # 2. Get student
    print("\n2️⃣ Student LOGIN...")
    student_resp = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'ali@student.com', 'password': 'student123'},
        timeout=3
    )
    print(f"   Status: {student_resp.status_code}")
    if student_resp.status_code != 200:
        print(f"   ERROR: {student_resp.text}")
        exit(1)
    
    student_data = student_resp.json()
    student_token = student_data['access_token']
    student_id = student_data['user']['id']
    print(f"   ✅ Student ID: {student_id}")

    # 3. Send message
    print("\n3️⃣ Admin SENDS MESSAGE to student...")
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': student_id, 'message': 'Test badge message'},
        headers={'Authorization': f'Bearer {admin_token}'},
        timeout=3
    )
    print(f"   Status: {send_resp.status_code}")
    if send_resp.status_code != 200:
        print(f"   ERROR: {send_resp.text}")
        exit(1)
    
    msg_id = send_resp.json()['message_id']
    print(f"   ✅ Message ID: {msg_id}")

    # 4. Student fetches messages
    print("\n4️⃣ Student GETS MESSAGES...")
    fetch_resp = requests.get(
        f'{BASE_URL}/messages/my-messages',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=3
    )
    print(f"   Status: {fetch_resp.status_code}")
    if fetch_resp.status_code != 200:
        print(f"   ERROR: {fetch_resp.text}")
        exit(1)
    
    messages = fetch_resp.json()
    print(f"   ✅ Total messages: {len(messages)}")
    
    # Find our test message
    test_msg = next((m for m in messages if m['id'] == msg_id), None)
    if test_msg:
        print(f"   ✅ Found test message:")
        print(f"       - is_read: {test_msg['is_read']} (should be False)")
        print(f"       - sender_id: {test_msg['sender_id']} (should be 1)")
    else:
        print(f"   ⚠️  Test message not found")

    # 5. Count unread
    print("\n5️⃣ Count UNREAD messages...")
    unread = len([m for m in messages if not m['is_read'] and m['sender_id'] != student_id])
    print(f"   Unread from admin: {unread}")
    if unread > 0:
        print(f"   ✅ BADGE SHOULD SHOW: {unread}")
    else:
        print(f"   ⚠️  No unread messages - badge won't show")

    # 6. Test batch endpoint
    print("\n6️⃣ Test BATCH mark-read endpoint...")
    batch_resp = requests.put(
        f'{BASE_URL}/messages/mark-all-read-from-admin',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=3
    )
    print(f"   Status: {batch_resp.status_code}")
    if batch_resp.status_code != 200:
        print(f"   ERROR: {batch_resp.text}")
        exit(1)
    
    batch_data = batch_resp.json()
    print(f"   ✅ Marked {batch_data['count']} message(s) as read")

    # 7. Verify marked as read
    print("\n7️⃣ Verify MESSAGES marked as read...")
    verify_resp = requests.get(
        f'{BASE_URL}/messages/my-messages',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=3
    )
    messages = verify_resp.json()
    unread_after = len([m for m in messages if not m['is_read'] and m['sender_id'] != student_id])
    print(f"   Unread after batch: {unread_after} (should be 0)")
    
    if unread_after == 0:
        print(f"\n✅ SUCCESS! All tests passed!")
    else:
        print(f"\n❌ FAILED! Still have {unread_after} unread messages")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
