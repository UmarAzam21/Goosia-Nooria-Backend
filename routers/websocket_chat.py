"""
WebSocket Router for Real-time Chat
Handles student-admin and student-student communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from models import ChatMessage, User

router = APIRouter()

# Store active WebSocket connections
# Key format: f"{student_id}:{admin_id}" or f"{user1_id}:{user2_id}"
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, connection_key: str, websocket: WebSocket):
        await websocket.accept()
        if connection_key not in self.active_connections:
            self.active_connections[connection_key] = []
        self.active_connections[connection_key].append(websocket)

    def disconnect(self, connection_key: str, websocket: WebSocket):
        if connection_key in self.active_connections:
            self.active_connections[connection_key].remove(websocket)
            if len(self.active_connections[connection_key]) == 0:
                del self.active_connections[connection_key]

    async def broadcast(self, connection_key: str, message: dict):
        """Send message to all connected users in this chat"""
        if connection_key in self.active_connections:
            for connection in self.active_connections[connection_key]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")

    def get_connection_count(self, connection_key: str) -> int:
        """Get number of active connections"""
        return len(self.active_connections.get(connection_key, []))


manager = ConnectionManager()


@router.websocket("/ws/chat/{student_id}/{admin_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    student_id: int,
    admin_id: int
):
    """
    WebSocket endpoint for real-time chat between student and admin
    
    URL: /ws/chat/{student_id}/{admin_id}
    
    Message format (client -> server):
    {
        "type": "message",
        "text": "Hello admin",
        "sender_id": 5,
        "sender_role": "student"
    }
    
    Response format (server -> client):
    {
        "type": "message",
        "id": 123,
        "sender_id": 5,
        "sender_name": "Ali Ahmed",
        "sender_role": "student",
        "text": "Hello admin",
        "created_at": "2026-02-25T12:47:07",
        "is_current_user": true
    }
    """
    
    # Create a unique key for this chat
    connection_key = f"{min(student_id, admin_id)}:{max(student_id, admin_id)}"
    
    # Get database session manually
    from database import SessionLocal
    db = SessionLocal()
    
    # Connect the WebSocket
    await manager.connect(connection_key, websocket)
    
    try:
        # Send chat history when user connects
        chat_messages = db.query(ChatMessage).filter(
            ((ChatMessage.sender_id == student_id) & (ChatMessage.receiver_id == admin_id)) |
            ((ChatMessage.sender_id == admin_id) & (ChatMessage.receiver_id == student_id))
        ).order_by(ChatMessage.created_at).all()
        
        print(f"\n🔗 NEW CONNECTION:")
        print(f"   Student: {student_id}, Admin: {admin_id}")
        print(f"   Connection Key: {connection_key}")
        print(f"   Sending {len(chat_messages)} messages from history\n")
        
        # Send history
        history_message = {
            "type": "history",
            "messages": [
                {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "sender_name": db.query(User).filter(User.id == msg.sender_id).first().name,
                    "sender_role": "admin" if msg.sender_id == admin_id else "student",
                    "text": msg.message,
                    "created_at": msg.created_at.isoformat(),
                    "is_read": msg.is_read,
                }
                for msg in chat_messages
            ]
        }
        
        print(f"📚 HISTORY MESSAGE:")
        print(f"   {json.dumps(history_message, indent=2)}\n")
        
        await websocket.send_json(history_message)
        
        # Send status message
        status_msg = {
            "type": "status",
            "text": f"Connected to chat. {manager.get_connection_count(connection_key)} user(s) online"
        }
        print(f"📊 STATUS: {manager.get_connection_count(connection_key)} users online in {connection_key}\n")
        await manager.broadcast(connection_key, status_msg)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            print(f"\n📨 MESSAGE RECEIVED FROM CLIENT: {msg_data}")
            
            if msg_data.get("type") == "message":
                sender_id = msg_data.get("sender_id")
                message_text = msg_data.get("text", "").strip()
                
                if not message_text:
                    print(f"⚠️ EMPTY MESSAGE SKIPPED")
                    continue
                
                # Determine receiver
                receiver_id = admin_id if sender_id == student_id else student_id
                sender_role = "student" if sender_id == student_id else "admin"
                
                print(f"📝 PROCESSING MESSAGE:")
                print(f"   Sender: {sender_id} ({sender_role})")
                print(f"   Receiver: {receiver_id}")
                print(f"   Text: {message_text}")
                
                # Save message to database
                db_message = ChatMessage(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    message=message_text,
                    is_read=False
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
                
                print(f"✅ MESSAGE SAVED TO DB - ID: {db_message.id}")
                
                # Get sender name
                sender = db.query(User).filter(User.id == sender_id).first()
                
                # Broadcast to all connected users
                broadcast_msg = {
                    "type": "message",
                    "id": db_message.id,
                    "sender_id": sender_id,
                    "sender_name": sender.name if sender else "Unknown",
                    "sender_role": sender_role,
                    "text": message_text,
                    "created_at": db_message.created_at.isoformat(),
                    "is_read": db_message.is_read
                }
                
                print(f"📤 BROADCASTING MESSAGE:")
                print(f"   {json.dumps(broadcast_msg, indent=2)}")
                print(f"   To {manager.get_connection_count(connection_key)} connected users\n")
                
                await manager.broadcast(connection_key, broadcast_msg)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_key, websocket)
        db.close()
        
        # Notify remaining users
        disconnect_msg = {
            "type": "status",
            "text": f"User disconnected. {manager.get_connection_count(connection_key)} user(s) online"
        }
        await manager.broadcast(connection_key, disconnect_msg)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_key, websocket)
        db.close()
