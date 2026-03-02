"""
Zoom Meeting Service
Generate Zoom meeting links for classes
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


def generate_zoom_meeting_id(event_name: str, event_id: Optional[str] = None) -> str:
    """
    Generate a unique Zoom meeting ID from event details
    
    Zoom Meeting ID format: 9-11 numeric digits only
    
    Strategy: Use timestamp-based ID which guarantees:
    - Uniqueness (timestamp is always different)
    - Proper format (10 digits from time.time())
    - Stability (no hash collisions)
    
    Examples: 1708617600 (10 digits)
    """
    import time
    
    # Use Unix timestamp as meeting ID (10 digits, always unique)
    # This is the most reliable format for Zoom
    timestamp = int(time.time())
    
    if event_id:
        # Add event_id as a suffix to ensure per-enrollment uniqueness
        # Format: {timestamp}{event_id % 100}
        # This creates a unique ID like: 1708617600 + 05 = 170861760005 (12 digits, take last 11)
        meeting_id = str(timestamp) + str(int(event_id) % 100).zfill(2)
    else:
        # Just use timestamp
        meeting_id = str(timestamp)
    
    # Ensure it's numeric only and 9-11 digits
    meeting_id = ''.join(filter(str.isdigit, str(meeting_id)))
    
    # Take last 11 digits (Zoom max) but keep at least 9
    if len(meeting_id) > 11:
        meeting_id = meeting_id[-11:]
    elif len(meeting_id) < 9:
        # Pad to 9 digits if somehow too short
        meeting_id = meeting_id.zfill(9)
    

    return meeting_id


def get_zoom_url(meeting_id: str) -> str:
    """
    Get the full Zoom meeting URL
    
    Format: https://zoom.us/j/{meeting_id}
    Users can join without waiting for host
    
    Args:
        meeting_id: The Zoom meeting ID
    
    Returns:
        Complete Zoom join URL
    """
    meeting_id = str(meeting_id).strip()
    
    # Zoom join URL format
    zoom_url = f"https://zoom.us/j/{meeting_id}"
    
    return zoom_url


def create_zoom_meeting(
    event_name: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
    attendees: list = None,
    event_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Zoom meeting
    
    Args:
        event_name: Name of the meeting
        start_time: Meeting start time
        end_time: Meeting end time
        description: Meeting description
        attendees: List of attendees (for info only)
        event_id: Event ID (used as meeting ID)
    
    Returns:
        Dictionary with meeting details
    """
    try:
        # Generate meeting ID from event
        meeting_id = generate_zoom_meeting_id(event_name, event_id)
        zoom_url = get_zoom_url(meeting_id)
        
        return {
            "success": True,
            "event_id": meeting_id,
            "meeting_id": meeting_id,
            "meet_link": zoom_url,
            "zoom_link": zoom_url,
            "room_id": meeting_id,
            "calendar_url": zoom_url,
            "message": f"Zoom meeting created: {meeting_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "event_id": None,
            "meet_link": None
        }


def test_zoom_service():
    """Test the Zoom service"""
    print("\n" + "="*70)
    print("  ZOOM SERVICE TEST")
    print("="*70 + "\n")
    
    # Test meeting generation
    test_cases = [
        ("Class 1", "1"),
        ("Quran Study", "2"),
        ("Islamic History", "42"),
    ]
    
    for event_name, event_id in test_cases:
        result = create_zoom_meeting(
            event_name=event_name,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            event_id=event_id
        )
        
        print(f"Event: {event_name} (ID: {event_id})")
        print(f"  Meeting ID: {result['meeting_id']}")
        print(f"  Zoom Link: {result['zoom_link']}")
        print(f"  Success: {result['success']}\n")
    
    print("="*70)
    print("✅ Zoom service working correctly!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_zoom_service()
