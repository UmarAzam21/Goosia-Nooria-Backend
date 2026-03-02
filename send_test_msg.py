#!/usr/bin/env python3
"""Send a test message and capture backend log output"""
import requests
import time

BASE_URL = 'http://localhost:5001/api'

print("\n" + "="*70)
print("SENDING TEST MESSAGE - Check backend console output")
print("="*70)

time.sleep(1)

# Admin login
print("\n1. Admin login...")
admin_resp = requests.post(
    f'{BASE_URL}/auth/login/json',
    json={'email': 'admin@masjid.com', 'password': 'admin123'},
    timeout=10
)
admin_token = admin_resp.json()['access_token']
print(f"   OK - Token: {admin_token[:20]}...")

# Send message
print("\n2. Sending message...")
send_resp = requests.post(
    f'{BASE_URL}/messages/admin/send-to-student',
    json={'student_id': 5, 'message': f'TEST {int(time.time())}'},
    headers={'Authorization': f'Bearer {admin_token}'},
    timeout=10
)

print(f"   Status: {send_resp.status_code}")
print(f"   Response: {send_resp.json()}")

print("\n⬆️ CHECK BACKEND CONSOLE FOR [SEND-MSG] DEBUG LINES")
print("="*70 + "\n")
