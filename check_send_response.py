#!/usr/bin/env python3
"""Check what the send endpoint returns"""
import requests
import json
import time

BASE_URL = 'http://localhost:5001/api'

# Admin login
admin_resp = requests.post(
    f'{BASE_URL}/auth/login/json',
    json={'email': 'admin@masjid.com', 'password': 'admin123'}
)
admin_token = admin_resp.json()['access_token']

# Send message
print("Sending message...")
send_resp = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    json={'student_id': 5, 'message': f'Test {int(time.time())}'},
    headers={'Authorization': f'Bearer {admin_token}'}
)

print(f"Status: {send_resp.status_code}")
print(f"Response:")
print(json.dumps(send_resp.json(), indent=2))
