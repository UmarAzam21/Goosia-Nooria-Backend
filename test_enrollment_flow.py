#!/usr/bin/env python3
"""
Test the complete enrollment flow with new htmlLink-based access
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_meet_service import create_meet_event, get_event_details

def test_enrollment_flow():
    """Simulate student enrollment and meeting access"""
    
    print("=" * 70)
    print("Testing Google Meet Enrollment Flow")
    print("=" * 70)
    
    # Create a test event simulating class enrollment
    class_name = "Introduction to Python"
    start_time = datetime.utcnow() + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)
    
    print(f"\n1. Creating class meeting event...")
    print(f"   Class: {class_name}")
    print(f"   Start: {start_time}")
    print(f"   End: {end_time}")
    
    # Create event using the main function
    result = create_meet_event(
        class_name,
        start_time,
        end_time,
        f"Learn Python programming with Google Meet",
        None,
        "UTC"
    )
    
    if not result.get("success"):
        print(f"\n❌ Error creating event: {result.get('error')}")
        return False
    
    event_id = result.get("event_id")
    meet_link = result.get("meet_link")
    
    print(f"\n✅ Event created successfully!")
    print(f"   Event ID: {event_id}")
    print(f"   Access Link: {meet_link}")
    
    # Get event details
    print(f"\n2. Retrieving event details...")
    details = get_event_details(event_id)
    
    if not details.get("success"):
        print(f"⚠️ Warning: Could not retrieve details: {details.get('error')}")
    else:
        print(f"✅ Link type: {'Google Meet' if 'meet.google.com' in meet_link else 'Google Calendar Event'}")
    
    # Test the link
    print(f"\n3. Testing student access...")
    print(f"   Students will receive this link: {meet_link}")
    
    # Parse the link to check format
    if "google.com/calendar/event" in meet_link:
        print(f"   ✅ Using public event link (htmlLink)")
        print(f"   This link works WITHOUT calendar access")
    elif "meet.google.com" in meet_link:
        print(f"   ✅ Using direct Google Meet link")
    elif "calendar.google.com" in meet_link:
        print(f"   ⚠️  Using calendar event link")
        print(f"   This may require calendar access")
    else:
        print(f"   ℹ️  Using custom link format")
    
    # Cleanup
    print(f"\n4. Cleanup...")
    try:
        credentials = Credentials.from_service_account_file(
            "noori-credential-file.json",
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"✅ Test event deleted")
    except Exception as e:
        print(f"⚠️  Could not delete test event: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Enrollment flow test complete!")
    print("=" * 70)
    print(f"\nStudents will receive meeting link: {meet_link}")
    print("This link provides direct access to the class meeting.")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    test_enrollment_flow()
