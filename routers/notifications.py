"""
Notifications router for managing user notifications and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import Notification, NotificationPreference, User
from schemas import NotificationPreferenceResponse, NotificationResponse, NotificationPreferenceBase
from auth import get_current_user
from notification_service import (
    create_notification,
    get_user_notification_preferences,
    update_notification_preferences,
    create_class_reminder,
    create_payment_reminder,
    get_pending_notifications,
    mark_notification_as_read,
    NotificationType
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Get user's notification preferences
@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's notification preferences"""
    prefs = get_user_notification_preferences(db, current_user.id)
    
    if not prefs:
        # Create default preferences if they don't exist
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs

# Update notification preferences
@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    preferences: NotificationPreferenceBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    updated = update_notification_preferences(
        db=db,
        user_id=current_user.id,
        enable_email_notifications=preferences.enable_email_notifications,
        enable_sms_notifications=preferences.enable_sms_notifications,
        enable_voice_notifications=preferences.enable_voice_notifications,
        enable_class_reminders=preferences.enable_class_reminders,
        enable_payment_reminders=preferences.enable_payment_reminders,
        enable_new_enrollment_notifications=preferences.enable_new_enrollment_notifications,
        notification_time=preferences.notification_time,
    )
    return updated

# Get all pending notifications for user
@router.get("/pending", response_model=list[NotificationResponse])
async def get_pending(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending unread notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).limit(limit).all()
    
    return notifications

# Get all notifications for user (with pagination)
@router.get("/", response_model=list[NotificationResponse])
async def get_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for current user with pagination"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications

# Mark notification as read
@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return notification

# Mark all notifications as read
@router.patch("/read-all", response_model=dict)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "Marked all notifications as read", "count": count}

# Delete a notification
@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}

# Get unread notification count
@router.get("/count/unread", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}
