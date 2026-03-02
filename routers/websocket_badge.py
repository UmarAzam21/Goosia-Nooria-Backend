"""
WebSocket Badge Events Handler
Handles real-time badge count updates and chat tab open/close events
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
from badge_manager import badge_manager
from auth import get_current_user_from_token

router = APIRouter()

# Track active WebSocket connections per user
# user_id → Set[WebSocket]
active_user_connections: Dict[int, Set[WebSocket]] = {}


async def send_badge_count(user_id: int, count: int):
    """
    Send badge count update to all connected clients for this user.
    
    Message format:
    {
        "event": "BADGE_COUNT",
        "user_id": 5,
        "count": 3
    }
    """
    if user_id not in active_user_connections:
        return
    
    message = {
        "event": "BADGE_COUNT",
        "user_id": user_id,
        "count": count
    }
    
    # Send to all connected clients for this user
    disconnected = set()
    for websocket in active_user_connections[user_id]:
        try:
            await websocket.send_json(message)
            print(f"✉️  Sent BADGE_COUNT to user {user_id}: count={count}")
        except Exception as e:
            print(f"❌ Failed to send to user {user_id}: {str(e)}")
            disconnected.add(websocket)
    
    # Clean up dead connections
    for ws in disconnected:
        active_user_connections[user_id].discard(ws)
    
    if not active_user_connections[user_id]:
        del active_user_connections[user_id]


@router.websocket("/ws/badge/{token}")
async def websocket_badge_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time badge count updates.
    
    Connection:
    - URL: /ws/badge/{auth_token}
    
    Client → Server Events:
    
    1. CHAT_OPEN: User opened the chat/messaging tab
       {
           "event": "CHAT_OPEN"
       }
       → Response: {"event": "BADGE_COUNT", "count": 0}
    
    2. CHAT_CLOSE: User closed the chat/messaging tab
       {
           "event": "CHAT_CLOSE"
       }
       → Response: {"event": "CHAT_CLOSED"}
    
    3. MESSAGE_RECEIVED: Backend notifies unread count changed
       (This is sent FROM server TO client automatically)
       {
           "event": "BADGE_COUNT",
           "count": 3
       }
    
    Server → Client Events:
    
    1. BADGE_COUNT: Sent whenever unread count changes
       {
           "event": "BADGE_COUNT",
           "user_id": 5,
           "count": 3
       }
    """
    
    # Authenticate user from token
    try:
        from auth import decode_token
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception as e:
        print(f"❌ WebSocket auth failed: {str(e)}")
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Accept connection
    await websocket.accept()
    
    # Register this connection
    if user_id not in active_user_connections:
        active_user_connections[user_id] = set()
    active_user_connections[user_id].add(websocket)
    
    print(f"\n🔌 BADGE WebSocket Connected:")
    print(f"   User ID: {user_id}")
    print(f"   Active connections for this user: {len(active_user_connections[user_id])}")
    
    # Send initial badge count
    initial_count = badge_manager.get_unread_count(user_id)
    await websocket.send_json({
        "event": "BADGE_COUNT",
        "count": initial_count
    })
    print(f"   Initial unread count: {initial_count}\n")
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            event_type = message.get("event")
            print(f"\n📨 BADGE EVENT from user {user_id}: {event_type}")
            
            # Handle CHAT_OPEN event
            if event_type == "CHAT_OPEN":
                print(f"   → Chat tab OPENED")
                result = badge_manager.open_chat(user_id)
                await websocket.send_json(result)
                print(f"   → Sent BADGE_COUNT=0")
            
            # Handle CHAT_CLOSE event
            elif event_type == "CHAT_CLOSE":
                print(f"   → Chat tab CLOSED")
                result = badge_manager.close_chat(user_id)
                await websocket.send_json(result)
                print(f"   → Sent confirmation")
            
            else:
                print(f"   ⚠️  Unknown event type: {event_type}")
    
    except WebSocketDisconnect:
        print(f"\n🔌 User {user_id} disconnected from badge WebSocket")
        if user_id in active_user_connections:
            active_user_connections[user_id].discard(websocket)
            if not active_user_connections[user_id]:
                del active_user_connections[user_id]
    
    except Exception as e:
        print(f"❌ WebSocket error for user {user_id}: {str(e)}")
        if user_id in active_user_connections:
            active_user_connections[user_id].discard(websocket)


async def notify_message_received(recipient_id: int):
    """
    Called when a message is received for a user.
    Updates unread count and sends badge count to all their clients.
    """
    # Update badge manager
    badge_event = badge_manager.receive_message(recipient_id)
    
    # If event returned (chat is closed, count increased)
    if badge_event:
        await send_badge_count(recipient_id, badge_event["count"])
        print(f"🔔 Badge updated for user {recipient_id}: count={badge_event['count']}\n")
    else:
        print(f"ℹ️  User {recipient_id} has chat open, not incrementing badge\n")
