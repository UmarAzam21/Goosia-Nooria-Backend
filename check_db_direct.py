#!/usr/bin/env python3
"""Direct database check"""
import sys
sys.path.insert(0, '/c/Users/lenovo/Desktop/noori/backend')

from database import SessionLocal
from models import AdminMessage
import os

db = SessionLocal()

try:
    # Get last 5 messages
    messages = db.query(AdminMessage).order_by(AdminMessage.id.desc()).limit(5).all()
    
    print("\n" + "="*70)
    print("LAST 5 MESSAGES IN DATABASE")
    print("="*70 + "\n")
    
    for msg in reversed(messages):
        print(f"ID: {msg.id}")
        print(f"  student_id: {msg.student_id}")
        print(f"  sender_id: {msg.sender_id}")
        print(f"  is_read: {msg.is_read}")
        print(f"  message: {msg.message[:50]}")
        print(f"  created_at: {msg.created_at}")
        print()
    
    # Check unread for student 5
    print("="*70)
    print("UNREAD MESSAGES FOR STUDENT 5 (where sender_id=1)")
    print("="*70 + "\n")
    
    unread_admin = db.query(AdminMessage).filter(
        AdminMessage.student_id == 5,
        AdminMessage.sender_id == 1,
        AdminMessage.is_read == False
    ).all()
    
    print(f"Count: {len(unread_admin)}")
    for msg in unread_admin[-5:]:
        print(f"ID: {msg.id} | is_read: {msg.is_read} | {msg.message[:50]}")
    
    print("\n" + "="*70 + "\n")

finally:
    db.close()
