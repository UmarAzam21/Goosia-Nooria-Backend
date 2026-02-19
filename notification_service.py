"""
Notification service for managing notifications and scheduling
"""

from datetime import datetime, time, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from models import Notification, NotificationPreference, User
from enum import Enum

class NotificationType(str, Enum):
    CLASS_REMINDER = "class_reminder"
    PAYMENT_REMINDER = "payment_reminder"
    PAYMENT_APPROVED = "payment_approved"
    ENROLLMENT_APPROVED = "enrollment_approved"
    NEW_STUDENT = "new_student"
    IMPORTANT = "important"

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.IMPORTANT,
    is_important: bool = False,
    scheduled_time: Optional[datetime] = None,
) -> Notification:
    """
    Create a new notification
    
    Args:
        db: Database session
        user_id: User ID to notify
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        is_important: Whether this is an important notification
        scheduled_time: When to send the notification (None = immediately)
        
    Returns:
        Created notification object
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type.value,
        is_important=is_important,
        scheduled_time=scheduled_time,
        is_sent=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification

def create_scheduled_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    scheduled_time: datetime,
    notification_type: NotificationType = NotificationType.IMPORTANT,
    is_important: bool = True,
) -> Notification:
    """
    Create a notification to be sent at a specific time
    
    Args:
        db: Database session
        user_id: User ID
        title: Notification title
        message: Notification message
        scheduled_time: When to send the notification
        notification_type: Type of notification
        is_important: Whether this is important
        
    Returns:
        Created notification object
    """
    return create_notification(
        db=db,
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_important=is_important,
        scheduled_time=scheduled_time
    )

def get_user_notification_preferences(db: Session, user_id: int) -> NotificationPreference:
    """
    Get notification preferences for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        NotificationPreference object
    """
    return db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()

def update_notification_preferences(
    db: Session,
    user_id: int,
    **kwargs
) -> NotificationPreference:
    """
    Update user's notification preferences
    
    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update
        
    Returns:
        Updated NotificationPreference object
    """
    prefs = get_user_notification_preferences(db, user_id)
    
    if not prefs:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
    
    for key, value in kwargs.items():
        if hasattr(prefs, key):
            setattr(prefs, key, value)
    
    db.commit()
    db.refresh(prefs)
    
    return prefs

def create_class_reminder(
    db: Session,
    student_id: int,
    teacher_name: str,
    course_name: str,
    class_date: str,
    class_time: str,
    minutes_before: int = 30
) -> Optional[Notification]:
    """
    Create a class reminder notification
    
    Args:
        db: Database session
        student_id: Student ID
        teacher_name: Teacher's name
        course_name: Course name
        class_date: Class date (YYYY-MM-DD)
        class_time: Class time (HH:MM)
        minutes_before: Minutes before class to send reminder
        
    Returns:
        Created notification or None
    """
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        return None
    
    prefs = get_user_notification_preferences(db, student_id)
    if prefs and not prefs.enable_class_reminders:
        return None
    
    title = f"Class Reminder: {course_name}"
    message = f"Your class with {teacher_name} will start at {class_time}. Please be ready!"
    
    # Parse class datetime and subtract minutes_before
    try:
        class_datetime = datetime.strptime(f"{class_date} {class_time}", "%Y-%m-%d %H:%M")
        scheduled_time = class_datetime - timedelta(minutes=minutes_before)
    except ValueError:
        scheduled_time = None
    
    # Check if user prefers voice notifications for important events
    should_voice = prefs.enable_voice_notifications if prefs else False
    
    return create_notification(
        db=db,
        user_id=student_id,
        title=title,
        message=message,
        notification_type=NotificationType.CLASS_REMINDER,
        is_important=True,
        scheduled_time=scheduled_time
    )

def create_payment_reminder(
    db: Session,
    student_id: int,
    course_name: str,
    amount: str,
    due_date: str
) -> Optional[Notification]:
    """
    Create a payment reminder notification
    
    Args:
        db: Database session
        student_id: Student ID
        course_name: Course name
        amount: Payment amount
        due_date: Due date (YYYY-MM-DD)
        
    Returns:
        Created notification or None
    """
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        return None
    
    prefs = get_user_notification_preferences(db, student_id)
    if prefs and not prefs.enable_payment_reminders:
        return None
    
    title = f"Payment Reminder: {course_name}"
    message = f"Payment of {amount} for {course_name} is due by {due_date}"
    
    try:
        due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
        # Send reminder 2 days before
        scheduled_time = due_datetime - timedelta(days=2)
    except ValueError:
        scheduled_time = None
    
    return create_notification(
        db=db,
        user_id=student_id,
        title=title,
        message=message,
        notification_type=NotificationType.PAYMENT_REMINDER,
        is_important=True,
        scheduled_time=scheduled_time
    )

def get_pending_notifications(db: Session, user_id: int) -> List[Notification]:
    """
    Get all pending notifications for a user (not yet sent and not read)
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of pending notifications
    """
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(db: Session, notification_id: int) -> Notification:
    """
    Mark a notification as read
    
    Args:
        db: Database session
        notification_id: Notification ID
        
    Returns:
        Updated notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    
    return notification

def send_scheduled_notifications(db: Session):
    """
    Send all notifications that are scheduled for now or earlier
    This should be called by a scheduler periodically
    
    Args:
        db: Database session
    """
    now = datetime.utcnow()
    
    pending = db.query(Notification).filter(
        Notification.is_sent == False,
        Notification.scheduled_time <= now,
        Notification.scheduled_time.isnot(None)
    ).all()
    
    for notification in pending:
        # Here you would integrate with:
        # - Email service for email notifications
        # - SMS service for SMS notifications
        # - Text-to-speech for voice notifications
        
        notification.is_sent = True
        
        if notification.should_notify_voice:
            # Call voice notification service
            send_voice_notification(notification)
        
        db.add(notification)
    
    db.commit()

def send_voice_notification(notification: Notification):
    """
    Send a voice notification (placeholder for actual implementation)
    This would integrate with a service like Twilio, Vonage, etc.
    
    Args:
        notification: Notification to send as voice
    """
    # Placeholder for actual voice notification implementation
    # In production, integrate with a service like:
    # - Twilio for voice calls
    # - Google Cloud Text-to-Speech
    # - AWS Polly
    pass
