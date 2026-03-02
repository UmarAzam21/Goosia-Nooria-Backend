import requests
import json

BASE_URL = "http://localhost:5001"

# Test 1: Quick Enroll
print("=" * 60)
print("TEST 1: Quick Enroll Endpoint")
print("=" * 60)

# First, create a test token (you'd need valid credentials)
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "student@example.com", "password": "password123"}
)

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try quick enroll
    enroll_response = requests.post(
        f"{BASE_URL}/enrollments/quick-enroll",
        json={"course_id": 1},
        headers=headers
    )
    
    print(f"Status: {enroll_response.status_code}")
    print(f"Response: {json.dumps(enroll_response.json(), indent=2)}")
    
    # Test 2: Get My Enrollments
    print("\n" + "=" * 60)
    print("TEST 2: My Enrollments Endpoint")
    print("=" * 60)
    
    my_enroll_response = requests.get(
        f"{BASE_URL}/enrollments/my-enrollments",
        headers=headers
    )
    
    print(f"Status: {my_enroll_response.status_code}")
    print(f"Response: {json.dumps(my_enroll_response.json(), indent=2)}")
else:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.json())
