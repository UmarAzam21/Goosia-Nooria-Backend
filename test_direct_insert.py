#!/usr/bin/env python
"""Test to identify exactly where is_read becomes True"""
from database import SessionLocal
from models import AdminMessage
import sys

db = SessionLocal()

try:
    # Create a new message with explicit is_read=False
    test_msg = AdminMessage(
        student_id=5,
        sender_id=1,
        student_name="Test Student",
        message="Direct test - should be False",
        is_read=False,  # EXPLICITLY FALSE
        is_responded=False,
        recipient_type="student"
    )
    
    print(f"BEFORE adding to session: is_read={test_msg.is_read}", file=sys.stderr, flush=True)
    
    db.add(test_msg)
    print(f"AFTER db.add: is_read={test_msg.is_read}", file=sys.stderr, flush=True)
    
    db.flush()
    print(f"AFTER db.flush: is_read={test_msg.is_read}", file=sys.stderr, flush=True)
    print(f"  Message ID after flush: {test_msg.id}", file=sys.stderr, flush=True)
    
    db.commit()
    print(f"AFTER db.commit: is_read={test_msg.is_read}", file=sys.stderr, flush=True)
    
    db.refresh(test_msg)
    print(f"AFTER db.refresh: is_read={test_msg.is_read}", file=sys.stderr, flush=True)
    
    # Now query the database directly
    message_id = test_msg.id
    queried = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    print(f"AFTER db.query: is_read={queried.is_read}", file=sys.stderr, flush=True)
    
    print(f"\nRESULT: Message {message_id} is_read value is {queried.is_read}", file=sys.stderr, flush=True)
    
except Exception as e:
    print(f"ERROR: {str(e)}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    db.rollback()
finally:
    db.close()
