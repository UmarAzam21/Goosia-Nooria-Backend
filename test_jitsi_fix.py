#!/usr/bin/env python
"""Test script to verify Jitsi room URLs work correctly"""

from google_meet_service import create_meet_event, generate_jitsi_room_id, get_jitsi_url
from datetime import datetime, timedelta

print("Testing Jitsi Room Generation")
print("=" * 60)

# Test 1: Room ID generation
room_id = generate_jitsi_room_id("Introduction to Python")
print(f"\n1. Room ID Generation:")
print(f"   Event: Introduction to Python")
print(f"   Generated ID: {room_id}")
print(f"   Format valid: {room_id.startswith('noori') and len(room_id) == 18}")

# Test 2: URL generation
url = get_jitsi_url(room_id)
print(f"\n2. Jitsi URL Generation:")
print(f"   URL: {url}")
print(f"   Expected: https://meet.jitsi.net/{room_id}")
print(f"   Match: {url == f'https://meet.jitsi.net/{room_id}'}")

# Test 3: Full event creation
result = create_meet_event(
    event_name="Python Basics",
    start_time=datetime.now(),
    end_time=datetime.now() + timedelta(hours=1),
    description="Learn Python"
)
print(f"\n3. Full Event Creation:")
print(f"   Success: {result['success']}")
print(f"   Event ID: {result.get('event_id')}")
print(f"   Meet Link: {result.get('meet_link')}")
print(f"   Room ID: {result.get('room_id')}")

print("\n" + "=" * 60)
print("DIRECT JOIN INSTRUCTIONS:")
print(f"Students can click directly on: {result.get('meet_link')}")
print("This should take them straight to the Jitsi meeting room.")
print("=" * 60)
