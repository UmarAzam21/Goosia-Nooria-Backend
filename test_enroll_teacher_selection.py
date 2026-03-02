import requests
import json

BASE_URL = "http://localhost:5001/api"

print("\n" + "=" * 80)
print("TESTING ENROLLMENT FLOW - TEACHER SELECTION")
print("=" * 80)

# Step 1: Get all teachers
print("\n[STEP 1] Fetching all teachers...")
response = requests.get(f"{BASE_URL}/teachers")
teachers = response.json()

print(f"\nAvailable Teachers:")
for teacher in teachers:
    print(f"  ID: {teacher['id']}, Name: {teacher['user']['name']}")

# Step 2: Select a specific teacher (e.g., "madam" with ID 6)
selected_teacher = None
for teacher in teachers:
    if teacher['user']['name'].lower() == 'madam':
        selected_teacher = teacher
        break

if not selected_teacher:
    print("\n✗ ERROR: 'madam' teacher not found!")
    exit(1)

print(f"\n[STEP 2] Selected Teacher: {selected_teacher['user']['name']} (ID: {selected_teacher['id']})")

# Step 3: Get time slots for selected teacher
print(f"\n[STEP 3] Fetching time slots for {selected_teacher['user']['name']}...")
response = requests.get(f"{BASE_URL}/teachers/{selected_teacher['id']}/time-slots")
time_slots = response.json()

print(f"\nAvailable Time Slots for {selected_teacher['user']['name']}:")
for i, slot in enumerate(time_slots[:3], 1):
    print(f"  {i}. ID: {slot['id']}, {slot['day_of_week']}: {slot['start_time']} - {slot['end_time']}")

if not time_slots:
    print("\n✗ ERROR: No time slots found for this teacher!")
    exit(1)

selected_slot = time_slots[0]
print(f"\n✓ Selected Time Slot: ID {selected_slot['id']} ({selected_slot['day_of_week']} {selected_slot['start_time']})")

# Step 4: Create enrollment with selected teacher's time slot
print(f"\n[STEP 4] Creating enrollment with:")
print(f"  Course ID: 1 (nazra)")
print(f"  Time Slot ID: {selected_slot['id']}")

# Get a test token (using student account)
print("\n[AUTH] Logging in as student...")
auth_response = requests.post(
    f"{BASE_URL}/login",
    json={
        "email": "umar@example.com",
        "password": "password123"
    }
)

if auth_response.status_code != 200:
    print(f"✗ Login failed: {auth_response.text}")
    exit(1)

token = auth_response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Create enrollment
enrollment_response = requests.post(
    f"{BASE_URL}/enrollments/quick-enroll",
    json={
        "course_id": 1,
        "time_slot_id": selected_slot['id']
    },
    headers=headers
)

if enrollment_response.status_code != 201:
    print(f"\n✗ Enrollment creation failed: {enrollment_response.text}")
    exit(1)

enrollment = enrollment_response.json()
print(f"\n✓ Enrollment Created!")
print(f"  Enrollment ID: {enrollment['id']}")
print(f"  Teacher ID: {enrollment['teacher_id']}")
print(f"  Time Slot ID: {enrollment['time_slot_id']}")

# Step 5: Verify the enrollment has correct teacher
print(f"\n[STEP 5] Verifying enrollment details...")
response = requests.get(
    f"{BASE_URL}/enrollments/my-enrollments",
    headers=headers
)

enrollments = response.json()
found_enrollment = None
for enr in enrollments:
    if enr['id'] == enrollment['id']:
        found_enrollment = enr
        break

if not found_enrollment:
    print(f"✗ ERROR: Enrollment not found in my-enrollments!")
    exit(1)

print(f"\n✓ Enrollment Found:")
print(f"  Enrollment ID: {found_enrollment['id']}")
print(f"  Teacher Name: {found_enrollment['teacher']['name']}")
print(f"  Teacher ID: {found_enrollment['teacher_id']}")
print(f"  Selected Teacher Name: {selected_teacher['user']['name']}")
print(f"  Selected Teacher ID: {selected_teacher['id']}")

# Verify match
if found_enrollment['teacher']['name'].lower() == selected_teacher['user']['name'].lower():
    print(f"\n✅ SUCCESS: Enrollment teacher matches selected teacher!")
    print(f"   Both are: {found_enrollment['teacher']['name']}")
else:
    print(f"\n❌ MISMATCH: Selected '{selected_teacher['user']['name']}' but enrollment shows '{found_enrollment['teacher']['name']}'!")
    print(f"\nDEBUG INFO:")
    print(f"  Selected Teacher ID: {selected_teacher['id']}")
    print(f"  Enrollment Teacher ID: {found_enrollment['teacher_id']}")
    print(f"  Time Slot ID used: {selected_slot['id']}")
    print(f"  Enrollment Time Slot ID: {found_enrollment['time_slot_id']}")
    
print("\n" + "=" * 80)
