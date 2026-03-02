"""
Zoom API Service - Create real Zoom meetings using OAuth
Generates actual Zoom meetings with real meeting IDs
"""

import base64
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# Zoom API Configuration
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "")
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID", "")
ZOOM_API_BASE = "https://api.zoom.us/v2"
ZOOM_OAUTH_URL = "https://zoom.us/oauth/token"

# Cache access token to avoid multiple requests
_access_token_cache = {"token": None, "expires_at": None}


def get_zoom_access_token() -> Optional[str]:
    """
    Get Zoom access token using account_credentials flow
    Uses Basic auth with Client ID and Secret
    
    Returns access token string or None if failed
    """
    if not ZOOM_CLIENT_ID or not ZOOM_CLIENT_SECRET or not ZOOM_ACCOUNT_ID:
        print("⚠️  Zoom credentials not configured. Set ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, and ZOOM_ACCOUNT_ID in .env")
        return None
    
    # Check if token is cached and still valid
    if _access_token_cache["token"] and _access_token_cache["expires_at"]:
        if datetime.now() < _access_token_cache["expires_at"]:
            return _access_token_cache["token"]
    
    try:
        # Create Basic auth header
        auth_string = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Request access token
        params = {
            "grant_type": "account_credentials",
            "account_id": ZOOM_ACCOUNT_ID
        }
        
        response = requests.post(
            ZOOM_OAUTH_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            error_msg = response.json().get("error_description", response.text)
            print(f"❌ Failed to get Zoom access token: {error_msg}")
            return None
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        
        # Cache the token
        _access_token_cache["token"] = access_token
        _access_token_cache["expires_at"] = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error getting Zoom access token: {e}")
        return None


def create_zoom_meeting_via_api(
    event_name: str,
    start_time: datetime,
    duration_minutes: int = 60,
    host_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a real Zoom meeting via API
    
    Args:
        event_name: Meeting title
        start_time: Meeting start time
        duration_minutes: Duration in minutes (default 60)
        host_email: Email of the host (optional)
    
    Returns:
        {
            "success": bool,
            "meeting_id": str,
            "zoom_link": str,
            "join_url": str,
            "error": str (if failed)
        }
    """
    token = get_zoom_access_token()
    
    if not token:
        print("❌ Cannot create meeting - Zoom API credentials not configured")
        return {
            "success": False,
            "error": "Zoom credentials not configured. Please set ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET in .env"
        }
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Use "me" to create meeting for the authenticated user/account
        # ZOOM_ACCOUNT_ID is not a valid user ID, so we use "me"
        host_id = "me"
        
        # Create meeting payload
        meeting_data = {
            "topic": event_name,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.isoformat(),
            "duration": duration_minutes,
            "settings": {
                "host_video": False,  # Host doesn't need video on
                "participant_video": True,  # Participants can video
                "join_before_host": True,  # Allow join before host
                "waiting_room": False,  # No waiting room
            }
        }
        
        # Create the meeting
        response = requests.post(
            f"{ZOOM_API_BASE}/users/{host_id}/meetings",
            headers=headers,
            json=meeting_data,
            timeout=10
        )
        
        if response.status_code != 201:
            error_msg = response.json().get("message", "Unknown error")
            print(f"❌ Zoom API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        meeting_info = response.json()
        meeting_id = meeting_info.get("id")
        join_url = meeting_info.get("join_url")
        
        print(f"✅ Created Zoom meeting: {meeting_id}")
        print(f"   Join URL: {join_url}")
        
        return {
            "success": True,
            "meeting_id": str(meeting_id),
            "zoom_link": join_url,
            "join_url": join_url,
            "start_url": meeting_info.get("start_url"),
            "message": f"Zoom meeting created: {meeting_id}"
        }
        
    except requests.exceptions.Timeout:
        print("❌ Zoom API request timed out")
        return {
            "success": False,
            "error": "Zoom API request timeout"
        }
    except Exception as e:
        print(f"❌ Error creating Zoom meeting: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """
    Get details of an existing Zoom meeting
    """
    token = get_zoom_access_token()
    
    if not token:
        return {"success": False, "error": "Zoom credentials not configured"}
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Meeting not found: {meeting_id}"
            }
        
        meeting_info = response.json()
        
        return {
            "success": True,
            "meeting_id": meeting_info.get("id"),
            "topic": meeting_info.get("topic"),
            "join_url": meeting_info.get("join_url"),
            "start_url": meeting_info.get("start_url"),
            "start_time": meeting_info.get("start_time")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """
    Delete a Zoom meeting
    """
    token = get_zoom_access_token()
    
    if not token:
        return {"success": False, "error": "Zoom credentials not configured"}
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code not in [200, 204]:
            return {
                "success": False,
                "error": f"Failed to delete meeting"
            }
        
        return {
            "success": True,
            "message": f"Meeting {meeting_id} deleted"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def test_zoom_api():
    """Test Zoom API connection"""
    print("\n" + "=" * 80)
    print("TESTING ZOOM API CONNECTION")
    print("=" * 80 + "\n")
    
    token = get_zoom_access_token()
    
    if not token:
        print("❌ Zoom credentials not configured")
        print("\nTo enable Zoom API, add these to your .env file:")
        print("  ZOOM_CLIENT_ID=your_client_id")
        print("  ZOOM_CLIENT_SECRET=your_client_secret")
        print("  ZOOM_ACCOUNT_ID=your_account_id")
        print("\nGet credentials from: https://marketplace.zoom.us/")
        return False
    
    print("✅ Zoom credentials configured")
    print(f"   Client ID: {ZOOM_CLIENT_ID[:10]}...")
    print(f"   Account ID: {ZOOM_ACCOUNT_ID or 'me'}")
    
    # Try creating a test meeting
    print("\n🔄 Creating test meeting...")
    result = create_zoom_meeting_via_api(
        event_name="Zoom API Test",
        start_time=datetime.now() + timedelta(hours=1)
    )
    
    if result["success"]:
        print(f"✅ Test meeting created!")
        print(f"   Meeting ID: {result['meeting_id']}")
        print(f"   Join URL: {result['join_url']}")
        
        # Clean up test meeting
        print(f"\n🔄 Cleaning up test meeting...")
        delete_result = delete_zoom_meeting(result['meeting_id'])
        if delete_result["success"]:
            print("✅ Test meeting deleted")
        
        return True
    else:
        print(f"❌ Failed to create test meeting: {result['error']}")
        return False


if __name__ == "__main__":
    test_zoom_api()
