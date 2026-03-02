#!/usr/bin/env python3
"""Test script for pending approvals endpoint"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal
from models import User, UserRole, Enrollment, Course, Teacher, Student, TimeSlot, Payment
from auth import create_access_token

# Create test data
db = SessionLocal()

# Create a test admin user
test_user = User(
    name="Test Admin",
    email="admin@test.com",
    password="hashedpassword",
    role=UserRole.ADMIN
)

# Check if there are any enrollments
enrollments = db.query(Enrollment).filter(Enrollment.is_active == False).all()
print(f"Found {len(enrollments)} inactive enrollments")

for e in enrollments[:3]:
    print(f"\nEnrollment {e.id}:")
    print(f"  Student: {e.student.name if e.student else 'None'}")
    print(f"  Course: {e.course.name if e.course else 'None'}")
    print(f"  Teacher: {e.teacher.user.name if (e.teacher and e.teacher.user) else 'None'}")
    
db.close()

