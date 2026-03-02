#!/usr/bin/env python3
"""Test that unread messages show badge in student sidebar"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

def test_unread_badge_display():
    try:
        # Setup: Get admin and student users
        print('=== Testing Unread Badge Display ===\n')
        
        # Login as admin
        print('1️⃣ Admin login...')
        admin_login = requests.post(
            f'{BASE_URL}/auth/login/json',
            json={'email': 'admin@masjid.com', 'password': 'admin123'},
            timeout=5
        )
        if admin_login.status_code != 200:
            print(f'❌ Admin login failed')
            return False
        admin_token = admin_login.json()['access_token']
        print(f'✅ Admin logged in')

        # Login as student
        print('\n2️⃣ Student login...')
        student_login = requests.post(
            f'{BASE_URL}/auth/login/json',
            json={'email': 'ali@student.com', 'password': 'student123'},
            timeout=5
        )
        if student_login.status_code != 200:
            print(f'❌ Student login failed: {student_login.text}')
            return False
        student_token = student_login.json()['access_token']
        student_id = student_login.json()['user']['id']
        print(f'✅ Student logged in (ID={student_id})')

        # Get initial message count (before admin sends)
        print('\n3️⃣ Get initial student messages...')
        initial_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        initial_messages = initial_resp.json() if initial_resp.status_code == 200 else []
        initial_unread = len([m for m in initial_messages if not m['is_read'] and m['sender_id'] != student_id])
        print(f'✅ Initial unread from admin: {initial_unread}')

        # Admin sends a message to student
        print('\n4️⃣ Admin sends message to student...')
        send_resp = requests.post(
            f'{BASE_URL}/messages/admin/send-to-student',
            json={'student_id': student_id, 'message': '🎉 Badge Test Message - Should Show in Sidebar!'},
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=5
        )
        if send_resp.status_code != 200:
            print(f'❌ Send message failed: {send_resp.text}')
            return False
        msg_id = send_resp.json()['message_id']
        print(f'✅ Message sent (ID={msg_id})')

        # Verify message is_read=False
        print('\n5️⃣ Verify message is_read=False in database...')
        time.sleep(0.5)
        fetch_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'},
            timeout=5
        )
        messages = fetch_resp.json()
        new_msg = next((m for m in messages if m['id'] == msg_id), None)
        if not new_msg:
            print(f'❌ Sent message not found in student messages!')
            return False
        
        print(f'✅ Message found:')
        print(f'   - is_read: {new_msg["is_read"]} (should be False)')
        print(f'   - sender_id: {new_msg["sender_id"]} (admin_id=1)')
        
        if new_msg['is_read']:
            print(f'❌ ERROR: Message is already marked as read!')
            return False

        # Count unread from admin
        print('\n6️⃣ Count unread messages from admin...')
        unread_count = len([m for m in messages if not m['is_read'] and m['sender_id'] != student_id])
        print(f'✅ Unread from admin: {unread_count}')
        print(f'   Should be displayed in sidebar badge!')

        if unread_count > initial_unread:
            print(f'\n✨ SUCCESS! Badge count increased from {initial_unread} to {unread_count}')
            print(f'   The sidebar should now show badge: {unread_count}')
            return True
        else:
            print(f'\n❌ FAILED! Badge count did not increase')
            return False

    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unread_badge_display()
    exit(0 if success else 1)
