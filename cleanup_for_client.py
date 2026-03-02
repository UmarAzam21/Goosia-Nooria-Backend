#!/usr/bin/env python3
"""
Clean up database for client demo
Keep only: 1 admin, 3 teachers, 1 student
Remove all test data and enrollments
"""

from database import SessionLocal
from models import User, Enrollment, Class, Course, CourseGroup, Certificate, ChatMessage, GroupMessage, Payment, Coupon, Notification, StudentProfile, Teacher, TimeSlot
from sqlalchemy import delete

db = SessionLocal()

print("=" * 80)
print("CLEANING DATABASE FOR CLIENT DEMO")
print("=" * 80)

# Users to KEEP
KEEP_USERS = {
    1: "admin@masjid.com (Admin)",
    2: "ahmed@masjid.com (Teacher 1)",
    3: "fatima@masjid.com (Teacher 2)",
    4: "ibrahim@masjid.com (Teacher 3)",
    5: "ali@student.com (Student 1)"
}

# Users to DELETE
all_users = db.query(User).all()
users_to_delete = [u for u in all_users if u.id not in KEEP_USERS.keys()]

print(f"\n📋 USERS TO KEEP ({len(KEEP_USERS)}):")
for uid, name in KEEP_USERS.items():
    print(f"   ✅ {name}")

print(f"\n🗑️  USERS TO DELETE ({len(users_to_delete)}):")
for u in users_to_delete:
    print(f"   ❌ ID {u.id}: {u.email} ({u.role})")

# Delete in correct order to avoid foreign key violations
# 1. Delete classes (they reference enrollments)
print("\n🔄 Deleting class sessions...")
deleted_classes = db.query(Class).delete(synchronize_session=False)
print(f"   Deleted {deleted_classes} class sessions")

# 2. Delete payments (they reference enrollments)
print("\n🔄 Deleting payments...")
deleted_payments = db.query(Payment).delete(synchronize_session=False)
print(f"   Deleted {deleted_payments} payments")

# 3. Delete enrollments (for deleted students)
print("\n🔄 Deleting enrollments for removed users...")
deleted_enrollments = db.query(Enrollment).filter(
    Enrollment.student_id.in_([u.id for u in users_to_delete])
).delete(synchronize_session=False)
print(f"   Deleted {deleted_enrollments} enrollments")

# 4. Delete courses
print("\n🔄 Deleting courses...")
deleted_courses = db.query(Course).delete(synchronize_session=False)
print(f"   Deleted {deleted_courses} courses")

# Delete groups and memberships
print("\n🔄 Deleting course groups...")
deleted_messages = db.query(GroupMessage).delete(synchronize_session=False)
print(f"   Deleted {deleted_messages} group messages")
deleted_groups = db.query(CourseGroup).delete(synchronize_session=False)
print(f"   Deleted {deleted_groups} course groups")

# Delete chat messages
print("\n🔄 Deleting chat messages...")
deleted_chat = db.query(ChatMessage).delete(synchronize_session=False)
print(f"   Deleted {deleted_chat} chat messages")

# Delete certificates
print("\n🔄 Deleting certificates...")
deleted_certs = db.query(Certificate).delete(synchronize_session=False)
print(f"   Deleted {deleted_certs} certificates")

# Delete student profiles
print("\n🔄 Deleting student profiles...")
deleted_profiles = db.query(StudentProfile).delete(synchronize_session=False)
print(f"   Deleted {deleted_profiles} student profiles")

# Delete teachers
print("\n🔄 Deleting teacher records...")
deleted_teachers = db.query(Teacher).delete(synchronize_session=False)
print(f"   Deleted {deleted_teachers} teacher records")

# Delete time slots
print("\n🔄 Deleting time slots...")
deleted_slots = db.query(TimeSlot).delete(synchronize_session=False)
print(f"   Deleted {deleted_slots} time slots")

# Delete notifications
print("\n🔄 Deleting notifications...")
deleted_notifications = db.query(Notification).delete(synchronize_session=False)
print(f"   Deleted {deleted_notifications} notifications")

# Delete coupons
print("\n🔄 Deleting coupons...")
deleted_coupons = db.query(Coupon).delete(synchronize_session=False)
print(f"   Deleted {deleted_coupons} coupons")

# Delete test users
print("\n🔄 Deleting test users...")
for user in users_to_delete:
    db.delete(user)
db.commit()
print(f"   Deleted {len(users_to_delete)} test users")

print("\n" + "=" * 80)
print("✅ DATABASE CLEANED FOR CLIENT DEMO")
print("=" * 80)

# Show final state
print("\n📊 FINAL DATABASE STATE:")
print(f"   Users: {db.query(User).count()}")
print(f"   Teachers: {db.query(User).filter(User.role == 'teacher').count()}")
print(f"   Students: {db.query(User).filter(User.role == 'student').count()}")
print(f"   Admins: {db.query(User).filter(User.role == 'admin').count()}")
print(f"   Enrollments: {db.query(Enrollment).count()}")
print(f"   Courses: {db.query(Course).count()}")
print(f"   Classes: {db.query(Class).count()}")

print("\n✨ System is clean and ready for client demo!")

db.close()
