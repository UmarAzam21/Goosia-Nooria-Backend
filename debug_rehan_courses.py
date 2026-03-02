import sys
sys.path.insert(0, '/c/Users/lenovo/Desktop/noori/backend')

from database import SessionLocal
from models import User, Teacher, Enrollment, Course, UserRole

db = SessionLocal()

# Get rehan user
rehan = db.query(User).filter(User.email == "rehan@teacher.com").first()
print(f"Rehan User: {rehan}")
if rehan:
    print(f"  ID: {rehan.id}, Role: {rehan.role}")
    
    # Get teacher profile
    teacher = db.query(Teacher).filter(Teacher.user_id == rehan.id).first()
    print(f"\nTeacher Profile: {teacher}")
    if teacher:
        print(f"  ID: {teacher.id}")
        print(f"  course_id: {teacher.course_id}")
        
        # Get enrollments where this teacher is assigned
        enrollments = db.query(Enrollment).filter(
            Enrollment.teacher_id == teacher.id
        ).all()
        print(f"\nEnrollments for teacher ID {teacher.id}: {len(enrollments)}")
        for e in enrollments:
            course = db.query(Course).filter(Course.id == e.course_id).first()
            print(f"  - Enrollment ID {e.id}: Course {course.name if course else 'NONE'} (course_id={e.course_id}), is_active={e.is_active}")
        
        # Get all enrollments with any teacher that has courses for this teacher
        all_enrollments = db.query(Enrollment).join(
            Course, Enrollment.course_id == Course.id
        ).filter(
            Enrollment.teacher_id == teacher.id,
            Enrollment.is_active == True
        ).all()
        print(f"\nActive enrollments for teacher: {len(all_enrollments)}")
        for e in all_enrollments:
            course = db.query(Course).filter(Course.id == e.course_id).first()
            print(f"  - Course {course.name if course else 'NONE'}: students enrolled")

db.close()
