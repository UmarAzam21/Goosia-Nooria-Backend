import requests
import json

BASE_URL = "https://pruritic-contemplable-roselee.ngrok-free.dev/api"

# Login as rehan
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "rehan@teacher.com", "password": "123456"}
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ Logged in as rehan@teacher.com")
    
    # Get teacher courses
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/courses/my-courses/teacher",
        headers=headers
    )
    
    if response.status_code == 200:
        courses = response.json()
        print(f"\n✓ Got {len(courses)} enrollments from /courses/my-courses/teacher")
        print("\nEnrollments:")
        for i, course in enumerate(courses):
            print(f"\n  {i+1}. {course.get('course', {}).get('name', 'Unknown')}")
            if course.get('time_slot'):
                print(f"     Day: {course['time_slot'].get('day', 'N/A')}")
                print(f"     Time: {course['time_slot'].get('start_time', '')}-{course['time_slot'].get('end_time', '')}")
            print(f"     Status: {course.get('enrollment_status', 'N/A')}")
    else:
        print(f"✗ Error fetching courses: {response.status_code}")
        print(response.text)
else:
    print(f"✗ Login failed: {response.status_code}")
    print(response.text)
