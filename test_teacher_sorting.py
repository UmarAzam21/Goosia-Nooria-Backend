import requests

BASE_URL = "http://localhost:5001/api"

# Get all teachers
response = requests.get(f"{BASE_URL}/teachers")
teachers = response.json()

print("Teachers in order returned by API:")
print("=" * 50)
for i, teacher in enumerate(teachers, 1):
    teacher_name = teacher.get('user', {}).get('name', 'Unknown')
    print(f"{i}. {teacher_name} (ID: {teacher.get('id')})")

print("\n" + "=" * 50)
print(f"Total teachers: {len(teachers)}")

# Check if sorted correctly
if teachers:
    names = [t.get('user', {}).get('name', '') for t in teachers]
    sorted_names = sorted(names)
    if names == sorted_names:
        print("✓ Teachers are properly sorted alphabetically!")
    else:
        print("✗ Teachers are NOT sorted correctly")
        print(f"Expected order: {sorted_names}")
        print(f"Actual order: {names}")
