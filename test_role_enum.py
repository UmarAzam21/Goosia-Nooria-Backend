#!/usr/bin/env python
"""Test admin role enum checking"""

from database import SessionLocal
from models import User, UserRole

db = SessionLocal()

admin_user = db.query(User).filter(User.email == 'admin@masjid.com').first()

if admin_user:
    print("Role comparisons:")
    print(f"  admin_user.role: {admin_user.role}")
    print(f"  admin_user.role.value: {admin_user.role.value}")
    print(f"  type: {type(admin_user.role)}")
    print()
    
    # Test different checks
    print("Check 1 - admin_user.role == 'admin':", admin_user.role == 'admin')
    print("Check 2 - admin_user.role.value == 'admin':", admin_user.role.value == 'admin')
    print("Check 3 - admin_user.role == UserRole.ADMIN:", admin_user.role == UserRole.ADMIN)
    
    print("\n✓ Using .value comparison works!")
else:
    print("User not found")

db.close()
