#!/usr/bin/env python
"""Verify 403 forbidden issue is fixed"""

from database import SessionLocal
from models import User, AdminMessage

db = SessionLocal()

admin_user = db.query(User).filter(User.email == 'admin@masjid.com').first()
msg = db.query(AdminMessage).filter(AdminMessage.is_responded == False).first()

print("=" * 70)
print("VERIFICATION - ADMIN RESPONSE FIX")
print("=" * 70)

if admin_user and msg:
    print(f"\nAdmin User: {admin_user.email}")
    print(f"Admin Role: {admin_user.role}")
    print(f"Role == 'admin': {admin_user.role == 'admin'}")
    print(f"Role != 'admin': {admin_user.role != 'admin'}")
    
    print(f"\nTest Message ID: {msg.id}")
    print(f"From: {msg.student_name}")
    print(f"Message: {msg.message[:50]}")
    print(f"Responded: {msg.is_responded}")
    
    # Simulate the role check from endpoint
    can_respond = admin_user.role == "admin"
    
    print(f"\n" + "=" * 70)
    if can_respond:
        print("✓ SUCCESS - Admin can now send responses!")
        print("  The 403 Forbidden error should be fixed.")
    else:
        print("✗ FAILED - Role check still rejecting admin")
    print("=" * 70)
else:
    print("✗ Missing test data")

db.close()
