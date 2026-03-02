#!/usr/bin/env python
"""Clean up old test messages and add fresh unread ones"""
from database import SessionLocal
from models import AdminMessage
from datetime import datetime

db = SessionLocal()

try:
    # Delete all old admin messages
    count_deleted = db.query(AdminMessage).delete()
    db.commit()
    print(f"✓ Deleted {count_deleted} old admin messages")
    
    # Create fresh test messages with is_read=False (unread)
    test_messages = [
        AdminMessage(
            student_id=5,
            sender_id=1,
            student_name="Ali Ahmed",
            message="Welcome to our online Quran classes! Here's your first lesson.",
            is_read=False,
            is_responded=False,
            recipient_type="student"
        ),
        AdminMessage(
            student_id=5,
            sender_id=1,
            student_name="Ali Ahmed",
            message="Don't forget: Classes are on Monday, Wednesday, and Friday at 7 PM EST.",
            is_read=False,
            is_responded=False,
            recipient_type="student"
        ),
        AdminMessage(
            student_id=5,
            sender_id=1,
            student_name="Ali Ahmed",
            message="Please complete the homework I sent in the materials section.",
            is_read=False,
            is_responded=False,
            recipient_type="student"
        ),
    ]
    
    for msg in test_messages:
        db.add(msg)
    db.commit()
    
    print(f"✓ Added {len(test_messages)} fresh unread test messages")
    
    # Verify
    unread_count = db.query(AdminMessage).filter(AdminMessage.is_read == False).count()
    print(f"\n✅ Database now has {unread_count} unread messages for student 5")
    
    # Show them
    msgs = db.query(AdminMessage).filter(AdminMessage.student_id == 5).all()
    for m in msgs:
        print(f"  - ID {m.id}: is_read={m.is_read}, message={m.message[:50]}...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
