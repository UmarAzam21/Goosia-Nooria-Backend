
# Zoom API Setup Guide

## Overview
Instead of generating fake meeting IDs, we now use **Zoom's real API** to create actual meetings that are valid in Zoom.

## What Changed
- ✅ Before: Generated fake meeting IDs like `77175054301` (Zoom rejects these)
- ✅ Now: Create real meetings via Zoom API and get actual meeting IDs from Zoom

## How to Get Zoom API Credentials

### Step 1: Create Zoom Developer Account
1. Go to https://marketplace.zoom.us/
2. Sign in with your Zoom account (create one if needed)
3. Click on "Build" → "Create an app"

### Step 2: Create Server-to-Server OAuth App
1. Select "Server-to-Server OAuth" as the app type
2. Fill in app name: "Noori Online Classes"
3. Click "Create"

### Step 3: Get Your Credentials
1. You'll see three credentials:
   - **Client ID** (looks like: `ABC123xyz...`)
   - **Client Secret** (looks like: `ABC123xyz...`)
   - **Account ID** (looks like: `ABC123xyz...`)

2. Copy these values

### Step 4: Add to .env File
Edit your `.env` file and add:

```env
ZOOM_CLIENT_ID=paste_your_client_id_here
ZOOM_CLIENT_SECRET=paste_your_client_secret_here
ZOOM_ACCOUNT_ID=paste_your_account_id_here
```

### Step 5: Install Required Package
Run in terminal:
```bash
pip install PyJWT zoom-python-sdk
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 6: Test Connection
Run:
```bash
python zoom_api_service.py
```

Expected output:
```
✅ Zoom credentials configured
✅ Test meeting created!
   Meeting ID: 12345678901
   Join URL: https://zoom.us/j/12345678901
✅ Test meeting deleted
```

## How It Works

### When Enrollment is Created:
```
1. Student enrolls in course
   ↓
2. System calls Zoom API: Create Meeting
   ↓
3. Zoom returns real meeting ID + join URL
   ↓
4. Database stores: zoom_link = "https://zoom.us/j/12345678901"
   ↓
5. Student clicks "Join Class"
   ↓
6. Opens https://zoom.us/j/12345678901 in Zoom
   ↓
7. ✅ Meeting exists and opens successfully!
```

## Without API Credentials (Fallback Mode)

If you don't set up Zoom API:
- System will fall back to old behavior
- Generated meeting IDs will still not work in Zoom
- Students will get "Invalid meeting ID" error

## Once Credentials Are Set Up

All new enrollments will automatically:
1. Create real Zoom meetings
2. Get valid meeting IDs from Zoom
3. Work perfectly when students click "Join Class"

## API Scopes Used
The Server-to-Server OAuth app uses these scopes:
- `meeting:write` - Create meetings
- `meeting:read` - Read meeting details
- `meeting:delete` - Delete meetings

These are automatically granted when you create the app.

## Testing
After adding credentials:

```bash
# Regenerate all enrollment zoom links
python regenerate_zoom_links.py

# This will create REAL Zoom meetings for each enrollment
```

## Troubleshooting

**Error: "Zoom credentials not configured"**
- Make sure .env has ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET
- Restart backend after editing .env

**Error: "Invalid credentials"**
- Double-check Client ID and Secret match exactly
- No spaces or extra characters

**Error: "Unauthorized"**
- Check Account ID is correct
- Make sure app status is "Activated" in Zoom Marketplace

## Production Notes
- ✅ Real meetings are created on demand
- ✅ Meetings auto-expire after course ends (optional feature)
- ✅ Can delete meetings when course is cancelled
- ✅ Students always get working Zoom links
- ✅ No fake IDs - everything is real

---

Once setup is complete, the system will work perfectly with real Zoom meetings!
