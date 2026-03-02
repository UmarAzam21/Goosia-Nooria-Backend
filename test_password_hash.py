#!/usr/bin/env python3
"""Test password hashing and verification"""
from database import SessionLocal
from models import User
from auth import get_password_hash, verify_password

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == "ali@student.com").first()
    
    if not user:
        print("User not found!")
    else:
        print(f"User: {user.email}")
        print(f"Current password_hash: {user.password_hash}")
        print()
        
        # Test verification with "student123"
        test_password = "student123"
        is_correct = verify_password(test_password, user.password_hash)
        print(f"Test verify_password('{test_password}', stored_hash): {is_correct}")
        
        if not is_correct:
            print("\n⚠️  Password verification FAILED!")
            print("Fixing by rehashing the password...")
            
            # Re-hash and update
            new_hash = get_password_hash(test_password)
            user.password_hash = new_hash
            db.commit()
            
            # Verify it works now
            is_correct_now = verify_password(test_password, user.password_hash)
            print(f"After rehash - verify_password('{test_password}', new_hash): {is_correct_now}")
            
            if is_correct_now:
                print("✅ Password fixed!")
            else:
                print("❌ Still failing!")
        else:
            print("✅ Password verification works!")
            
finally:
    db.close()
