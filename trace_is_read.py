#!/usr/bin/env python3
import requests
from database import SessionLocal
from models import AdminMessage
from sqlalchemy import text

BASE_URL = 'http://localhost:5001/api'

print("="*70)
print("DETAILED TRACE: Where are admin messages being marked as read?")
print("="*70)

# Step 1: Check DB before any action
print("\n[Step 1] Current DB state for admin messages:")
db = SessionLocal()
count_unread = db.query(AdminMessage).filter(AdminMessage.sender_id == 1, AdminMessage.is_read == False).count()
count_read = db.query(AdminMessage).filter(AdminMessage.sender_id == 1, AdminMessage.is_read == True).count()
print(f"  Admin messages: {count_unread} unread, {count_read} read")
db.close()

# Step 2: Admin sends a message
print("\n[Step 2] Admin sends new message...")
admin_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'admin@masjid.com',
    'password': 'admin123'
})
admin_token = admin_login.json()['access_token']

send_resp = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    json={'student_id': 5, 'message': 'Trace test message'},
    headers={'Authorization': f'Bearer {admin_token}'}
)
msg_id = send_resp.json()['message_id']
print(f"  Sent message ID {msg_id}")

# Step 3: Check DB immediately after send
print(f"\n[Step 3] Check DB immediately after send (before any API calls)...")
db = SessionLocal()
msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
print(f"  Message {msg_id} is_read={msg.is_read}")
db.close()

# Step 4: Check via API
print(f"\n[Step 4] Fetch message via API (student)...")
student_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'ali@student.com',
    'password': 'ali123'
})
student_token = student_login.json()['access_token']

messages_resp = requests.get(
    f'{BASE_URL}/messages/my-messages',
    headers={'Authorization': f'Bearer {student_token}'}
)
messages = messages_resp.json()
api_msg = next((m for m in messages if m['id'] == msg_id), None)
if api_msg:
    print(f"  API says message {msg_id} is_read={api_msg['is_read']}")
else:
    print(f"  Message {msg_id} not found in API response!")

# Step 5: Check DB final state
print(f"\n[Step 5] Final DB check...")
db = SessionLocal()
msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
print(f"  Message {msg_id} is_read={msg.is_read}")
db.close()

print("\n" + "="*70)
