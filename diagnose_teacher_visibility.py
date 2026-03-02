#!/usr/bin/env python3
"""
Diagnostic script to verify why teachers don't see their enrolled students
"""
import sys
sys.path.insert(0, '/workspace')

from database import SessionLocal
from models import User, Teacher, Enrollment, Course, TimeSlot, Payment, PaymentStatus

db = SessionLocal()

print("=" * 80)
print("TEACHER VISIBILITY DIAGNOSIS")
print("=" * 80)

# 1. Check all teacher users
print("\n1. CHECKING TEACHER USERS")
print("-" * 80)
teacher_users = db.query(User).filter(User.role == 'teacher').all()
print(f"Found {len(teacher_users)} teacher users:")
for user in teacher_users:
    print(f"  - ID: {user.id}, Name: {user.name}, Email: {user.email}")

# 2. Check Teacher records
print("\n2. CHECKING TEACHER RECORDS")
print("-" * 80)
teachers = db.query(Teacher).all()
print(f"Found {len(teachers)} teacher records:")
for t in teachers:
    print(f"  ID: {t.id}, User: {t.user.name} (ID:{t.user_id}), Course: {t.course.name if t.course else 'NONE'} (ID:{t.course_id})")

# 3. Check enrollments
print("\n3. CHECKING ENROLLMENTS")
print("-" * 80)
enrollments = db.query(Enrollment).all()
print(f"Found {len(enrollments)} enrollments:")
for e in enrollments:
    student = db.query(User).filter(User.id == e.student_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == e.teacher_id).first()
    course = db.query(Course).filter(Course.id == e.course_id).first()
    
    print(f"  ID: {e.id}")
    print(f"    Student: {student.name if student else 'UNKNOWN'} (ID:{e.student_id})")
    print(f"    Course: {course.name if course else 'UNKNOWN'} (ID:{e.course_id})")
    print(f"    Teacher Record ID: {e.teacher_id}")
    if teacher:
        print(f"    Teacher User: {teacher.user.name} (ID:{teacher.user_id})")
    else:
        print(f"    Teacher Record: NOT FOUND!")
    print(f"    Time Slot ID: {e.time_slot_id}")
    print(f"    Is Active: {e.is_active}")
    print(f"    Payment Status: {e.payment_status}")
    print(f"    Enrollment Status: {e.enrollment_status}")
    print()

# 4. Check if teacher enrollment counts are correct
print("\n4. CHECKING TEACHER COURSES AND ENROLLMENT COUNTS")
print("-" * 80)
for teacher_user in teacher_users:
    teacher_records = db.query(Teacher).filter(Teacher.user_id == teacher_user.id).all()
    print(f"Teacher: {teacher_user.name} (ID:{teacher_user.id})")
    
    if not teacher_records:
        print(f"  WARNING: No Teacher records found for this user!")
        continue
    
    for tr in teacher_records:
        course = tr.course
        print(f"  Course: {course.name if course else 'UNKNOWN'} (ID:{tr.course_id})")
        
        # Count active enrollments for this course
        active_count = db.query(Enrollment).filter(
            Enrollment.course_id == tr.course_id,
            Enrollment.is_active == True
        ).count()
        print(f"    Active enrollments: {active_count}")
        
        # List all enrollments
        all_enrollments = db.query(Enrollment).filter(
            Enrollment.course_id == tr.course_id
        ).all()
        print(f"    Total enrollments: {len(all_enrollments)}")
        
        for e in all_enrollments:
            student = db.query(User).filter(User.id == e.student_id).first()
            print(f"      - {student.name if student else 'UNKNOWN'}: is_active={e.is_active}, payment={e.payment_status}")
    print()

# 5. Check time slots
print("\n5. CHECKING TIME SLOTS")
print("-" * 80)
time_slots = db.query(TimeSlot).all()
print(f"Found {len(time_slots)} time slots:")
slot_by_teacher = {}
for ts in time_slots:
    if ts.teacher_id not in slot_by_teacher:
        slot_by_teacher[ts.teacher_id] = []
    slot_by_teacher[ts.teacher_id].append(ts)

for teacher_id in sorted(slot_by_teacher.keys()):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher:
        print(f"Teacher: {teacher.user.name} (ID:{teacher.user_id})")
        print(f"  Time Slots: {len(slot_by_teacher[teacher_id])}")
        for ts in slot_by_teacher[teacher_id]:
            print(f"    - ID: {ts.id}, {ts.day_of_week} {ts.start_time} - {ts.end_time}")
    print()

# 6. Check payments
print("\n6. CHECKING PAYMENTS")
print("-" * 80)
payments = db.query(Payment).all()
print(f"Found {len(payments)} payments:")
for p in payments:
    enrollment = db.query(Enrollment).filter(Enrollment.id == p.enrollment_id).first()
    if enrollment:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        print(f"  Payment ID: {p.id}, Enrollment: {p.enrollment_id}, Student: {student.name if student else 'UNKNOWN'}")
        print(f"    Status: {p.payment_status}, Amount: {p.amount}")
    else:
        print(f"  Payment ID: {p.id}, Enrollment: {p.enrollment_id} - ENROLLMENT NOT FOUND!")
    print()

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
