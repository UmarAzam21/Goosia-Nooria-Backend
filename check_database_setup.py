from database import SessionLocal
from models import User, Course, Enrollment

db = SessionLocal()

print("=" * 60)
print("TEACHERS:")
print("=" * 60)
teachers = db.query(User).filter(User.role == 'teacher').all()
for t in teachers:
    print(f"  ID: {t.id}, Name: {t.name}, Email: {t.email}")

print("\n" + "=" * 60)
print("COURSES:")
print("=" * 60)
courses = db.query(Course).all()
for c in courses:
    print(f"  ID: {c.id}, Name: {c.name}")

print("\n" + "=" * 60)
print("ENROLLMENTS (Student -> Course):")
print("=" * 60)
enrollments = db.query(Enrollment).all()
for e in enrollments:
    user = db.query(User).filter(User.id == e.student_id).first()
    course = db.query(Course).filter(Course.id == e.course_id).first()
    if user and course:
        print(f"  {user.email} enrolled in {course.name}")

print("\n" + "=" * 60)
print("TEACHER RECORDS (who teaches which course):")
print("=" * 60)
from models import Teacher
teachers_courses = db.query(Teacher).all()
if teachers_courses:
    for tc in teachers_courses:
        teacher_user = db.query(User).filter(User.id == tc.user_id).first()
        course = db.query(Course).filter(Course.id == tc.course_id).first()
        if teacher_user and course:
            print(f"  {teacher_user.email} teaches {course.name}")
else:
    print("  (No Teacher records found - this is the problem!)")

db.close()
