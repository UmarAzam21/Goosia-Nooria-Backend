#!/usr/bin/env python3
"""Test script to create an enrollment and verify jitsi_link is populated"""
from datetime import date, timedelta
from database import SessionLocal
from models import User, Course, Teacher, TimeSlot, Enrollment, PaymentMethod, PaymentStatus, EnrollmentStatus
from google_meet_service import create_meet_event

def test_enrollment_with_jitsi():
    db = SessionLocal()
    
    try:
        print("Testing Jitsi enrollment creation...\n")
        
        # Get first student
        student = db.query(User).filter(User.email == "ali@student.com").first()
        if not student:
            print("❌ Student not found!")
            return
        print(f"✓ Found student: {student.name}")
        
        # Get first course
        course = db.query(Course).first()
        if not course:
            print("❌ Course not found!")
            return
        print(f"✓ Found course: {course.name}")
        
        # Get first teacher
        teacher = db.query(Teacher).first()
        if not teacher:
            print("❌ Teacher not found!")
            return
        print(f"✓ Found teacher: {teacher.user.name}")
        
        # Get first time slot
        time_slot = db.query(TimeSlot).first()
        if not time_slot:
            print("❌ Time slot not found!")
            return
        print(f"✓ Found time slot: {time_slot.day_of_week} {time_slot.start_time}-{time_slot.end_time}")
        
        # Test Jitsi meet event creation
        event_name = f"{course.name} - {student.name}"
        print(f"\n📅 Creating Jitsi meet event: {event_name}")
        
        from datetime import datetime, timedelta
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        meet_result = create_meet_event(
            event_name=event_name,
            start_time=start_time,
            end_time=end_time,
            description=f"Test class for {course.name}"
        )
        
        print(f"✓ Jitsi event created:")
        print(f"   - Success: {meet_result['success']}")
        print(f"   - Meet Link: {meet_result.get('meet_link')}")
        print(f"   - Room ID: {meet_result.get('room_id')}")
        print(f"   - Jitsi Link: {meet_result.get('jitsi_link')}")
        
        if not meet_result['success']:
            print(f"❌ Failed to create meet event: {meet_result.get('error')}")
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
        
        print(f"\n✓ Enrollment created:")
        print(f"   - ID: {enrollment.id}")
        print(f"   - Student: {student.name}")
        print(f"   - Course: {course.name}")
        print(f"   - Jitsi Link: {enrollment.jitsi_link}")
        print(f"   - Status: {enrollment.enrollment_status}")
        print(f"   - Payment: {enrollment.payment_status}")
        
        if not enrollment.jitsi_link:
            print("❌ WARNING: jitsi_link is empty!")
        else:
            print(f"✅ Jitsi link is properly set!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_enrollment_with_jitsi()
