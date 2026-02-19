"""Script to create a test payment for payment approval testing"""
from datetime import datetime, date
from database import SessionLocal
from models import User, Course, Teacher, TimeSlot, Enrollment, Payment, PaymentStatus, PaymentMethod, UserRole, EnrollmentStatus

def create_test_payment():
    db = SessionLocal()
    
    try:
        print("Creating test payment for payment approval testing...")
        
        # Get test data
        course = db.query(Course).first()
        teacher = db.query(Teacher).first()
        student = db.query(User).filter(User.role == UserRole.STUDENT).first()
        time_slot = db.query(TimeSlot).filter(TimeSlot.teacher_id == teacher.id).first()
        
        if not (course and teacher and student and time_slot):
            print("Missing required test data (course, teacher, student, or time_slot)")
            return
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            teacher_id=teacher.id,
            course_id=course.id,
            time_slot_id=time_slot.id,
            payment_method=PaymentMethod.AT_MASJID,
            payment_status=PaymentStatus.PENDING,
            enrollment_status=EnrollmentStatus.PENDING_TEACHER,
            start_date=date.today(),
            end_date=date.today(),
            is_active=True,
            created_at=datetime.now()
        )
        db.add(enrollment)
        db.flush()
        
        # Create payment record
        payment = Payment(
            enrollment_id=enrollment.id,
            amount=course.fee,
            payment_method=PaymentMethod.AT_MASJID,
            payment_status=PaymentStatus.PENDING,
            created_at=datetime.now()
        )
        db.add(payment)
        
        db.commit()
        
        print(f"Test payment created successfully!")
        print(f"  Enrollment ID: {enrollment.id}")
        print(f"  Payment ID: {payment.id}")
        print(f"  Student: {student.name} ({student.email})")
        print(f"  Teacher: {teacher.user.name}")
        print(f"  Course: {course.name}")
        print(f"  Amount: {payment.amount}")
        print(f"  Status: {payment.payment_status}")
        
    except Exception as e:
        print(f"Error creating test payment: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_payment()
