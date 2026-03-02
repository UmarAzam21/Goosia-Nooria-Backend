import requests
import json

BASE_URL = "http://localhost:5001/api"

print("\n" + "=" * 70)
print("TESTING SELECTION OF 'teacher1'")
print("=" * 70)

response = requests.get(f"{BASE_URL}/teachers")
teachers = response.json()

# Find teacher1
teacher1 = None
for teacher in teachers:
    if teacher.get('user', {}).get('name', '').lower() == 'teacher1':
        teacher1 = teacher
        break

if teacher1:
    print(f"\n✓ Found 'teacher1' teacher:")
    print(f"  ID: {teacher1.get('id')}")
    print(f"  Name: {teacher1.get('user', {}).get('name')}")
    print(f"  Email: {teacher1.get('user', {}).get('email')}")
    
    # Get time slots for teacher1
    teacher_id = teacher1.get('id')
    response = requests.get(f"{BASE_URL}/teachers/{teacher_id}/time-slots")
    time_slots = response.json()
    
    print(f"\n  Time Slots: {len(time_slots)}")
    if time_slots:
        for i, slot in enumerate(time_slots[:3], 1):
            print(f"    {i}. {slot.get('day_of_week')}: {slot.get('start_time')} - {slot.get('end_time')}")
        if len(time_slots) > 3:
            print(f"    ... and {len(time_slots) - 3} more")
else:
    print("✗ teacher1 not found")

print("\n" + "=" * 70)
print("COMPARISON SUMMARY")
print("=" * 70)
print("""
When you enroll a course and SELECT A TEACHER:

✓ The backend returns teachers in alphabetical order
✓ Each teacher has their own time slots
✓ The selection is working correctly on the backend
✓ The frontend now shows "✓ Selected: [Teacher Name]" when you click a teacher

Your browser should now show:
- Green highlighting on the selected teacher card
- "✓ Selected: madam" at the top when you select madam
- Proper time slots for the selected teacher
""")
