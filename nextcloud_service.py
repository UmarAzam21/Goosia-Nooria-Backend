import requests
import os
from typing import Optional, Dict, Any
from requests.auth import HTTPBasicAuth
import urllib.parse

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL", "https://your-nextcloud-server.com")
NEXTCLOUD_USERNAME = os.getenv("NEXTCLOUD_USERNAME", "admin")
NEXTCLOUD_APP_PASSWORD = os.getenv("NEXTCLOUD_APP_PASSWORD", "your-app-specific-password")

# Remove trailing slash if present
NEXTCLOUD_URL = NEXTCLOUD_URL.rstrip('/')

def get_auth():
    """Get authentication credentials for Nextcloud API"""
    return HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_APP_PASSWORD)

def create_talk_room(room_name: str, participant_type: str = "public") -> Dict[str, Any]:
    """
    Create a new Nextcloud Talk conversation/room
    
    Args:
        room_name: Name of the room
        participant_type: "public" or "private"
    
    Returns:
        Dictionary with room creation response
    """
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v4/rooms"
    
    params = {
        "roomType": 1,  # 1 = public group, 2 = private group, 3 = one-to-one
        "roomName": room_name,
    }
    
    headers = {
        "OCS-APIRequest": "true",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            url,
            json=params,
            auth=get_auth(),
            headers=headers,
            timeout=10,
            verify=False  # For self-signed certificates
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("ocs", {}).get("meta", {}).get("status") == "ok":
            room_data = data["ocs"]["data"]
            return {
                "success": True,
                "room_id": room_data.get("token"),
                "room_name": room_data.get("displayName"),
                "room_type": room_data.get("roomType"),
                "message": "Room created successfully"
            }
        else:
            return {
                "success": False,
                "error": data.get("ocs", {}).get("meta", {}).get("message", "Unknown error")
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_room_token(room_name: str) -> Optional[str]:
    """
    Get the token (room ID) of an existing room by name
    
    Args:
        room_name: Name of the room
    
    Returns:
        Room token if found, None otherwise
    """
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v4/rooms"
    
    headers = {
        "OCS-APIRequest": "true"
    }
    
    try:
        response = requests.get(
            url,
            auth=get_auth(),
            headers=headers,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("ocs", {}).get("meta", {}).get("status") == "ok":
            rooms = data["ocs"]["data"]
            for room in rooms:
                if room.get("displayName") == room_name:
                    return room.get("token")
        
        return None
    
    except Exception as e:
        print(f"Error getting room token: {e}")
        return None

def get_talk_link(room_token: str, user_name: str) -> str:
    """
    Generate Nextcloud Talk join link
    
    Args:
        room_token: Room token/ID
        user_name: User's display name
    
    Returns:
        Join URL
    """
    # Nextcloud Talk link format
    return f"{NEXTCLOUD_URL}/call/{room_token}"

def add_user_to_room(room_token: str, user_id: str) -> bool:
    """
    Add a user to a Nextcloud Talk room
    
    Args:
        room_token: Room token
        user_id: Nextcloud user ID
    
    Returns:
        True if successful, False otherwise
    """
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v4/rooms/{room_token}/participants"
    
    params = {
        "newParticipant": user_id
    }
    
    headers = {
        "OCS-APIRequest": "true"
    }
    
    try:
        response = requests.post(
            url,
            json=params,
            auth=get_auth(),
            headers=headers,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get("ocs", {}).get("meta", {}).get("status") == "ok"
    
    except Exception as e:
        print(f"Error adding user to room: {e}")
        return False

def get_room_link(room_token: str) -> Dict[str, str]:
    """
    Get the direct link to join a Nextcloud Talk room
    
    Args:
        room_token: Room token
    
    Returns:
        Dictionary with join link
    """
    join_link = f"{NEXTCLOUD_URL}/call/{room_token}"
    
    return {
        "join_url": join_link,
        "room_token": room_token,
        "server_url": NEXTCLOUD_URL
    }

def delete_room(room_token: str) -> Dict[str, Any]:
    """
    Delete a Nextcloud Talk room
    
    Args:
        room_token: Room token
    
    Returns:
        Result dictionary
    """
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v4/rooms/{room_token}"
    
    headers = {
        "OCS-APIRequest": "true"
    }
    
    try:
        response = requests.delete(
            url,
            auth=get_auth(),
            headers=headers,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("ocs", {}).get("meta", {}).get("status") == "ok":
            return {
                "success": True,
                "message": "Room deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": data.get("ocs", {}).get("meta", {}).get("message", "Unknown error")
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_connection() -> Dict[str, Any]:
    """
    Test connection to Nextcloud server
    
    Returns:
        Connection status
    """
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v4/rooms"
    
    headers = {
        "OCS-APIRequest": "true"
    }
    
    try:
        response = requests.get(
            url,
            auth=get_auth(),
            headers=headers,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Connected to Nextcloud successfully",
            "server_url": NEXTCLOUD_URL
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to connect to Nextcloud: {str(e)}",
            "server_url": NEXTCLOUD_URL
        }
