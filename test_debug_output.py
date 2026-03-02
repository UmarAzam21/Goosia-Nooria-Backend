#!/usr/bin/env python
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("1. Logging in as admin...")
admin_login = requests.post(
    f'{BASE_URL}/auth/login/json',
    json={'email': 'admin@masjid.com', 'password': 'admin123'},
    timeout=5
)
admin_token = admin_login.json()['access_token']
print(f"   Admin token: {admin_token[:20]}...")

print("\n2. Sending message to student ID 5...")
response = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    json={'student_id': 5, 'message': 'Test debug message'},
    headers={'Authorization': f'Bearer {admin_token}'},
    timeout=5
)
result = response.json()
message_id = result.get('message_id')
print(f"   Response: {result}")
print(f"   Message ID: {message_id}")

# Wait a moment
time.sleep(1)

print("\n3. Checking database for message...")
import sys
sys.path.insert(0, 'c:\\Users\\lenovo\\Desktop\\noori\\backend')
from database import SessionLocal
from models import AdminMessage

db = SessionLocal()
msg = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
if msg:
    print(f"   Message found in DB:")
    print(f"   - ID: {msg.id}")
    print(f"   - is_read: {msg.is_read}")
    print(f"   - Message: {msg.message}")
else:
    print(f"   ERROR: Message {message_id} not found in database!")
db.close()

print("\n4. Test complete!")
