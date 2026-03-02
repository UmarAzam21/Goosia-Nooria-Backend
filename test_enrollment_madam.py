import requests
import json

BASE_URL = "http://localhost:5001/api"

print("=" * 70)
print("TESTING ENROLLMENT FLOW - TEACHER SELECTION")
print("=" * 70)

# Step 1: Get all teachers
print("\n1. FETCHING ALL TEACHERS")
print("-" * 70)
response = requests.get(f"{BASE_URL}/teachers")
teachers = response.json()

print(f"Response Status: {response.status_code}")
print(f"Total Teachers: {len(teachers)}\n")

for i, teacher in enumerate(teachers, 1):
    teacher_name = teacher.get('user', {}).get('name', 'Unknown')
    teacher_id = teacher.get('id')
    is_available = teacher.get('is_available', False)
    print(f"  {i}. ID: {teacher_id:2d} | Name: {teacher_name:15s} | Available: {is_available}")

# Step 2: Select a specific teacher - let's test with "madam"
print("\n" + "=" * 70)
print("2. SELECTING TEACHER - 'madam'")
print("-" * 70)

madam_teacher = None
for teacher in teachers:
    if teacher.get('user', {}).get('name', '').lower() == 'madam':
        madam_teacher = teacher
        break

if madam_teacher:
    print(f"✓ Found 'madam' teacher:")
    print(f"  ID: {madam_teacher.get('id')}")
    print(f"  Name: {madam_teacher.get('user', {}).get('name')}")
    print(f"  Available: {madam_teacher.get('is_available')}")
    print(f"  Course ID: {madam_teacher.get('course_id')}")
    print(f"\n✓ SELECTION SUCCESS - 'madam' teacher object:")
    print(json.dumps(madam_teacher, indent=2))
else:
    print("✗ ERROR: 'madam' teacher not found in the list")

# Step 3: Get first teacher (teacher1 - the one that was being auto-selected)
print("\n" + "=" * 70)
print("3. COMPARING WITH FIRST TEACHER")
print("-" * 70)

if teachers:
    first_teacher = teachers[0]
    print(f"✓ First teacher in list:")
    print(f"  ID: {first_teacher.get('id')}")
    print(f"  Name: {first_teacher.get('user', {}).get('name')}")
    print(f"  Available: {first_teacher.get('is_available')}")
    print(f"\n  Full object:")
    print(json.dumps(first_teacher, indent=2))

# Step 4: Get time slots for "madam"
if madam_teacher:
    print("\n" + "=" * 70)
    print("4. FETCHING TIME SLOTS FOR 'madam'")
    print("-" * 70)
    
    teacher_id = madam_teacher.get('id')
    response = requests.get(f"{BASE_URL}/teachers/{teacher_id}/time-slots")
    time_slots = response.json()
    
    print(f"Response Status: {response.status_code}")
    print(f"Time Slots Found: {len(time_slots)}\n")
    
    if time_slots:
        for slot in time_slots:
            print(f"  • {slot.get('day_of_week')}: {slot.get('start_time')} - {slot.get('end_time')}")
    else:
        print("  No time slots available for this teacher")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
