#!/usr/bin/env python3
"""
Test Login Endpoint
"""
import requests
import json

print('=' * 80)
print('TESTING LOGIN ENDPOINT')
print('=' * 80)

BASE_URL = 'http://localhost:5000'

test_credentials = [
    ('admin@masjid.com', 'admin123', 'Admin'),
    ('ahmed@masjid.com', 'ahmed123', 'Teacher'),
    ('ali@student.com', 'ali123', 'Student'),
]

for email, password, role in test_credentials:
    print(f'\n🔐 Testing {role}: {email}')
    
    try:
        # OAuth2PasswordRequestForm expects form data, not JSON
        response = requests.post(
            f'{BASE_URL}/api/auth/login',
            data={
                'username': email,  # username field but we pass email
                'password': password
            },
            timeout=5
        )
        
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token', 'N/A')[:30] + '...'
            user_email = data.get('user', {}).get('email', 'N/A')
            user_role = data.get('user', {}).get('role', 'N/A')
            print(f'   ✅ LOGIN SUCCESS')
            print(f'   Token: {token}')
            print(f'   User Email: {user_email}')
            print(f'   Role: {user_role}')
        else:
            print(f'   ❌ LOGIN FAILED')
            try:
                error_detail = response.json()
                print(f'   Error: {json.dumps(error_detail, indent=2)[:400]}')
            except:
                print(f'   Response: {response.text[:300]}')
            
    except requests.exceptions.ConnectionError:
        print(f'   ❌ CONNECTION ERROR - Backend not running on {BASE_URL}')
        break
    except Exception as e:
        print(f'   ❌ ERROR: {str(e)[:100]}')

print('\n' + '=' * 80)
