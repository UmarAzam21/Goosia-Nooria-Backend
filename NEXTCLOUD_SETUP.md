# Nextcloud Integration Setup Guide

## Overview
This backend now uses **Nextcloud Talk** for video conferencing and room management instead of BigBlueButton.

## Prerequisites
1. A Nextcloud instance (self-hosted or cloud-based)
2. Nextcloud Talk app enabled
3. Admin access to create app passwords

## Configuration Steps

### 1. Get Your Nextcloud Server URL
- If self-hosted: `https://your-domain.com` (without `/nextcloud` path)
- If cloud-hosted: `https://your-instance.nextcloud.com`

Example: `https://meeting.example.com`

### 2. Create an App Password
1. Log in to your Nextcloud admin account
2. Go to **Settings** → **Security**
3. Scroll to **App Passwords** section
4. Click **Create new app password**
5. Give it a name like "Noori API"
6. Copy the generated password

### 3. Update `.env` File
Set these values in `.env`:

```dotenv
NEXTCLOUD_URL=https://your-nextcloud-server.com
NEXTCLOUD_USERNAME=admin
NEXTCLOUD_APP_PASSWORD=your-app-specific-password
```

Example:
```dotenv
NEXTCLOUD_URL=https://meeting.example.com
NEXTCLOUD_USERNAME=admin
NEXTCLOUD_APP_PASSWORD=abcd1234efgh5678ijkl9012mnop3456
```

### 4. Test the Connection
Run this command to verify connection:
```bash
curl http://localhost:5000/api/health/nextcloud
```

Expected response:
```json
{
  "success": true,
  "message": "Connected to Nextcloud successfully",
  "server_url": "https://your-nextcloud-server.com"
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
  "join_url": "https://meeting.example.com/call/room_token",
  "room_token": "abc123xyz",
  "server_url": "https://meeting.example.com",
  "class_name": "Class Name",
  "is_moderator": true
}
```

### Create a Meeting Room
```
POST /api/meetings/create
```

Body:
```json
{
  "class_id": 1,
  "meeting_name": "Class Name",
  "participant_type": "public"
}
```

### Join a Meeting
```
POST /api/meetings/join
```

Body:
```json
{
  "room_token": "abc123xyz"
}
```

### Delete a Room
```
POST /api/meetings/{room_token}/delete
```

## How It Works

1. **Room Creation**: When students enroll in a course, a Nextcloud Talk room is automatically created
2. **Room Token Storage**: The room token is stored in the database and linked to each class
3. **Join URL Generation**: Participants receive direct links to join via `GET /api/classes/{class_id}/bbb-join-url`
4. **No Passwords**: Nextcloud Talk handles authentication automatically - no moderator/attendee passwords needed

## Features

✅ Screen sharing  
✅ Recording support  
✅ Chat functionality  
✅ File sharing  
✅ Participant management  
✅ End-to-end encryption compatible  

## SSL/TLS Certificate Issues

If you get SSL certificate errors:

### Option 1: Use Self-Signed Certificates (Development Only)
The service automatically disables SSL verification for self-signed certificates.

### Option 2: Fix Certificate Issues (Production)
1. Ensure your Nextcloud has a valid SSL certificate
2. Update the .env URL to match your certificate domain
3. Test with: `curl -I https://your-nextcloud-server.com`

## Troubleshooting

### "Failed to resolve domain"
- Check NEXTCLOUD_URL spelling
- Remove trailing slashes from URL
- Verify the server is reachable from your network

### "401 Unauthorized"
- Verify NEXTCLOUD_USERNAME is correct
- Verify NEXTCLOUD_APP_PASSWORD is correct (not the user password)
- Regenerate the app password

### "Connection timeout"
- Check if Nextcloud server is running
- Verify firewall allows outbound HTTPS connections
- Test manually: `curl -u admin:password https://your-server/ocs/v2.php/apps/spreed/api/v4/rooms`

## Migration from BigBlueButton

If migrating from BBB:
1. Update .env with Nextcloud credentials
2. New enrollments will automatically use Nextcloud Talk
3. Existing BBB links in database can be kept or migrated separately if needed

## Support

For Nextcloud Talk documentation: https://docs.nextcloud.com/server/latest/user_manual/en/talk/
For API documentation: https://docs.nextcloud.com/server/latest/developer_manual/client_apis/Guest/talk.html
