import requests
import json

BASE_URL = 'http://localhost:5001/api'

# Login
login_resp = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'admin@masjid.com',
    'password': 'admin123'
})
token = login_resp.json().get('access_token')

# Fetch all messages
headers = {'Authorization': f'Bearer {token}'}
messages_resp = requests.get(f'{BASE_URL}/messages/admin/all', headers=headers)
messages = messages_resp.json()

print('Messages fetched from API:')
print(f'Total: {len(messages)}')
print('\nLast 10 messages:')
print('-' * 80)
for msg in messages[-10:]:
    sender = str(msg.get('sender_id')) if msg.get('sender_id') else 'NONE'
    student = msg.get('student_id')
    text = msg.get('message', '')[:30]
    print(f'ID:{msg.get("id"):2d} | Student:{student:2d} | Sender:{sender:5s} | {text}')
print('-' * 80)
print('\nKeys in message object:')
if messages:
    print(list(messages[0].keys()))
