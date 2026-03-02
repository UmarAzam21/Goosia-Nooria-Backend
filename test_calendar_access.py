#!/usr/bin/env python3
"""
Test if the service account's primary calendar is publicly accessible
by checking the ACL (Access Control List) settings
"""

import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load configuration
GOOGLE_CREDENTIALS_FILE = "noori-credential-file.json"
GOOGLE_CALENDAR_ID = "primary"

def check_calendar_acl():
    """Check if calendar is public via ACL"""
    try:
        # Load credentials
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        print("=" * 60)
        print("Calendar Access Control List (ACL) Check")
        print("=" * 60)
        
        # Get ACL entries
        acl_list = service.acl().list(calendarId='primary').execute()
        
        print(f"\nACL Entries for primary calendar:")
        print(f"Total entries: {len(acl_list.get('items', []))}\n")
        
        has_public = False
        for item in acl_list.get('items', []):
            scope = item.get('scope', {})
            role = item.get('role')
            
            scope_type = scope.get('type')
            scope_email = scope.get('email', 'N/A')
            scope_domain = scope.get('domain', 'N/A')
            
            print(f"Entry:")
            print(f"  Type: {scope_type}")
            print(f"  Role: {role}")
            if scope_email != 'N/A':
                print(f"  Email: {scope_email}")
            if scope_domain != 'N/A':
                print(f"  Domain: {scope_domain}")
            
            if scope_type == 'default' and role == 'reader':
                has_public = True
                print(f"  ✅ This makes the calendar PUBLIC (reader)")
            
            print()
        
        if has_public:
            print("✅ RESULT: Calendar is PUBLIC and readable by anyone")
        else:
            print("❌ RESULT: Calendar is NOT public")
            print("\nAttempting to make it public...")
            
            try:
                rule = {
                    'scope': {
                        'type': 'default'
                    },
                    'role': 'reader'
                }
                result = service.acl().insert(calendarId='primary', body=rule).execute()
                print("✅ Successfully made calendar public")
                return True
            except Exception as e:
                print(f"❌ Failed to make calendar public: {e}")
                return False
        
        return has_public
    
    except Exception as e:
        print(f"Error checking calendar ACL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_access():
    """Create a test event and verify it's accessible"""
    try:
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        print("=" * 60)
        print("Test Event Creation and Access")
        print("=" * 60)
        
        # Create test event
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        event = {
            "summary": f"Test Public Event - {now.isoformat()}",
            "description": "This is a test event to verify calendar access",
            "start": {
                "dateTime": start_time.isoformat() + "Z",
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat() + "Z",
                "timeZone": "UTC",
            },
            "visibility": "public",
            "conferenceData": {
                "createRequest": {
                    "requestId": f"test-{start_time.timestamp()}",
                    "conferenceSolution": {
                        "key": {
                            "conferenceSolution": "hangoutsMeet"
                        }
                    }
                }
            }
        }
        
        result = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        event_id = result.get("id")
        
        print(f"\n✅ Test event created: {event_id}")
        
        # Get calendar details
        calendar = service.calendars().get(calendarId='primary').execute()
        calendar_email = calendar.get('id')
        
        print(f"\nCalendar Details:")
        print(f"  Calendar ID: {calendar_email}")
        print(f"  Name: {calendar.get('summary', 'N/A')}")
        print(f"  Timezone: {calendar.get('timeZone', 'N/A')}")
        
        # Try to access the event
        event_details = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        print(f"\nEvent Details:")
        print(f"  Title: {event_details.get('summary')}")
        print(f"  Visibility: {event_details.get('visibility')}")
        print(f"  Status: {event_details.get('status')}")
        
        # Generate access links
        calendar_link = f"https://calendar.google.com/calendar/u/0/r/events/{event_id}"
        
        print(f"\nAccess Links:")
        print(f"  Calendar Link: {calendar_link}")
        
        # Check for conference data
        if "conferenceData" in event_details:
            entry_points = event_details["conferenceData"].get("entryPoints", [])
            if entry_points:
                print(f"\n  Google Meet Conference Data:")
                for entry in entry_points:
                    print(f"    Type: {entry.get('entryPointType')}")
                    print(f"    URI: {entry.get('uri')}")
            else:
                print(f"\n  ⚠️ Conference data exists but no entry points (Meet link will be generated by Google Calendar)")
        else:
            print(f"\n  ℹ️ No conference data (Google Calendar will show 'Join with Google Meet' button)")
        
        # Cleanup
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"\n✅ Test event cleaned up")
        except:
            print(f"\n⚠️ Could not delete test event")
        
        return True
    
    except Exception as e:
        print(f"Error during event test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Calendar Access & Google Meet Configuration Test")
    print("=" * 60 + "\n")
    
    # Check ACL
    acl_ok = check_calendar_acl()
    
    # Test event creation
    event_ok = test_event_access()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if acl_ok and event_ok:
        print("✅ Calendar is properly configured and public")
        print("✅ Students should be able to join class meetings")
    else:
        print("⚠️ There may be issues with calendar access")
        print("Please check the output above for details")
    
    print("=" * 60 + "\n")
