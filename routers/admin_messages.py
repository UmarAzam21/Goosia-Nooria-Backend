"""
Admin Messages Router - Handle student messages to admin
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import AdminMessage, User
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/messages", tags=["Admin Messages"])

class AdminMessageCreate(BaseModel):
    student_name: str
    message: str
    recipient_type: str = "admin"  # 'admin' or 'teacher'

class AdminSendToStudent(BaseModel):
    student_id: int
    message: str

class AdminMessageResponse(BaseModel):
    id: int
    student_id: int
    sender_id: int | None = None
    student_name: str
    message: str
    response: str | None = None
    is_read: bool
    is_responded: bool
    recipient_type: str
    created_at: datetime
    responded_at: datetime | None = None

    class Config:
        from_attributes = True

# Student sends message to admin
@router.post("/send-to-admin", response_model=dict)
async def send_message_to_admin(
    message_data: AdminMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Student sends a message to admin or teacher
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can send messages")
    
    try:
        # Create the message - IMPORTANT: Explicitly set is_read=False for admin to see badge
        admin_message = AdminMessage(
            student_id=current_user.id,
            sender_id=current_user.id,  # Student is the sender
            student_name=message_data.student_name,
            message=message_data.message,
            is_read=False,  # CRITICAL: Student's message is unread for admin
            is_responded=False,  # Not yet responded by admin
            recipient_type=message_data.recipient_type  # Store recipient type
        )
        
        db.add(admin_message)
        db.flush()
        db.commit()
        db.refresh(admin_message)
        
        recipient_name = "Admin" if message_data.recipient_type == "admin" else "Teacher"
        return {
            "success": True,
            "message": f"Message sent successfully to {recipient_name}! They will respond within one hour.",
            "message_id": admin_message.id,
            "created_at": admin_message.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

# Student gets their sent messages
@router.get("/my-messages", response_model=list[AdminMessageResponse])
async def get_my_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages sent by the current student
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their messages")
    
    messages = db.query(AdminMessage).filter(
        AdminMessage.student_id == current_user.id
    ).order_by(AdminMessage.created_at).all()
    
    return messages

# Student gets their unread message count
@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread messages from admin for the current student
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can check their unread count")
    
    # Count unread messages from admin
    # Messages where: TO this student, FROM admin, and unread
    unread_count = db.query(AdminMessage).filter(
        AdminMessage.student_id == current_user.id,
        AdminMessage.sender_id != current_user.id,  # From admin, not from student
        AdminMessage.is_read == False
    ).count()
    
    return {"unread_count": unread_count}

# Admin gets all unread messages
@router.get("/admin/unread", response_model=list[AdminMessageResponse])
async def get_unread_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Get all unread messages from students
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access this endpoint")
    
    messages = db.query(AdminMessage).filter(
        AdminMessage.is_read == False
    ).order_by(AdminMessage.created_at).all()
    
    return messages

# Admin gets all messages (both read and unread)
@router.get("/admin/all", response_model=list[AdminMessageResponse])
async def get_all_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Get all messages from students
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access this endpoint")
    
    messages = db.query(AdminMessage).order_by(AdminMessage.created_at).all()
    
    return messages

# Admin responds to a message
@router.put("/admin/{message_id}/respond", response_model=dict)
async def respond_to_message(
    message_id: int,
    response_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Respond to a student's message
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can respond to messages")
    
    message = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        message.response = response_data.get("response")
        message.is_responded = True
        message.is_read = True
        message.responded_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Response sent successfully",
            "message_id": message.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error responding to message: {str(e)}")

# Admin sends a direct message to a student
@router.post("/admin/send-to-student", response_model=dict)
async def admin_send_to_student(
    message_data: AdminSendToStudent,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Send a direct message to a student
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can send messages")
    
    student_id = message_data.student_id
    message_text = message_data.message
    
    if not student_id or not message_text:
        raise HTTPException(status_code=400, detail="Missing student_id or message")
    
    try:
        # Get student name
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create admin message - IMPORTANT: Explicitly set is_read=False for badge
        admin_message = AdminMessage(
            student_id=student_id,
            sender_id=current_user.id,  # Admin is the sender
            student_name=student.name if student.name else f"Student {student_id}",
            message=message_text,
            response=None,  # This is not a response, it's a direct message
            is_responded=False,  # Direct message, not a response
            is_read=False,  # CRITICAL: Must be False for badge to show
            recipient_type="student"  # Mark as message to student
        )
        
        print(f"[SEND-MSG] 1. BEFORE add - is_read={admin_message.is_read}")
        
        db.add(admin_message)
        print(f"[SEND-MSG] 2. After add - is_read={admin_message.is_read}")
        
        db.flush()
        print(f"[SEND-MSG] 3. After flush - is_read={admin_message.is_read}, ID={admin_message.id}")
        
        db.commit()
        print(f"[SEND-MSG] 4. After commit - is_read={admin_message.is_read}")
        
        db.refresh(admin_message)
        print(f"[SEND-MSG] 5. After refresh - is_read={admin_message.is_read}")
        
        # VERIFY IN DATABASE
        verify_msg = db.query(AdminMessage).filter(AdminMessage.id == admin_message.id).first()
        print(f"[SEND-MSG] 6. Re-queried from DB - is_read={verify_msg.is_read}")
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "message_id": admin_message.id,
            "created_at": admin_message.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

# Admin marks message as read
@router.put("/admin/{message_id}/mark-read", response_model=dict)
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Mark a message as read
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access this endpoint")
    
    message = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        message.is_read = True
        db.commit()
        
        return {
            "success": True,
            "message": "Message marked as read"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking message as read: {str(e)}")

# Admin marks all messages from a student as read
@router.put("/admin/student/{student_id}/mark-all-read", response_model=dict)
async def mark_student_messages_read(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Mark all messages from a student as read
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access this endpoint")
    
    try:
        # Mark all unread messages from this student as read
        messages = db.query(AdminMessage).filter(
            AdminMessage.student_id == student_id,
            AdminMessage.is_read == False
        ).all()
        
        count = 0
        for message in messages:
            message.is_read = True
            count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Marked {count} message(s) as read"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking messages as read: {str(e)}")

# Student marks all messages from admin as read
@router.put("/mark-all-read-from-admin", response_model=dict)
async def mark_all_admin_messages_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Student endpoint: Mark all unread messages from admin as read
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    try:
        # Mark all unread messages TO this student (from admin) as read
        # Messages where sender_id is NOT the current user (i.e., from admin)
        messages = db.query(AdminMessage).filter(
            AdminMessage.student_id == current_user.id,
            AdminMessage.sender_id != current_user.id,  # Messages from admin, not from student
            AdminMessage.is_read == False
        ).all()
        
        count = 0
        for message in messages:
            message.is_read = True
            count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Marked {count} message(s) as read",
            "count": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking messages as read: {str(e)}")
