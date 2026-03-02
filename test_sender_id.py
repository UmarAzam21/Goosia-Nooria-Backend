import requests
import json
from database import SessionLocal
from models import AdminMessage

BASE_URL = 'http://localhost:5001/api'
admin_email = 'admin@masjid.com'
admin_password = 'admin123'

print('=' * 70)
print('TESTING ADMIN MESSAGE ENDPOINT WITH SENDER_ID')
print('=' * 70)

# Step 1: Login
print('\n1. Logging in as admin...')
login_resp = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': admin_email,
    'password': admin_password
})
print(f'   Status: {login_resp.status_code}')
if not login_resp.ok:
    print(f'   Error: {login_resp.text}')
    exit(1)

token = login_resp.json().get('access_token')
user_data = login_resp.json().get('user')
admin_id = user_data.get('id')
print(f'   Admin ID: {admin_id}')
print(f'   Token: {token[:30]}...')

# Step 2: Send message
print(f'\n2. Sending message to student ID 5...')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
message_data = {'student_id': 5, 'message': f'TEST MESSAGE - Admin ID {admin_id}'}
send_resp = requests.post(f'{BASE_URL}/messages/admin/send-to-student', json=message_data, headers=headers)
print(f'   Status: {send_resp.status_code}')

if send_resp.ok:
    msg_id = send_resp.json().get('message_id')
    print(f'   Message created with ID: {msg_id}')
    
    # Step 3: Check database
    print(f'\n3. Checking message in database...')
    db = SessionLocal()
    msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
    if msg:
        print(f'   Message ID: {msg.id}')
        print(f'   Student ID: {msg.student_id}')
        print(f'   Sender ID: {msg.sender_id}')
        print(f'   Message: {msg.message[:50]}')
        if msg.sender_id == admin_id:
            print(f'   ✓ SENDER_ID CORRECTLY SET!')
        else:
            print(f'   ✗ SENDER_ID INCORRECT! Expected {admin_id}, got {msg.sender_id}')
    db.close()
else:
    print(f'   Error: {send_resp.text}')

print('\n' + '=' * 70)
