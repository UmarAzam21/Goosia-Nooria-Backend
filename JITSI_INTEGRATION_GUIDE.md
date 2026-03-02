# Jitsi Meet Integration Guide

## Overview
Students and Teachers use **Jitsi Meet** for video conferencing. Meeting rooms are automatically created for each class enrollment using deterministic room IDs.

## URL Format
```
https://meet.jitsi.net/{room_id}
```

### Example
```
https://meet.jitsi.net/noorib9e224cc42
```

## How It Works

### 1. Class Enrollment
When a student enrolls in a course:
- Backend generates deterministic room ID from course name
- Room ID: `noori` + 10-char MD5 hash (lowercase)
- URL stored in `enrollment.zoom_link` and `class.zoom_link`
- Same course name = **same room ID** (consistent)

### 2. Student Joins Class
When student clicks "Join Class" button:

**Endpoint:** `POST /api/classes/{class_id}/join`

**Response:**
```json
{
  "success": true,
  "zoom_link": "https://meet.jitsi.net/noorib9e224cc42",
  "jitsi_url": "https://meet.jitsi.net/noorib9e224cc42",
  "meeting_id": "noorib9e224cc42",
  "jitsi_room": "noorib9e224cc42",
  "class_name": "Introduction to Python",
  "attendance_status": "present",
  "message": "Join the meeting at: https://meet.jitsi.net/noorib9e224cc42",
  "instructions": "Click the zoom_link or jitsi_url to join the meeting directly"
}
```

### 3. Direct Meeting Link Access
**Endpoint:** `GET /api/classes/{class_id}/open-meeting`

**Response:**
```json
{
  "meeting_url": "https://meet.jitsi.net/noorib9e224cc42",
  "room_id": "noorib9e224cc42",
  "class_name": "Introduction to Python",
  "message": "Click the meeting_url link OR visit this address in your Jitsi app"
}
```

## Frontend Implementation

### Option 1: Direct Link Click (Recommended)
```html
<a href="https://meet.jitsi.net/noorib9e224cc42" target="_blank">
  Join Meeting
</a>
```

When clicked, user is taken directly to the Jitsi meeting room (auto-joins).

### Option 2: Open in New Window
```javascript
const meetingUrl = "https://meet.jitsi.net/noorib9e224cc42";
window.open(meetingUrl, '_blank');
```

### Option 3: Embedded iframe (Advanced)
```html
<iframe 
  src="https://meet.jitsi.net/noorib9e224cc42?jwt={token}"
  width="100%"
  height="600"
  allow="camera; microphone; display-capture"
/>
```

## Room ID Format
- **Prefix:** `noori` (lowercase)
- **Hash:** 10-character MD5 hash (lowercase hex)
- **Total Length:** 15 characters
- **Valid Examples:**
  - `noorib9e224cc42`
  - `nooribf7e8a9c1d`
  - `nooribae32f1a5c2`

## Important Notes

### Auto-Join
- Simply visiting `https://meet.jitsi.net/{room_id}` automatically joins the room
- No manual room name entry needed
- No "Start meeting" button needed to be clicked
- First person creates the room, subsequent visitors join same room

### Room Persistence
- Rooms are ephemeral (auto-close when empty)
- Same room ID always leads to same meeting
- Deterministic from course name (reproducible)

### Browser Support
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile support (iOS, Android)
- No client installation needed

## Troubleshooting

### Issue: Landing on Jitsi Homepage
**Cause:** Room ID or URL format incorrect
**Solution:** 
- Verify URL format: `https://meet.jitsi.net/noorib9e224cc42`
- Ensure room ID is lowercase
- Check for spaces or special characters

### Issue: Room Not Found
**Cause:** Invalid room ID format
**Solution:**
- Room ID should be exactly: `noori` + 10-char hex
- Example: `noorib9e224cc42` ✅ (15 chars total)
- Invalid: `Noori` (mixed case) ❌
- Invalid: `noori123` (too short) ❌

### Issue: Permission Denied
**Cause:** Room created with specific password
**Solution:**
- Rooms auto-created by backend have no password
- Room ID is the only identifier needed

## API Endpoints

### Get My Classes
```
GET /api/classes/my-classes
```
Returns list of classes with `zoom_link` field

### Join Class (Mark Attendance)
```
POST /api/classes/{class_id}/join
```
Returns meeting details with full `zoom_link` URL

### Get Class Details
```
GET /api/classes/{class_id}
```
Returns class details including `zoom_link`

### Direct Meeting Link
```
GET /api/classes/{class_id}/open-meeting
```
Returns meeting URL optimized for direct joining

## Testing

### Test URL Generation
```python
from google_meet_service import generate_jitsi_room_id, get_jitsi_url

room_id = generate_jitsi_room_id("Introduction to Python")
url = get_jitsi_url(room_id)
print(url)  # https://meet.jitsi.net/noorib9e224cc42
```

### Test Direct Link
Copy this URL to browser:
```
https://meet.jitsi.net/noorib9e224cc42
```
Should auto-join the meeting room immediately.

## Security

- No authentication required at Jitsi level (handled by backend)
- Room IDs derived from course names (deterministic, not random)
- Attendee list visible within meeting
- Meeting ends when all participants leave
- No recording by default

---
**Last Updated:** February 21, 2026
**Version:** Jitsi Meet Integration v1.0
