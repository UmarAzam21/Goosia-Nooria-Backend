#!/usr/bin/env python3
"""
Diagnostic script to test Google Calendar API setup
Run this to troubleshoot Google Meet integration issues
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
def load_env_file():
    """Load .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

# Load .env before importing anything else
load_env_file()

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuration
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_credentials_file():
    """Test if credentials file exists and is valid JSON"""
    print_header("1. Checking Credentials File")
    
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print(f"❌ FAILED: Credentials file not found")
        print(f"   Expected path: {os.path.abspath(GOOGLE_CREDENTIALS_FILE)}")
        print(f"   Current directory: {os.getcwd()}")
        return False
    
    print(f"✅ Credentials file found: {GOOGLE_CREDENTIALS_FILE}")
    
    try:
        with open(GOOGLE_CREDENTIALS_FILE, 'r') as f:
            cred_data = json.load(f)
        print(f"✅ Credentials file is valid JSON")
        print(f"\n   Service Account Email: {cred_data.get('client_email')}")
        print(f"   Project ID: {cred_data.get('project_id')}")
        print(f"   Key ID: {cred_data.get('private_key_id')}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Credentials file is not valid JSON")
        print(f"   Error: {e}")
        return False

def test_authentication():
    """Test if we can authenticate with Google API"""
    print_header("2. Testing Authentication")
    
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print("❌ FAILED: Credentials file missing (skip)")
        return False
    
    try:
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )
        print(f"✅ Service account credentials loaded successfully")
        print(f"   Scopes: Calendar read/write enabled")
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not load credentials")
        print(f"   Error: {e}")
        return False

def test_calendar_service():
    """Test if we can build the Calendar service"""
    print_header("3. Building Google Calendar Service")
    
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print("❌ FAILED: Credentials file missing (skip)")
        return False
    
    try:
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        print(f"✅ Google Calendar service built successfully")
        return service
    except Exception as e:
        print(f"❌ FAILED: Could not build Calendar service")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_list_calendars(service):
    """Test if we can list calendars"""
    print_header("4. Listing Available Calendars")
    
    if not service:
        print("❌ FAILED: Calendar service not available (skip)")
        return False
    
    try:
        result = service.calendarList().list().execute()
        items = result.get('items', [])
        
        if not items:
            print(f"⚠️  WARNING: No calendars found")
            print(f"   The service account may not have any calendars yet")
            return False
        
        print(f"✅ Successfully connected to Google Calendar API")
        print(f"   Total calendars: {len(items)}\n")
        
        for i, cal in enumerate(items, 1):
            cal_id = cal.get('id')
            cal_summary = cal.get('summary', 'N/A')
            cal_primary = " [PRIMARY]" if cal.get('primary') else ""
            print(f"   {i}. {cal_summary}")
            print(f"      ID: {cal_id}{cal_primary}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not list calendars")
        print(f"   Error: {e}")
        
        # Provide specific troubleshooting
        error_str = str(e)
        if "403" in error_str:
            print(f"\n   Troubleshooting: Calendar API may not be enabled in GCP project")
            print(f"   Go to: https://console.cloud.google.com/apis/api/calendar/overview")
        elif "401" in error_str:
            print(f"\n   Troubleshooting: Authentication failed")
            print(f"   Verify the service account credentials are valid")
        
        return False

def test_create_event(service):
    """Test if we can create a calendar event with Google Meet"""
    print_header("5. Creating Test Calendar Event with Google Meet")
    
    if not service:
        print("[ERROR] Calendar service not available (skip)")
        return False
    
    try:
        # Create test event
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        event = {
            "summary": "Test Google Meet Event - noori Portal",
            "description": "This is a test event for class meetings",
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
        
        print(f"   Creating calendar event...")
        print(f"   Calendar ID: {GOOGLE_CALENDAR_ID}")
        print(f"   Event: Test Google Meet Event - noori Portal")
        print(f"   Time: {start_time} to {end_time}")
        
        result = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        event_id = result.get("id")
        
        print(f"\n[OK] Event created successfully!")
        print(f"   Event ID: {event_id}")
        print(f"   Status: {result.get('status')}")
        
        # Extract Google Meet link if generated
        meet_link = None
        if "conferenceData" in result:
            entry_points = result["conferenceData"].get("entryPoints", [])
            for entry in entry_points:
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break
        
        # Generate calendar link
        calendar_link = f"https://calendar.google.com/calendar/u/0/r/events/{event_id}"
        
        if meet_link:
            print(f"\n   ✅ Google Meet Link Generated!")
            print(f"   Direct Link: {meet_link}")
        else:
            print(f"\n   ℹ️ Google Meet link not generated yet")
        
        print(f"\n   Google Calendar Link:")
        print(f"   {calendar_link}")
        print(f"\n   How it works:")
        if meet_link:
            print(f"   1. Student can click direct Meet link: {meet_link}")
        else:
            print(f"   1. Student clicks the calendar link")
            print(f"   2. Opens Google Calendar event page")
            print(f"   3. Google Calendar shows 'Join with Google Meet' button")
            print(f"   4. Student clicks to join the video call")
        
        # Try to delete the test event
        try:
            service.events().delete(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=event_id
            ).execute()
            print(f"\n   [OK] Test event deleted")
        except:
            print(f"\n   [INFO] Could not delete test event (may need manual cleanup)")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Could not create event")
        print(f"   Error: {e}")
        
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "#"*60)
    print("# Google Calendar API Diagnostic Tool")
    print("# noori Portal Backend")
    print("#"*60)
    
    print(f"\nConfiguration:")
    print(f"  Credentials File: {os.getenv('GOOGLE_CREDENTIALS_FILE', 'Not set')}")
    print(f"  Calendar ID: {os.getenv('GOOGLE_CALENDAR_ID', 'Not set')}")
    print(f"  Working Directory: {os.getcwd()}")
    
    # Run tests
    if not test_credentials_file():
        print_header("FAILED: Cannot proceed without credentials file")
        return
    
    if not test_authentication():
        print_header("FAILED: Authentication not working")
        return
    
    service = test_calendar_service()
    if not service:
        print_header("FAILED: Cannot build Calendar service")
        return
    
    if not test_list_calendars(service):
        print_header("WARNING: No calendars accessible")
        # Don't fail here, continue to event creation test
    
    if not test_create_event(service):
        print_header("FAILED: Cannot create events")
        return
    
    print_header("✅ All Tests Passed!")
    print("\nYour Google Calendar API setup is working correctly.")
    print("You should now be able to use Google Meet for class meetings.\n")

if __name__ == "__main__":
    main()
