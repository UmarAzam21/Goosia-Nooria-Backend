#!/usr/bin/env python3
"""Test script to verify new simple Jitsi room ID format"""
from datetime import date, timedelta, datetime, time
from database import SessionLocal
from models import User, Course, Teacher, TimeSlot, Enrollment, PaymentMethod, PaymentStatus, EnrollmentStatus, Payment, Class, ClassStatus
from google_meet_service import create_meet_event

def test_new_format():
    db = SessionLocal()
    
    try:
        print("Testing New Simplified Jitsi Room ID Format\n")
        print("=" * 60)
        
        # Get first student
        student = db.query(User).filter(User.email == "ali@student.com").first()
        if not student:
            print("❌ Student not found!")
            return
        print(f"✓ Student: {student.name}")
        
        # Get first course
        course = db.query(Course).first()
        if not course:
            print("❌ Course not found!")
            return
        print(f"✓ Course: {course.name} (ID: {course.id})")
        
        # Get first teacher
        teacher = db.query(Teacher).first()
        if not teacher:
            print("❌ Teacher not found!")
            return
        print(f"✓ Teacher: {teacher.user.name}")
        
        # Get first time slot
        time_slot = db.query(TimeSlot).first()
        if not time_slot:
            print("❌ Time slot not found!")
            return
        print(f"✓ Time Slot: {time_slot.day_of_week} {time_slot.start_time}-{time_slot.end_time}\n")
        
        # Create Jitsi meet event with simple room ID using course ID
        print("Creating Jitsi Meet Event with Course ID...")
        print("-" * 60)
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        meet_result = create_meet_event(
            event_name=course.name,
            start_time=start_time,
            end_time=end_time,
            description=f"Class: {course.name}",
            event_id=str(course.id)  # ← This creates simple room ID: noori-class-1
        )
        
        print(f"✓ Meet Event Created:")
        print(f"  - Success: {meet_result['success']}")
        print(f"  - Room ID: {meet_result.get('room_id')}")
        print(f"  - Jitsi URL: {meet_result.get('jitsi_link')}\n")
        
        if not meet_result['success']:
            print(f"❌ Failed: {meet_result.get('error')}")
            return
        
        # Create enrollment
        end_date = date.today() + timedelta(weeks=course.duration_weeks)
        
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            teacher_id=teacher.id,
            time_slot_id=time_slot.id,
            payment_method=PaymentMethod.AT_MASJID,
            start_date=date.today(),
            end_date=end_date,
            payment_status=PaymentStatus.COMPLETED,
            enrollment_status=EnrollmentStatus.APPROVED,
            jitsi_link=meet_result.get('meet_link')
        )
        
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        
        # Create classes for the enrollment
        current_date = enrollment.start_date
        for i in range(5):  # Create 5 classes
            class_obj = Class(
                enrollment_id=enrollment.id,
                class_date=current_date,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time,
                meeting_id=meet_result.get('room_id'),
                jitsi_link=meet_result.get('meet_link'),
                status=ClassStatus.SCHEDULED
            )
            db.add(class_obj)
            current_date += timedelta(days=1)
        
        db.commit()
        
        print("✓ Enrollment Created:")
        print(f"  - ID: {enrollment.id}")
        print(f"  - Student: {student.name}")
        print(f"  - Course: {course.name}")
        print(f"  - Jitsi Link: {enrollment.jitsi_link}")
        print(f"  - Status: {enrollment.enrollment_status}")
        print(f"  - Payment: {enrollment.payment_status}")
        print( f"\n✅ SUCCESS! Jitsi link is now in simple format: {enrollment.jitsi_link}")
        print("\n" + "=" * 60)
        print(f"Test the URL: {enrollment.jitsi_link}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_new_format()
