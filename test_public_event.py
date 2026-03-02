#!/usr/bin/env python3
"""
Test Google Calendar public event accessibility.
When an event is marked as 'public', Google Calendar should provide
a way to access it without needing calendar access.
"""

import os
import json
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

GOOGLE_CREDENTIALS_FILE = "noori-credential-file.json"

def test_public_event_link():
    """Create a public event and get direct access link"""
    try:
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Create public event
        now = datetime.utcnow()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=1)
        
        event = {
            "summary": "Public Test Event",
            "description": "Testing public event access",
            "start": {
                "dateTime": start.isoformat() + "Z",
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end.isoformat() + "Z",
                "timeZone": "UTC",
            },
            "visibility": "public"
        }
        
        result = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        event_id = result.get("id")
        html_link = result.get("htmlLink")
        
        print("Event Created Successfully!")
        print(f"Event ID: {event_id}")
        print(f"Event Link (from API): {html_link}")
        print(f"Visibility: {result.get('visibility')}")
        print(f"\nAlternative Links:")
        print(f"1. Calendar Event: https://calendar.google.com/calendar/u/0/r/events/{event_id}")
        print(f"2. API HTML Link: {html_link}")
        
        # Check all response keys
        print(f"\nAll response keys containing 'link' or 'url':")
        for key in result.keys():
            if 'link' in key.lower() or 'url' in key.lower():
                print(f"  {key}: {result[key]}")
        
        # Cleanup
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print("\nEvent cleaned up")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_public_event_link()
