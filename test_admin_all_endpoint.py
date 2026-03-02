"""
Check what the /messages/admin/all endpoint actually returns
"""
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:5001/api"

def make_request(method, url, token=None, data=None):
    """Simple HTTP request helper"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if data:
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return e.code, {"error": error_body}

# Step 1: Admin Login
print("=" * 80)
print("STEP 1: ADMIN LOGIN")
print("=" * 80)
status, data = make_request(
    'POST',
    f"{BASE_URL}/auth/login/json",
    data={'email': 'admin@masjid.com', 'password': 'admin123'}
)
print(f"Status: {status}")
if status != 200:
    print(f"FAILED: {data}")
    exit(1)

admin_token = data['access_token']
print(f"✅ Admin logged in successfully")

# Step 2: Get all messages
print("\n" + "=" * 80)
print("STEP 2: FETCH /messages/admin/all")
print("=" * 80)
status, data = make_request(
    'GET',
    f"{BASE_URL}/messages/admin/all",
    token=admin_token
)
print(f"Status: {status}")
if status != 200:
    print(f"FAILED: {data}")
    exit(1)

print(f"\n✅ Returned {len(data)} messages")

if not data:
    print("⚠️  ERROR: No messages returned!")
    exit(1)

# Step 3: Analyze response structure
print("\n" + "=" * 80)
print("STEP 3: ANALYZE RESPONSE STRUCTURE")
print("=" * 80)

first_msg = data[0]
print(f"\nFirst message structure:")
print(f"  Keys: {list(first_msg.keys())}")

print(f"\nFirst message data:")
for key, value in first_msg.items():
    if isinstance(value, str):
        print(f"  {key}: {value[:50]}")
    else:
        print(f"  {key}: {value}")

# Step 4: Check student_id field
print("\n" + "=" * 80)
print("STEP 4: STUDENT_ID ANALYSIS")
print("=" * 80)

if 'student_id' in first_msg:
    student_ids = [m.get('student_id') for m in data]
    unique_student_ids = set(student_ids)
    print(f"✅ student_id field present in messages")
    print(f"  Total messages: {len(data)}")
    print(f"  Unique students: {len(unique_student_ids)}")
    print(f"  Student IDs: {sorted(unique_student_ids)}")
else:
    print(f"❌ student_id field NOT present in messages!")
    print(f"   Frontend cannot group messages by student")

# Step 5: Check for null/empty student_ids
print("\n" + "=" * 80)
print("STEP 5: CHECK FOR NULL/EMPTY VALUES")
print("=" * 80)

null_student_ids = [m for m in data if m.get('student_id') is None]
if null_student_ids:
    print(f"⚠️  {len(null_student_ids)} messages have NULL student_id")
    print(f"   This might prevent grouping by student")
else:
    print(f"✅ No NULL student_ids found")

# Step 6: Show sample messages
print("\n" + "=" * 80)
print("STEP 6: SAMPLE MESSAGES (First 5)")
print("=" * 80)

for i, msg in enumerate(data[:5]):
    student_id = msg.get('student_id', 'NULL')
    student_name = msg.get('student_name', 'Unknown')
    message_text = msg.get('message', '')[:40]
    print(f"\n[{i+1}] ID={msg.get('id')}, Student ID={student_id}, Name={student_name}")
    print(f"    Message: {message_text}...")
