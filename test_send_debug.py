import requests
import json

BASE_URL = 'http://localhost:5001/api'

# Login as admin
admin_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'admin@masjid.com',
    'password': 'admin123'
})

if admin_login.ok:
    admin_token = admin_login.json()['access_token']
    print('Admin logged in')
    
    # Send a message
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    message_payload = {
        'student_id': 5,
        'message': 'Debug test message from admin'
    }
    
    print(f'\nSending POST to /messages/admin/send-to-student')
    print(f'Payload: {json.dumps(message_payload, indent=2)}')
    
    response = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json=message_payload,
        headers=headers
    )
    
    print(f'\nResponse Status: {response.status_code}')
    print(f'Response Body:\n{json.dumps(response.json(), indent=2)}')
    
    # Now check if message was saved
    if response.ok:
        resp_data = response.json()
        msg_id = resp_data.get('message_id')
        
        if msg_id:
            print(f'\n\nChecking database for message ID {msg_id}...')
            from database import SessionLocal
            from models import AdminMessage
            
            db = SessionLocal()
            msg = db.query(AdminMessage).filter(AdminMessage.id == msg_id).first()
            
            if msg:
                print(f'Message found in DB:')
                print(f'  is_read: {msg.is_read}')
                print(f'  sender_id: {msg.sender_id}')
                print(f'  student_id: {msg.student_id}')
            else:
                print(f'Message NOT found in DB!')
            
            db.close()
else:
    print('Admin login failed')
