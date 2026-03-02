from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from datetime import datetime

from database import get_db
from models import ChatMessage, User, Class
from schemas import ChatMessageCreate, ChatMessageResponse
from auth import get_current_user

router = APIRouter()

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # Format: {user_id: [websocket connections]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a chat message"""
    # Verify class exists if class_id is provided
    if message.class_id:
        class_obj = db.query(Class).filter(Class.id == message.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
    
    # Create message
    db_message = ChatMessage(
        class_id=message.class_id,
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Create response with sender name
    response_data = {
        **db_message.__dict__,
        "sender_name": current_user.name
    }
    
    # BROADCAST via WebSocket to receiver in real-time
    message_json = {
        "type": "new_message",
        "id": db_message.id,
        "sender_id": db_message.sender_id,
        "sender_name": current_user.name,
        "receiver_id": db_message.receiver_id,
        "message": db_message.message,
        "class_id": db_message.class_id,
        "is_read": db_message.is_read,
        "created_at": db_message.created_at.isoformat() if db_message.created_at else None
    }
    
    # Send to receiver's WebSocket connections without blocking
    try:
        await manager.broadcast_to_user(message.receiver_id, message_json)
    except Exception as e:
        print(f"[WebSocket Broadcast Error] {str(e)}")
        # Continue even if WebSocket broadcast fails - message is still saved in DB
    
    return ChatMessageResponse(**response_data)

@router.get("/class/{class_id}", response_model=List[ChatMessageResponse])
def get_class_messages(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a specific class"""
    # Verify user has access to this class
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.class_id == class_id
    ).order_by(ChatMessage.created_at).all()
    
    # Enrich with sender names
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        msg_dict = {
            **msg.__dict__,
            "sender_name": sender.name if sender else "Unknown"
        }
        result.append(ChatMessageResponse(**msg_dict))
    
    return result

@router.get("/conversation/{user_id}", response_model=List[ChatMessageResponse])
def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation between current user and another user"""
    messages = db.query(ChatMessage).filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == user_id)) |
        ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.created_at).all()
    
    # Enrich with sender names
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        msg_dict = {
            **msg.__dict__,
            "sender_name": sender.name if sender else "Unknown"
        }
        result.append(ChatMessageResponse(**msg_dict))
    
    return result

@router.put("/conversation/{user_id}/read-all")
def mark_conversation_as_read(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all messages from a specific user as read"""
    # Update all unread messages from user_id to current_user
    messages = db.query(ChatMessage).filter(
        ChatMessage.sender_id == user_id,
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False
    ).all()
    
    count = 0
    for msg in messages:
        msg.is_read = True
        count += 1
    
    db.commit()
    
    return {"message": f"Marked {count} messages as read"}

@router.put("/{message_id}/read")
def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read"""
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread messages"""
    count = db.query(ChatMessage).filter(
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False
    ).count()
    
    return {"unread_count": count}

@router.get("/contacts")
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of contacts user can message (admins and teachers)"""
    # Get all admins and teachers
    contacts = db.query(User).filter(
        User.role.in_(["admin", "teacher"]),
        User.id != current_user.id
    ).all()
    
    contact_list = []
    for contact in contacts:
        # Get unread count for this contact
        unread = db.query(ChatMessage).filter(
            ChatMessage.sender_id == contact.id,
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.is_read == False
        ).count()
        
        contact_list.append({
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "role": contact.role,
            "unread_count": unread
        })
    
    return contact_list

@router.get("/received-messages", response_model=List[ChatMessageResponse])
def get_received_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages received by the current user (for admins/teachers)"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.receiver_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).all()
    
    # Enrich with sender names
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        msg_dict = {
            **msg.__dict__,
            "sender_name": sender.name if sender else "Unknown"
        }
        result.append(ChatMessageResponse(**msg_dict))
    
    return result

@router.get("/sent-messages", response_model=List[ChatMessageResponse])
def get_sent_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages sent by the current user"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.sender_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).all()
    
    # Enrich with receiver names
    result = []
    for msg in messages:
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()
        msg_dict = {
            **msg.__dict__,
            "receiver_name": receiver.name if receiver else "Unknown"
        }
        result.append(ChatMessageResponse(**msg_dict))
    
    return result

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = None):
    """WebSocket endpoint for real-time messaging"""
    try:
        # Connect the WebSocket
        await manager.connect(user_id, websocket)
        print(f"[WebSocket] User {user_id} connected")
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Just keep the connection alive
            # Messages are sent via HTTP POST /chat/ and broadcast here
            
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        print(f"[WebSocket] User {user_id} disconnected")
    except Exception as e:
        manager.disconnect(user_id, websocket)
        print(f"[WebSocket] Error with user {user_id}: {str(e)}")
