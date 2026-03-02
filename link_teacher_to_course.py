#!/usr/bin/env python
"""Script to link a teacher user to their courses"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Course, Teacher, UserRole

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # Get all teacher users
    teachers = db.query(User).filter(User.role == UserRole.TEACHER).all()
    
    print(f"Found {len(teachers)} teacher(s)")
    
    for teacher in teachers:
        print(f"\nTeacher: {teacher.name} ({teacher.email})")
        
        # Get all courses
        courses = db.query(Course).filter(Course.is_active == True).all()
        print(f"Available courses: {len(courses)}")
        
        for i, course in enumerate(courses, 1):
            print(f"  {i}. {course.name}")
        
        # Check if teacher already has courses
        existing_teachers = db.query(Teacher).filter(Teacher.user_id == teacher.id).all()
        print(f"Current courses for this teacher: {len(existing_teachers)}")
        
        if existing_teachers:
            for t in existing_teachers:
                if t.course:
                    print(f"  - {t.course.name}")
        
        # Ask user to link courses
        print(f"\nEnter course IDs to link to {teacher.name} (comma-separated, or 'skip'):")
        user_input = input("> ").strip()
        
        if user_input.lower() != 'skip':
            course_ids = [int(x.strip()) for x in user_input.split(',') if x.strip()]
            
            for course_id in course_ids:
                # Check if teacher already linked to this course
                existing = db.query(Teacher).filter(
                    Teacher.user_id == teacher.id,
                    Teacher.course_id == course_id
                ).first()
                
                if existing:
                    print(f"  Teacher already linked to course {course_id}")
                else:
                    new_teacher = Teacher(
                        user_id=teacher.id,
                        course_id=course_id,
                        is_available=True
                    )
                    db.add(new_teacher)
                    print(f"  ✓ Linked to course {course_id}")
            
            db.commit()
            print("\nChanges saved!")
    
finally:
    db.close()
