from database import SessionLocal
from models import Teacher, Course, User

db = SessionLocal()

# Check if Teacher record already exists for user_id 9
existing = db.query(Teacher).filter(Teacher.user_id == 9).first()

if existing:
    # Update existing record
    if existing.course_id is None:
        existing.course_id = 1
        db.commit()
        print("✓ Teacher record updated successfully!")
        course = db.query(Course).filter(Course.id == 1).first()
        if course:
            print(f"  teacher@noori.com (ID 9) is now linked to '{course.name}' course (ID 1)")
    else:
        print(f"✓ Teacher record already linked to course ID {existing.course_id}")
else:
    # Create new record
    teacher_record = Teacher(user_id=9, course_id=1)
    db.add(teacher_record)
    db.commit()
    print("✓ Teacher record created successfully!")
    print(f"  teacher@noori.com (ID 9) is now linked to 'nazra' course (ID 1)")

db.close()
