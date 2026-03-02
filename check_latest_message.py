#!/usr/bin/env python3
"""Check what's stored in database after message send"""
from database import SessionLocal
from models import AdminMessage
import json

db = SessionLocal()

try:
    # Get the latest message
    latest = db.query(AdminMessage).order_by(AdminMessage.id.desc()).first()
    
    if latest:
        print(f"Latest message in database:")
        print(f"  ID: {latest.id}")
        print(f"  student_id: {latest.student_id}")
        print(f"  sender_id: {latest.sender_id}")
        print(f"  message: {latest.message[:40] if latest.message else 'None'}...")
        print(f"  is_read: {latest.is_read} (type: {type(latest.is_read).__name__})")
        print(f"  is_responded: {latest.is_responded}")
        print(f"  recipient_type: {latest.recipient_type}")
    else:
        print("No messages in database")
        
finally:
    db.close()
