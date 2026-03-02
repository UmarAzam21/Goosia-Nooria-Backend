#!/usr/bin/env python3
"""
Create a real Google Calendar event that you can see in your calendar
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def create_test_meeting():
    """Create a visible test meeting in the calendar"""
    
    try:
        cred_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "noori-credential-file.json")
        
        credentials = Credentials.from_service_account_file(
            cred_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Create event TOMORROW at 2:00 PM (so it's visible in calendar)
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        import hashlib
        event_hash = hashlib.md5(f"Test{start.isoformat()}".encode()).hexdigest()[:8]
        jitsi_link = f"https://meet.jitsi.net/Noori{event_hash}"
        
        event = {
            "summary": "✅ Test Class - Click to Join",
            "description": f"""Test Meeting with Google Meet Integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 HOW TO JOIN THE MEETING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Option 1: Google Meet (Recommended)
   1. Refresh this event page (wait 1-2 minutes)
   2. Look for 'Join with Google Meet' button
   3. Click to join the video call

🔗 Option 2: Backup Video Room (Instant)
   {jitsi_link}

⏰ Meeting Details:
   📅 Date: {start.strftime('%B %d, %Y')}
   ⏱️  Time: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}
   🌍 Timezone: UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Troubleshooting:
   • If 'Join' button doesn't appear, refresh
   • Use the Jitsi link above if needed
   • Contact support if you have issues
""",
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": "UTC",
            },
            "visibility": "public",
            "transparency": "opaque",
            "conferenceData": {
                "createRequest": {
                    "requestId": f"test-{int(start.timestamp())}",
                    "conferenceSolution": {
                        "key": {
                            "conferenceSolution": "hangoutsMeet"
                        }
                    }
                }
            }
        }
        
        print(f"Creating test meeting...")
        print(f"📅 Date: {start.strftime('%B %d, %Y')}")
        print(f"⏱️  Time: {start.strftime('%H:%M')} UTC")
        
        result = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        event_id = result.get("id")
        calendar_link = result.get("htmlLink")
        
        print(f"\n✅ EVENT CREATED SUCCESSFULLY!")
        print(f"\n📌 Event Details:")
        print(f"   ID: {event_id}")
        print(f"   Title: {result.get('summary')}")
        print(f"   Status: {result.get('status')}")
        
        print(f"\n🔗 Access Links:")
        print(f"   Calendar: {calendar_link}")
        print(f"   Jitsi Backup: {jitsi_link}")
        
        print(f"\n📱 What to do next:")
        print(f"   1. Go to Google Calendar")
        print(f"   2. Look for '{result.get('summary')}' on {start.strftime('%B %d')}")
        print(f"   3. Click to open the event")
        print(f"   4. You'll see options to join via Google Meet or Jitsi")
        
        print(f"\n⏰ Timeline:")
        print(f"   - Google Meet button: appears in 1-2 minutes")
        print(f"   - Jitsi link: available immediately (in description)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Creating Test Meeting in Google Calendar")
    print("="*60 + "\n")
    
    create_test_meeting()
    
    print("\n" + "="*60)
    print("Done! Check your Google Calendar")
    print("="*60 + "\n")
