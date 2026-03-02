#!/usr/bin/env python3
"""Test the new batch mark-read endpoint for students"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

def test_batch_mark_read():
    try:
        # Login as student
        print('1️⃣ Student login...')
        student_login = requests.post(f'{BASE_URL}/auth/login/json', json={'email': 'umar@example.com', 'password': 'student123'}, timeout=5)
        if student_login.status_code != 200:
            print(f'❌ Student login failed: {student_login.text}')
            # Try alternative
            print('   Trying ali@student.com...')
            student_login = requests.post(f'{BASE_URL}/auth/login/json', json={'email': 'ali@student.com', 'password': 'student123'}, timeout=5)
            if student_login.status_code != 200:
                print(f'❌ Ali login also failed: {student_login.text}')
                return False
        
        student_token = student_login.json()['access_token']
        student_id = student_login.json()['user']['id']
        student_email = student_login.json()['user']['email']
        print(f'✅ Student logged in: ID={student_id}, Email={student_email}')

        # Login as admin
        print('\n2️⃣ Admin login...')
        admin_login = requests.post(f'{BASE_URL}/auth/login/json', json={'email': 'admin@masjid.com', 'password': 'admin123'}, timeout=5)
        if admin_login.status_code != 200:
            print(f'❌ Admin login failed: {admin_login.text}')
            return False
        admin_token = admin_login.json()['access_token']
        print(f'✅ Admin logged in')

        # Admin sends message to student
        print('\n3️⃣ Admin sends message to student...')
        send_resp = requests.post(
            f'{BASE_URL}/messages/admin/send-to-student',
            json={'student_id': student_id, 'message': 'Test message from admin for batch test'},
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=5
        )
        if send_resp.status_code != 200:
            print(f'❌ Send failed: {send_resp.text}')
            return False
        print(f'✅ Message sent')

        time.sleep(1)

        # Student gets messages
        print('\n4️⃣ Student fetches messages (should show is_read=False)...')
        get_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        if get_resp.status_code != 200:
            print(f'❌ Fetch failed: {get_resp.text}')
            return False
        messages = get_resp.json()
        unread_count = len([m for m in messages if not m['is_read'] and m['sender_id'] != student_id])
        print(f'✅ Retrieved {len(messages)} messages, {unread_count} unread from admin')

        # Test new batch endpoint
        print('\n5️⃣ Testing new BATCH mark-read endpoint...')
        batch_resp = requests.put(
            f'{BASE_URL}/messages/mark-all-read-from-admin',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        if batch_resp.status_code != 200:
            print(f'❌ Batch endpoint failed: Status {batch_resp.status_code}')
            print(f'   Response: {batch_resp.text}')
            return False
        batch_data = batch_resp.json()
        print(f'✅ Batch endpoint worked! Marked {batch_data["count"]} message(s) as read')

        # Verify messages are now marked as read
        print('\n6️⃣ Verify messages are now marked as read...')
        verify_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        messages = verify_resp.json()
        unread_after = len([m for m in messages if not m['is_read'] and m['sender_id'] != student_id])
        print(f'✅ After batch mark: {unread_after} unread from admin (should be 0)')

        if unread_after == 0:
            print('\n✨ SUCCESS! Batch endpoint test passed!')
            return True
        else:
            print(f'\n❌ FAILED! Still {unread_after} unread messages')
            return False

    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_batch_mark_read()
    exit(0 if success else 1)
