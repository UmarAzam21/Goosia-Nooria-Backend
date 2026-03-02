import requests

BASE_URL = 'http://localhost:5001/api'

# Step 1: Login as admin
print('=== TESTING BADGE FLOW ===\n')
print('Step 1: Admin login...')
admin_login = requests.post(f'{BASE_URL}/auth/login/json', json={
    'email': 'admin@masjid.com',
    'password': 'admin123'
})

if admin_login.ok:
    admin_token = admin_login.json()['access_token']
    print(' ✓ Admin logged in\n')
    
    # Step 2: Send a message
    print('Step 2: Admin sends message to student 5...')
    send_resp = requests.post(
        f'{BASE_URL}/messages/admin/send-to-student',
        json={'student_id': 5, 'message': 'Hello from admin test'},
        headers={'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    )
    
    if send_resp.ok:
        msg_data = send_resp.json()
        print(f' ✓ Message sent with ID: {msg_data.get("id")}\n')
    else:
        print(f' ✗ Error: {send_resp.status_code} - {send_resp.text}\n')
    
    # Step 3: Login as student
    print('Step 3: Student login and fetch messages...')
    student_login = requests.post(f'{BASE_URL}/auth/login/json', json={
        'email': 'ali@student.com',
        'password': 'ali123'
    })
    
    if student_login.ok:
        student_token = student_login.json()['access_token']
        print(' ✓ Student logged in\n')
        
        messages_resp = requests.get(
            f'{BASE_URL}/messages/my-messages',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        if messages_resp.ok:
            messages = messages_resp.json()
            print(f'Total messages: {len(messages)}\n')
            
            # Show last 3 messages
            print('Last 3 messages:')
            for i, msg in enumerate(messages[-3:], 1):
                print(f'\n {i}. ID={msg["id"]}, From=sender_id:{msg["sender_id"]}, Read={msg["is_read"]}')
                print(f'    Text: {msg["message"][:60]}...')
            
            # Calculate unread (from others, not read)
            student_id = 5
            unread = [m for m in messages if m.get("sender_id") != student_id and not m.get("is_read")]
            print(f'\n\nUNREAD COUNT (sender_id != {student_id} AND is_read=False): {len(unread)}')
            
            if unread:
                print('\nUnread messages:')
                for msg in unread[:3]:
                    print(f'  - ID {msg["id"]}: {msg["message"][:40]}...')
else:
    print('Failed to login as admin')
