import sys
sys.path.insert(0, '/c/Users/lenovo/Desktop/noori/backend')

from database import SessionLocal
from models import User, Enrollment, Course, TimeSlot

db = SessionLocal()

# Get a student user
student = db.query(User).filter(User.email.like("student%")).first()
if not student:
    # Try test student
    student = db.query(User).filter(User.role == "STUDENT").first()

print(f"Student: {student.email if student else 'None found'}")
if student:
    print(f"  ID: {student.id}")
    
    # Get enrollments
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()
    
    print(f"\nEnrollments: {len(enrollments)}")
    for i, e in enumerate(enrollments[:5]):  # Show first 5
        course = db.query(Course).filter(Course.id == e.course_id).first()
        time_slot = db.query(TimeSlot).filter(TimeSlot.id == e.time_slot_id).first()
        print(f"\n  Enrollment {i+1}:")
        print(f"    Course: {course.name if course else 'NONE'} (ID {e.course_id})")
        print(f"    TimeSlot: {time_slot.day if time_slot else 'NONE'} {time_slot.start_time if time_slot else ''}-{time_slot.end_time if time_slot else ''}")

db.close()
