#!/usr/bin/env python3
"""Quick database check"""
from database import SessionLocal
from models import User
import json

db = SessionLocal()

try:
    users = db.query(User).all()
    print(f"\nTotal users in database: {len(users)}\n")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"  Name: {user.name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Password Hash (first 30 chars): {user.password_hash[:30] if user.password_hash else 'None'}...")
        print()
        
finally:
    db.close()
