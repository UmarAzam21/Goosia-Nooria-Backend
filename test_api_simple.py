#!/usr/bin/env python3
"""Simple API test"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*60)
print("SIMPLE API TEST")
print("="*60 + "\n")

try:
    # Login student
    print("1. Student login...")
    resp = requests.post(
        f'{BASE_URL}/auth/login/json',
        json={'email': 'ali@student.com', 'password': 'student123'}
    )
    if resp.status_code != 200:
        print(f"   ERROR: {resp.status_code}")
        print(f"   Response: {resp.text}")
    else:
        data = resp.json()
        token = data['access_token']
        student_id = data['user']['id']
        print(f"   OK - Student ID: {student_id}, Token: {token[:20]}...")
        
        # Fetch messages
        print("\n2. Fetching messages...")
        msg_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if msg_resp.status_code != 200:
            print(f"   ERROR: {msg_resp.status_code}")
            print(f"   Response: {msg_resp.text}")
        else:
            messages = msg_resp.json()
            print(f"   OK - Got {len(messages)} messages")
            
            # Show last 3 messages with details
            print("\n3. Last 3 messages:")
            for msg in messages[-3:]:
                sender_id = msg.get('sender_id')
                is_read = msg.get('is_read')
                text = msg.get('message', '')[:50]
                is_from_admin = sender_id != student_id
                print(f"   - sender:{sender_id} admin:{is_from_admin} read:{is_read} | {text}")
            
            # Count unread from admin
            unread = [m for m in messages if not m.get('is_read') and m.get('sender_id') != student_id]
            print(f"\n4. UNREAD MESSAGES (from admin): {len(unread)}")
            if unread:
                print("   ✅ Should show badge!")
                for u in unread:
                    print(f"      ID:{u['id']} text:{u['message'][:40]}")
            else:
                print("   ⚠️ No unread messages to show badge")

except Exception as e:
    print(f"EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")
