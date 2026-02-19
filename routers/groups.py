from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import CourseGroup, GroupMessage, User, Enrollment
from schemas import CourseGroupResponse, GroupMessageResponse, GroupMessageCreate
from auth import get_current_user

router = APIRouter()

@router.get("/groups/{enrollment_id}", response_model=CourseGroupResponse)
def get_course_group(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course group for an enrollment"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check access
    if (current_user.id != enrollment.student_id and 
        current_user.id != enrollment.teacher.user_id and
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this group"
        )
    
    group = db.query(CourseGroup).filter(CourseGroup.enrollment_id == enrollment_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group

@router.post("/groups/{group_id}/messages", response_model=GroupMessageResponse, status_code=status.HTTP_201_CREATED)
def send_group_message(
    group_id: int,
    message_data: GroupMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to course group"""
    group = db.query(CourseGroup).filter(CourseGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check access
    enrollment = group.enrollment
    if (current_user.id != enrollment.student_id and 
        current_user.id != enrollment.teacher.user_id and
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this group"
        )
    
    message = GroupMessage(
        group_id=group_id,
        sender_id=current_user.id,
        message=message_data.message,
        attachment_url=message_data.attachment_url
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    print(f"[INFO] Message sent to group {group_id} by {current_user.email}")
    
    return message

@router.get("/groups/{group_id}/messages", response_model=List[GroupMessageResponse])
def get_group_messages(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a course group"""
    group = db.query(CourseGroup).filter(CourseGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check access
    enrollment = group.enrollment
    if (current_user.id != enrollment.student_id and 
        current_user.id != enrollment.teacher.user_id and
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this group"
        )
    
    messages = db.query(GroupMessage).filter(
        GroupMessage.group_id == group_id
    ).order_by(GroupMessage.created_at).all()
    
    return messages

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message (only sender or admin can delete)"""
    message = db.query(GroupMessage).filter(GroupMessage.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if current_user.id != message.sender_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )
    
    db.delete(message)
    db.commit()
    print(f"[INFO] Message deleted by {current_user.email}")
    
    return None

