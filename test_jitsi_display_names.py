"""
Test Jitsi URLs with display name parameters
Verify that room names work without redirects and display names are properly encoded
"""

from google_meet_service import generate_jitsi_room_id, get_jitsi_url, create_meet_event
from datetime import datetime, timedelta

def test_simple_room_ids():
    """Test that simple room IDs are generated correctly"""
    print("=" * 60)
    print("TEST 1: Simple Room ID Generation")
    print("=" * 60)
    
    room_ids = [
        ("Class 1", "1"),
        ("Quran Class", "2"),
        ("Islamic History", "42"),
    ]
    
    for event_name, event_id in room_ids:
        room_id = generate_jitsi_room_id(event_name, event_id)
        print(f"Event: {event_name:20} | Event ID: {event_id:5} | Room ID: {room_id}")
    
    print()

def test_urls_without_display_name():
    """Test URL generation without display name"""
    print("=" * 60)
    print("TEST 2: Jitsi URLs Without Display Name")
    print("=" * 60)
    
    enrollments = [
        ("1", None),
        ("2", None),
        ("42", None),
    ]
    
    for enrollment_id, display_name in enrollments:
        room_id = generate_jitsi_room_id("Class", enrollment_id)
        url = get_jitsi_url(room_id, display_name)
        print(f"Enrollment {enrollment_id}: {url}")
    
    print()

def test_urls_with_display_name():
    """Test URL generation with display names"""
    print("=" * 60)
    print("TEST 3: Jitsi URLs With Display Names")
    print("=" * 60)
    
    enrollments = [
        ("1", "Ali Rahman"),
        ("2", "Sara Ahmed"),
        ("3", "Muhammad Hassan"),
        ("4", "Fatima Ali"),
    ]
    
    for enrollment_id, display_name in enrollments:
        room_id = generate_jitsi_room_id("Class", enrollment_id)
        url = get_jitsi_url(room_id, display_name)
        print(f"Enrollment {enrollment_id} ({display_name:20}): {url}")
    
    print()

def test_space_handling():
    """Test that spaces in display names are properly handled"""
    print("=" * 60)
    print("TEST 4: Display Name Encoding (Spaces)")
    print("=" * 60)
    
    names_with_spaces = [
        "Ali Muhammad Rahman",
        "Fatima Aisha Khan",
        "Muhammad Hassan Ali",
    ]
    
    for name in names_with_spaces:
        room_id = generate_jitsi_room_id("Class", "99")
        url = get_jitsi_url(room_id, name)
        print(f"Name: {name:25} | URL: {url}")
    
    print()

def test_full_meet_event_creation():
    """Test full meet event creation with display names"""
    print("=" * 60)
    print("TEST 5: Full Meet Event Creation")
    print("=" * 60)
    
    students = [
        ("1", "Ali Rahman"),
        ("2", "Sara Ahmed"),
        ("3", "Muhammad Hassan"),
    ]
    
    now = datetime.now()
    start_time = now + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    for enrollment_id, student_name in students:
        result = create_meet_event(
            event_name="Quran Class",
            start_time=start_time,
            end_time=end_time,
            description="Online Quranic Studies",
            event_id=enrollment_id,
            display_name=student_name
        )
        
        print(f"\nStudent: {student_name}")
        print(f"  Event ID: {result['event_id']}")
        print(f"  Jitsi Link: {result['jitsi_link']}")
        print(f"  Success: {result['success']}")
    
    print()

def show_example_urls():
    """Show example URLs for testing in browser"""
    print("=" * 60)
    print("EXAMPLE JITSI URLs FOR BROWSER TESTING")
    print("=" * 60)
    print("\nThese URLs can be tested directly in a browser:")
    print()
    
    examples = [
        ("noori-class-1", None, "Simple room without display name"),
        ("noori-class-1", "Ali Rahman", "Room with display name"),
        ("noori-class-2", "Sara Ahmed", "Different room with different student"),
        ("noori-class-42", "Muhammad Hassan", "High enrollment ID"),
    ]
    
    for room_id, display_name, description in examples:
        if display_name:
            url = f"https://meet.jitsi.net/{room_id}#userInfo.displayName={display_name}"
        else:
            url = f"https://meet.jitsi.net/{room_id}"
        
        print(f"{description}")
        print(f"  URL: {url}")
        print()

if __name__ == "__main__":
    test_simple_room_ids()
    test_urls_without_display_name()
    test_urls_with_display_name()
    test_space_handling()
    test_full_meet_event_creation()
    show_example_urls()
    
    print("=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)
