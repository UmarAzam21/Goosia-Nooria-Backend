#!/usr/bin/env python3
"""
Verify Zoom Server-to-Server OAuth Credentials
Debug script to test if credentials are valid
"""

import jwt
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID", "")

print("=" * 80)
print("ZOOM CREDENTIALS VERIFICATION")
print("=" * 80)

print("\n1️⃣ Checking Credentials...")
print(f"   Client ID:     {CLIENT_ID[:20]}..." if CLIENT_ID else "   ❌ No Client ID")
print(f"   Client Secret: {CLIENT_SECRET[:20]}..." if CLIENT_SECRET else "   ❌ No Client Secret")
print(f"   Account ID:    {ACCOUNT_ID}")

if not CLIENT_ID or not CLIENT_SECRET:
    print("\n❌ Missing credentials. Cannot proceed.")
    exit(1)

print("\n2️⃣ Generating JWT Token...")
try:
    now = int(time.time())
    payload = {
        "iss": CLIENT_ID,
        "sub": ACCOUNT_ID if ACCOUNT_ID else CLIENT_ID,
        "exp": now + 3600
    }
    
    token = jwt.encode(payload, CLIENT_SECRET, algorithm="HS256")
    print(f"   ✅ JWT Generated")
    print(f"   Token: {token[:50]}...")
    
    # Decode to verify
    decoded = jwt.decode(token, CLIENT_SECRET, algorithms=["HS256"])
    print(f"   Payload: {json.dumps(decoded, indent=8)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n3️⃣ Testing Methods to Get Access Token...")

# Method 1: Direct JWT as Bearer token
print("\n   Method 1: Using JWT as Bearer Token")
try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://api.zoom.us/v2/users/me",
        headers=headers,
        timeout=10
    )
    print(f"      Status: {response.status_code}")
    if response.status_code == 200:
        print(f"      ✅ SUCCESS - Credentials are valid!")
        print(f"      User: {response.json().get('email')}")
    else:
        print(f"      ❌ Failed: {response.json().get('message')}")
except Exception as e:
    print(f"      ❌ Error: {e}")

# Method 2: Exchange JWT for access token (OAuth token endpoint)
print("\n   Method 2: Exchanging JWT for Access Token")
try:
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": token
    }
    response = requests.post(
        "https://zoom.us/oauth/token",
        data=data,
        timeout=10
    )
    print(f"      Status: {response.status_code}")
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print(f"      ✅ Got Access Token: {access_token[:30]}...")
        
        # Test the access token
        headers = {"Authorization": f"Bearer {access_token}"}
        response2 = requests.get(
            "https://api.zoom.us/v2/users/me",
            headers=headers,
            timeout=10
        )
        if response2.status_code == 200:
            print(f"      ✅ Access Token WORKS!")
        else:
            print(f"      ❌ Access Token failed: {response2.json()}")
    else:
        print(f"      ❌ Failed: {response.json()}")
except Exception as e:
    print(f"      ❌ Error: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
print("""
If Method 1 works:
   ✅ Your Server-to-Server OAuth is correctly configured
   ✅ You can use JWT tokens directly as Bearer tokens

If Method 2 works but Method 1 doesn't:
   ⚠️  You need to exchange JWT for access tokens first
   ⚠️  Update the Zoom service to use /oauth/token endpoint

If both fail:
   ❌ The credentials might be incorrect or incomplete
   ❌ Check that your Zoom app is set up as Server-to-Server OAuth
   ❌ Verify Client ID, Client Secret, and Account ID match your app
""")

print("\n" + "=" * 80)
