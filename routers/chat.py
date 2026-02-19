from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import ChatMessage, User, Class
from schemas import ChatMessageCreate, ChatMessageResponse
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
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
