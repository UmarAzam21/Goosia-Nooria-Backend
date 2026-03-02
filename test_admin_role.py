#!/usr/bin/env python
"""Test admin response endpoint role checking"""

from database import SessionLocal
from models import User, AdminMessage

db = SessionLocal()

# Get admin user
admin_user = db.query(User).filter(User.email == 'admin@masjid.com').first()

print("=" * 70)
print("TESTING ADMIN RESPONSE ENDPOINT")
print("=" * 70)

if admin_user:
    print(f"\nAdmin User Found: {admin_user.email}")
    print(f"User ID: {admin_user.id}")
    print(f"Role type: {type(admin_user.role)}")
    print(f"Role value: {admin_user.role}")
    print(f"Role as str: {str(admin_user.role)}")
    print(f"Role lower: {str(admin_user.role).lower()}")
    
    # Test the role checks
    role_check_1 = str(admin_user.role) != "admin"
    role_check_2 = str(admin_user.role).lower() != "admin"
    
    print(f"\nRole Checks:")
    print(f"  str(role) != 'admin': {role_check_1}")
    print(f"  str(role).lower() != 'admin': {role_check_2}")
    print(f"  Will API allow response? {not (role_check_1 and role_check_2)}")
    
    # Get a message to test
    msg = db.query(AdminMessage).filter(AdminMessage.is_responded == False).first()
    if msg:
        print(f"\nTest Message:")
        print(f"  ID: {msg.id}")
        print(f"  Student: {msg.student_name}")
        print(f"  Message: {msg.message[:50]}")
        print(f"  Responded: {msg.is_responded}")
        print(f"\n✓ Ready to test response endpoint")
    else:
        print("\n⚠ No unresponded messages in database")
else:
    print("✗ Admin user not found")

db.close()
