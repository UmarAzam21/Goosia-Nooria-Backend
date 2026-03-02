"""
Simplified Jitsi Meet service for video conferencing
Removes Google Calendar API dependency - uses only Jitsi Meet
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import quote


def generate_jitsi_room_id(event_name: str, event_id: Optional[str] = None) -> str:
    """
    Generate a deterministic Jitsi room ID from event details
    Room ID format: simple-readable-format for direct auto-join
    
    Args:
        event_name: Name of the class/event
        event_id: Optional event ID (for enrollment/class ID)
    
    Returns:
        Deterministic room ID suitable for Jitsi URL - auto-joins when visited
    """
    # Jitsi room names must be URL-safe and work best with simple alphanumeric + hyphens
    # If we have an event_id (enrollment ID), use that as primary identifier
    if event_id:
        # Format: noori-class-{enrollment_id}
        # Example: noori-class-1, noori-class-123, etc.
        room_id = f"noori-class-{event_id}".lower()
    else:
        # Fallback: create from event name with hash for uniqueness
        # Make room name shorter and simpler for Jitsi
        clean_name = event_name.lower().replace(" ", "-")[:20]  # Max 20 chars, clean format
        hash_input = f"noori_{event_name}".encode()
        hash_short = hashlib.md5(hash_input).hexdigest()[:6]
        room_id = f"noori-{clean_name}-{hash_short}"
    
    return room_id


def get_jitsi_url(room_id: str, display_name: Optional[str] = None) -> str:
    """
    Get the full Jitsi Meet URL for a room ID
    
    Simple format: Just the room ID in the path
    This ensures Jitsi opens the meeting room directly without redirecting.
    
    Parameters:
    - room_id: The Jitsi room ID (e.g., "noori-class-1")
    - display_name: Optional user display name (not used in URL to avoid conflicts)
    
    Returns:
    - Simple Jitsi URL: https://meet.jitsi.net/{room_id}
    
    Note: Room ID in path causes auto-join to the meeting room.
    Simple format avoids redirect issues.
    """
    # Ensure room_id is lowercase and valid - MUST be simple alphanumeric with hyphens only
    room_id = str(room_id).lower().strip()
    
    # Remove any non-alphanumeric characters except hyphens
    # This prevents Jitsi from rejecting the room name
    room_id = ''.join(c for c in room_id if c.isalnum() or c == '-')
    
    # Simple URL - no parameters whatsoever
    # Jitsi requires room names to be simple for direct access
    base_url = f"https://meet.jitsi.net/{room_id}"
    
    return base_url


def create_meet_event(
    event_name: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
    attendees: list = None,
    event_id: Optional[str] = None,
    display_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Jitsi Meet event
    
    Args:
        event_name: Name of the event
        start_time: Event start time
        end_time: Event end time
        description: Event description
        attendees: List of attendees (for info only, not used)
        event_id: Optional event ID (for compatibility)
        display_name: Optional display name for auto-identification in the room
    
    Returns:
        Dictionary with meeting details
    """
    try:
        # Generate room ID from event name
        room_id = generate_jitsi_room_id(event_name, event_id)
        jitsi_url = get_jitsi_url(room_id, display_name)
        
        return {
            "success": True,
            "event_id": room_id,
            "meet_link": jitsi_url,
            "room_id": room_id,
            "jitsi_link": jitsi_url,
            "calendar_url": jitsi_url,
            "message": f"Jitsi room created: {room_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "event_id": None,
            "meet_link": None
        }

    
def get_event_details(event_id: str) -> Dict[str, Any]:
    """
    Get event details from event ID (room ID)
    
    Args:
        event_id: The room ID
    
    Returns:
        Dictionary with event details
    """
    try:
        jitsi_url = get_jitsi_url(event_id)
        return {
            "success": True,
            "event_id": event_id,
            "meet_link": jitsi_url,
            "jitsi_link": jitsi_url,
            "room_id": event_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "event_id": None,
            "meet_link": None
        }


def test_connection() -> Dict[str, Any]:
    """
    Test the Jitsi service (no API calls needed)
    
    Returns:
        Dictionary with connection status
    """
    try:
        # Test room creation
        test_result = create_meet_event(
            event_name="Test Event",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        return {
            "status": "success",
            "message": "Jitsi service is working",
            "test_room_id": test_result.get("room_id"),
            "test_url": test_result.get("meet_link")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Jitsi service error: {str(e)}"
        }


def update_event(
    event_id: str,
    event_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a Jitsi meeting (stub - Jitsi rooms don't need updates)
    
    Args:
        event_id: Room ID
        event_name: New name (ignored for Jitsi)
        start_time: New start time (ignored)
        end_time: New end time (ignored)
        description: New description (ignored)
    
    Returns:
        Dictionary with update result
    """
    # Jitsi rooms are ephemeral and don't need updates
    # Return success for API compatibility
    return {
        "success": True,
        "event_id": event_id,
        "message": "Jitsi room URL remains the same"
    }


def delete_event(event_id: str) -> Dict[str, Any]:
    """
    Delete a Jitsi meeting (stub - Jitsi rooms auto-close)
    
    Args:
        event_id: Room ID
    
    Returns:
        Dictionary with delete result
    """
    # Jitsi rooms are ephemeral and auto-close when empty
    # No explicit deletion needed
    return {
        "success": True,
        "event_id": event_id,
        "message": "Jitsi room will auto-close when empty"
    }


if __name__ == "__main__":
    # Test the service
    print("Testing Jitsi Meet Service")
    print("=" * 50)
    
    # Test connection
    connection_status = test_connection()
    print(f"Connection: {connection_status['status']}")
    print(f"Test Room: {connection_status.get('test_room_id')}")
    print(f"Test URL: {connection_status.get('test_url')}")
    print()
    
    # Test event creation
    from datetime import timedelta
    result = create_meet_event(
        event_name="Introduction to Python",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        description="Learn Python basics"
    )
    
    print("Event Creation:")
    print(f"Success: {result['success']}")
    print(f"Room ID: {result.get('event_id')}")
    print(f"Join URL: {result.get('meet_link')}")
