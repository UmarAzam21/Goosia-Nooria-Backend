# Google Meet Integration Setup Guide

## Overview
This backend uses **Google Meet** (via Google Calendar API) for video conferencing.

## Prerequisites
1. Google Cloud Platform (GCP) account
2. Google Calendar API enabled
3. Service Account or OAuth 2.0 credentials

## Setup Steps

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a Project** → **New Project**
3. Name: "Noori Meeting Platform"
4. Click **Create**

### Step 2: Enable APIs
1. In the GCP console, go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click on it and press **Enable**
4. Search for "Google Meet API" (if available in your region)
5. Click on it and press **Enable**

### Step 3: Create Service Account (Recommended for Backend)
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in the service account details:
   - Service account name: `noori-api`
   - Click **Create and Continue**
4. Grant roles:
   - Click **Add another role**
   - Search for "Calendar"
   - Select **Editor**
   - Click **Continue**
5. Click **Create Key** → **JSON**
6. Save the JSON file as `google-credentials.json` in your backend directory
7. Click **Done**

### Step 4: Set Up Calendar Access
1. In GCP console, go to **APIs & Services** → **Credentials**
2. Find your Service Account in the list
3. Click on it to view details
4. Copy the **Service Account Email** (e.g., `noori-api@project-id.iam.gserviceaccount.com`)
5. Open [Google Calendar](https://calendar.google.com)
6. Share your calendar with the service account email:
   - Settings → Calendars → Select calendar
   - Share with people → Add the service account email
   - Give Editor permissions

### Step 5: Update Environment Variables
Update your `.env` file:
```dotenv
GOOGLE_CREDENTIALS_FILE=google-credentials.json
GOOGLE_CALENDAR_ID=primary
```

Or use a specific calendar ID:
```dotenv
GOOGLE_CREDENTIALS_FILE=google-credentials.json
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

### Step 6: Test Connection
Run this endpoint to verify setup:
```bash
curl http://localhost:5000/api/health/google-meet
```

Expected response:
```json
{
  "success": true,
  "message": "Connected to Google Calendar successfully",
  "calendars_count": 1
}
```

## API Endpoints

### Get Join URL for a Class
```
GET /api/classes/{class_id}/bbb-join-url
```

Response:
```json
{
  "join_url": "https://meet.google.com/abc-defg-hij",
  "event_id": "event123",
  "event_name": "Nazra - Student Name",
  "class_name": "Nazra",
  "start_time": "2026-02-19T09:00:00",
  "end_time": "2026-02-19T10:00:00",
  "is_organizer": true
}
```

### Create a Meeting Event
```
POST /api/meetings/create
```

Body:
```json
{
  "class_id": 1,
  "meeting_name": "Nazra Class",
  "start_time": "2026-02-20T10:00:00",
  "end_time": "2026-02-20T11:00:00",
  "description": "Online Quran class"
}
```

### Get Event Details
```
GET /api/meetings/{event_id}/info
```

### Update Event
```
POST /api/meetings/{event_id}/update
```

Body:
```json
{
  "meeting_name": "Updated Class Name",
  "start_time": "2026-02-20T11:00:00",
  "end_time": "2026-02-20T12:00:00"
}
```

### Delete Event
```
POST /api/meetings/{event_id}/delete
```

## How It Works

1. **Event Creation**: When students enroll in courses, a Google Meet is automatically created in your calendar
2. **Automatic Invitations**: Students are automatically added as attendees
3. **Meet Link**: Google Calendar automatically creates a Google Meet link for the event
4. **Easy Access**: Students get direct links via the API endpoint

## Features

✅ Video conferencing with Google Meet  
✅ Automatic calendar integration  
✅ Recording (Google Meet premium feature)  
✅ Screen sharing  
✅ Chat and hand raise  
✅ Participant management  
✅ Works with all Google Workspace features  

## Troubleshooting

### "File not found: google-credentials.json"
- Ensure the JSON file is in your backend root directory
- Check file name spelling and capitalization
- Verify file path in `.env` is correct

### "401 Unauthorized - Invalid grant"
- Service account not added to calendar
- Check calendar sharing permissions
- Regenerate service account key

### "403 Forbidden - User does not have access"
- Calendar not shared with service account email
- Check sharing settings in Google Calendar
- Verify service account has Editor role

### "Failed to create Google Meet event"
- Google Calendar API not enabled
- Service account doesn't have Calendar permissions
- Check GCP project quotas and limits

## Upgrading from Other Platforms

If migrating from Jitsi/BigBlueButton/Nextcloud:
1. Replace credentials in `.env`
2. New enrollments will automatically use Google Meet
3. Existing links can be kept in database or migrated separately

## Advanced Configuration

### Using OAuth 2.0 Instead of Service Account
For user-based authentication:
1. Create OAuth 2.0 Desktop Application credentials
2. Download client secret JSON
3. Implement OAuth flow in your backend
4. Update `google_meet_service.py` to use user credentials

### Custom Calendar
To use a specific calendar other than primary:
```dotenv
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

## Support

- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Google Meet API Docs](https://developers.google.com/meet)
- [Google Cloud Support](https://cloud.google.com/support)

## Security Notes

⚠️ Keep `google-credentials.json` secret!
- Never commit to version control
- Use `.gitignore` to exclude it
- Use different service accounts for dev/prod
- Rotate keys regularly
