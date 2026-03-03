import requests
import json

BASE_URL = "http://localhost:5001/api"

print("\n" + "=" * 90)
print("COMPREHENSIVE TEACHER-TIMESLOT ENROLLMENT DIAGNOSTIC")
print("=" * 90)

# Step 1: Get all teachers
print("\n[1] FETCHING ALL TEACHERS...")
print("-" * 90)
response = requests.get(f"{BASE_URL}/teachers")
if response.status_code != 200:
    print(f"✗ Failed to fetch teachers: {response.text}")
    exit(1)

teachers = response.json()
print(f"✓ Found {len(teachers)} teachers\n")
for teacher in teachers:
    print(f"  ID: {teacher['id']:2d} | Name: {teacher['user']['name']:20s} | Available: {teacher['is_available']}")

# Step 2: Get all time slots and their teacher assignments
print("\n\n[2] FETCHING TIME SLOTS FOR EACH TEACHER...")
print("-" * 90)

teacher_timeslots_map = {}
for teacher in teachers:
    response = requests.get(f"{BASE_URL}/teachers/{teacher['id']}/time-slots")
    if response.status_code == 200:
        slots = response.json()
        teacher_timeslots_map[teacher['id']] = {
            'name': teacher['user']['name'],
            'slots': slots
        }
        print(f"\n✓ Teacher ID {teacher['id']} ({teacher['user']['name']}): {len(slots)} time slots")
        for i, slot in enumerate(slots[:3], 1):
            print(f"    #{i} Slot ID: {slot['id']:3d} | {slot['day_of_week']:10s} | {slot['start_time']} - {slot['end_time']}")
        if len(slots) > 3:
            print(f"    ... and {len(slots) - 3} more")

# Step 3: Verify time slots don't overlap between teachers
print("\n\n[3] CHECKING FOR TIME SLOT CONFLICTS...")
print("-" * 90)

slot_to_teacher = {}
conflicts = []
for teacher_id, data in teacher_timeslots_map.items():
    for slot in data['slots']:
        slot_id = slot['id']
        if slot_id in slot_to_teacher:
            conflicts.append({
                'slot_id': slot_id,
                'teachers': [slot_to_teacher[slot_id]['name'], data['name']]
            })
        else:
            slot_to_teacher[slot_id] = {'id': teacher_id, 'name': data['name']}

if conflicts:
    print(f"⚠️  Found {len(conflicts)} time slot conflicts:")
    for conf in conflicts:
        print(f"  - Slot ID {conf['slot_id']} assigned to: {conf['teachers']}")
else:
    print("✓ No time slot conflicts - each slot belongs to exactly one teacher")

# Step 4: Select a specific teacher and test enrollment
print("\n\n[4] TESTING ENROLLMENT FLOW...")
print("-" * 90)

# Find madam teacher
madam_teacher = None
for teacher in teachers:
    if teacher['user']['name'].lower() == 'madam':
        madam_teacher = teacher
        break

if not madam_teacher:
    print("✗ 'madam' teacher not found!")
    exit(1)

print(f"\n✓ Selected Teacher: {madam_teacher['user']['name']} (ID: {madam_teacher['id']})")

# Get teacher's time slots
madam_slots = teacher_timeslots_map[madam_teacher['id']]['slots']
if not madam_slots:
    print(f"✗ No time slots for {madam_teacher['user']['name']}")
    exit(1)

selected_slot = madam_slots[0]
print(f"✓ Selected Time Slot: ID {selected_slot['id']} | {selected_slot['day_of_week']} {selected_slot['start_time']}")

# Step 5: Create test enrollment
print("\n\n[5] CREATING ENROLLMENT...")
print("-" * 90)

print(f"\nEnrollment request:")
print(f"  course_id: 1")
print(f"  time_slot_id: {selected_slot['id']}")
print(f"  Expected teacher_id: {madam_teacher['id']} ({madam_teacher['user']['name']})")

# Login as test student
auth_response = requests.post(
    f"{BASE_URL}/login",
    json={
        "email": "umar@example.com",
        "password": "password123"
    }
)

if auth_response.status_code != 200:
    # Try alternative student
    auth_response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": "student1@example.com",
            "password": "password123"
        }
    )

if auth_response.status_code != 200:
    print(f"\n✗ Login failed: {auth_response.text}")
    print("\nTrying without authentication...")
    headers = {}
else:
    token = auth_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"✓ Logged in successfully")

# Create enrollment
print(f"\nCreating enrollment...")
enrollment_response = requests.post(
    f"{BASE_URL}/enrollments/quick-enroll",
    json={
        "course_id": 1,
        "time_slot_id": selected_slot['id']
    },
    headers=headers
)

if enrollment_response.status_code != 201:
    print(f"✗ Enrollment failed: {enrollment_response.status_code}")
    print(f"Response: {enrollment_response.text}")
    
    # Try with direct database check
    print("\n[FALLBACK] Checking database directly...")
    import psycopg2
    try:
        conn = psycopg2.connect("postgresql://postgres:bZ2BD!RLXb_s9-c@efdvqqbkykonjawgrpos.supabase.co:5432/postgres")
        cur = conn.cursor()
        
        # Get the most recent enrollment
        cur.execute("""
            SELECT e.id, e.student_id, e.course_id, e.teacher_id, e.time_slot_id, 
                   t.user_id, u.name,
                   ts.day_of_week, ts.start_time
            FROM enrollments e
            LEFT JOIN teachers t ON e.teacher_id = t.id
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN time_slots ts ON e.time_slot_id = ts.id
            ORDER BY e.created_at DESC LIMIT 1
        """)
        
        result = cur.fetchone()
        if result:
            print(f"\n✓ Latest enrollment in DB:")
            print(f"  Enrollment ID: {result[0]}")
            print(f"  Student ID: {result[1]}")
            print(f"  Course ID: {result[2]}")
            print(f"  Teacher ID: {result[3]}")
            print(f"  Time Slot ID: {result[4]}")
            print(f"  Teacher User ID: {result[5]}")
            print(f"  Teacher Name: {result[6]}")
            print(f"  Time Slot: {result[7]} {result[8]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"✗ Database check failed: {e}")
    exit(1)

enrollment = enrollment_response.json()
print(f"\n✓ Enrollment created!")
print(f"  Enrollment ID: {enrollment['id']}")
print(f"  Returned teacher_id: {enrollment['teacher_id']}")
print(f"  Returned time_slot_id: {enrollment['time_slot_id']}")

# Step 6: Verify the enrollment
print("\n\n[6] VERIFYING ENROLLMENT IN DATABASE...")
print("-" * 90)

import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:bZ2BD!RLXb_s9-c@efdvqqbkykonjawgrpos.supabase.co:5432/postgres")
    cur = conn.cursor()
    
    # Get the enrollment we just created
    cur.execute("""
        SELECT e.id, e.student_id, e.course_id, e.teacher_id, e.time_slot_id, 
               t.id, t.user_id, u.name,
               ts.id, ts.teacher_id, ts.day_of_week, ts.start_time
        FROM enrollments e
        LEFT JOIN teachers t ON e.teacher_id = t.id
        LEFT JOIN users u ON t.user_id = u.id
        LEFT JOIN time_slots ts ON e.time_slot_id = ts.id
        WHERE e.id = %s
    """, (enrollment['id'],))
    
    result = cur.fetchone()
    if result:
        db_enrollment_id, student_id, course_id, teacher_id, ts_id, \
        t_id, t_user_id, t_name, \
        slot_id, slot_teacher_id, day, time = result
        
        print(f"\n✓ Enrollment found in database:")
        print(f"  Enrollment ID: {db_enrollment_id}")
        print(f"  Student ID: {student_id}")
        print(f"  Course ID: {course_id}")
        print(f"  Teacher ID (enrollment.teacher_id): {teacher_id}")
        print(f"  Time Slot ID (enrollment.time_slot_id): {ts_id}")
        print(f"  Teacher object ID: {t_id}")
        print(f"  Teacher User ID: {t_user_id}")
        print(f"  Teacher Name: {t_name}")
        print(f"  Time Slot ID (in DB): {slot_id}")
        print(f"  Time Slot's teacher_id: {slot_teacher_id}")
        print(f"  Time Slot: {day} {time}")
        
        print(f"\n[VERIFICATION]")
        print(f"  Selected teacher: {madam_teacher['user']['name']} (ID: {madam_teacher['id']})")
        print(f"  Enrollment teacher_id: {teacher_id}")
        print(f"  DB teacher name: {t_name}")
        print(f"  Time Slot teacher_id: {slot_teacher_id}")
        
        if teacher_id == madam_teacher['id']:
            print(f"\n✅ SUCCESS: Teacher matched!")
        else:
            print(f"\n❌ MISMATCH: Expected teacher ID {madam_teacher['id']}, got {teacher_id}")
            
            # Check the relationship
            print(f"\n[DEBUGGING]")
            if slot_teacher_id != madam_teacher['id']:
                print(f"⚠️  Time Slot ID {ts_id} belongs to teacher {slot_teacher_id}, not {madam_teacher['id']}")
            if teacher_id != slot_teacher_id:
                print(f"⚠️  Enrollment teacher_id {teacher_id} doesn't match time_slot.teacher_id {slot_teacher_id}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Database verification failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 90)
