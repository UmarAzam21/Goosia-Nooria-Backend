#!/usr/bin/env python
"""Test the badge - verify API returns correct unread count"""
import requests

BASE_URL = 'http://localhost:5001/api'

print("\n=== Testing Badge Functionality ===\n")

try:
    # Get student auth token
    print("1. Authenticating as student (ali@student.com)...")
    student_login = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'ali@student.com', 'password': 'password123'},
        timeout=5
    )
    
    if student_login.status_code != 200:
        print(f"   Error: {student_login.status_code}")
        print(f"   {student_login.json()}")
    else:
        student_token = student_login.json().get('access_token')
        user_data = student_login.json().get('user')
        student_id = user_data.get('id')
        print(f"   ✓ Logged in as student ID {student_id}\n")
    
    # Get messages via the endpoint the badge uses
    print("2. Fetching messages from /my-messages endpoint...")
    response = requests.get(
        f'{BASE_URL}/messages/my-messages',
        headers={'Authorization': f'Bearer {student_token}'},
        timeout=5
    )
    
    if response.status_code == 200:
        all_messages = response.json()
        print(f"   ✓ Total messages: {len(all_messages)}\n")
        
        # Calculate unread count (same logic as sidebar)
        unread_count = sum(1 for msg in all_messages if msg.get('sender_id') != student_id and not msg.get('is_read'))
        
        print(f"3. Badge calculation:")
        print(f"   - Total messages: {len(all_messages)}")
        print(f"   - Unread messages (sender_id != {student_id} AND is_read=False): {unread_count}\n")
        
        # Show the unread messages
        if unread_count > 0:
            print(f"   Unread messages:")
            for msg in all_messages:
                if msg.get('sender_id') != student_id and not msg.get('is_read'):
                    print(f"     - ID {msg['id']}: '{msg['message'][:50]}...' (from ID {msg['sender_id']})")
        
        if unread_count > 0:
            print(f"\n✅ SUCCESS: Badge should display '{unread_count}' on sidebar!")
        else:
            print(f"\n⚠️  WARNING: No unread messages found. Badge will not display.")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.json()}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
