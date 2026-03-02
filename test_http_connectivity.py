"""
Test basic HTTP connectivity to make sure the server is responding
"""
import requests
import sys

print("\n" + "="*80)
print("BASIC HTTP CONNECTIVITY TEST")
print("="*80 + "\n")

# Test basic health check
try:
    print("1. Testing /api/health endpoint...")
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

# Test root endpoint
try:
    print("2. Testing / endpoint...")
    response = requests.get("http://localhost:5000/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

print("✅ HTTP server is responding correctly!")
